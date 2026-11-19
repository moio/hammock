#!/usr/bin/env python3
"""Compare license files against canonical SPDX license text.

Deterministic helper for the `license` skill. Uses only the Python standard
library so it runs in any harness.

Modes:
  compare (default)  Check one or more license files against a known SPDX ID.
  identify           Guess the SPDX ID of a license file by scoring it against
                     candidate licenses from the SPDX license list.

Network: SPDX texts are fetched from raw.githubusercontent.com (same source the
skill uses). For offline use, pass --spdx-text with a local canonical file.

Exit codes: 0 = all files match (compare) / candidates found (identify),
1 = mismatch or no confident match, 2 = usage/network/parse error.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

SPDX_TEXT_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/text/{id}.txt"
SPDX_LIST_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"

LICENSE_PATTERNS = ["LICENSE*", "LICENCE*", "COPYING*", "COPYRIGHT*"]

# Lines stripped from both sides of the comparison. Must look like an actual
# copyright notice — a bare "line starts with 'copyright'" rule would eat
# legitimate term lines like "The above copyright notice and this permission
# notice shall be included..." when hard-wrapped texts happen to break there.
# We therefore require a (c)/© marker, a <year placeholder, or a 4-digit year.
COPYRIGHT_LINE = re.compile(
    r"^\s*(?=.*(\(c\)|\u00a9|<year|\[\s*yyyy|\d{4}))(?:Copyright\b|\u00a9)",
    re.IGNORECASE,
)


def find_license_files(root: Path) -> list[Path]:
    """Find license-ish files at the repo root (not recursive)."""
    found: set[Path] = set()
    for pattern in LICENSE_PATTERNS:
        found.update(p for p in root.glob(pattern) if p.is_file())
    return sorted(found)


def normalize(text: str) -> list[str]:
    """Normalize license text into comparable word tokens.

    Tolerates formatting-only drift so that real term changes stand out:
    - Unicode normalization + typographic quotes/dashes folded to ASCII
    - copyright lines removed
    - whitespace split (hard-wrapping and reflowing are not findings)
    """
    text = unicodedata.normalize("NFKC", text)
    for a, b in (("\u2018", "'"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'),
                 ("\u2013", "-"), ("\u2014", "-")):
        text = text.replace(a, b)
    words: list[str] = []
    for line in text.splitlines():
        if COPYRIGHT_LINE.match(line):
            continue
        words.extend(line.split())
    return words


def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "license-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def fetch_spdx_text(spdx_id: str) -> str:
    try:
        return fetch_url(SPDX_TEXT_URL.format(id=spdx_id))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise SystemExit(
                f"error: SPDX has no license '{spdx_id}' (404). "
                "Check the identifier — see https://spdx.org/licenses/"
            ) from None
        raise


def word_diff(a: list[str], b: list[str]) -> list[str]:
    """Word-level diff rendered as compact +line/-line chunks."""
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a_words, b_words = a[i1:i2], b[j1:j2]
        context = " ".join(a[max(0, i1 - 4):i1][-4:])
        out.append(f"  context: ...{context}")
        if a_words:
            out.append(f"  - {' '.join(a_words)}")
        if b_words:
            out.append(f"  + {' '.join(b_words)}")
    return out


def score(candidate_text: str, target_words: list[str]) -> float:
    return difflib.SequenceMatcher(
        a=normalize(candidate_text), b=target_words, autojunk=False
    ).ratio()


def identify(license_path: Path, top: int) -> list[tuple[str, float]]:
    """Score the file against plausible SPDX candidates.

    Strategy: the full SPDX list is ~600 licenses — fetching every text is not
    reasonable. Shortlist candidates by name/keyword overlap with the file's
    own distinctive words (e.g. 'Apache', 'Affero', 'Artistic'), then fetch
    and score only the shortlist.
    """
    target_words = normalize(license_path.read_text(encoding="utf-8", errors="replace"))
    listing = json.loads(fetch_url(SPDX_LIST_URL))
    licenses = listing.get("licenses", [])

    # Distinctive tokens from the file itself. No length filter — short tokens
    # like 'mit' (from 'MIT License') are the strongest signal we have.
    target_tokens = {w.lower().strip(".,;:()\"") for w in target_words}

    def shortlist_key(lic: dict) -> float:
        name = lic.get("name", "")
        lic_id = lic.get("licenseId", "")
        keywords = {t.lower() for t in re.split(r"[^A-Za-z0-9]+", name + " " + lic_id)}
        keywords.discard("")
        overlap = float(len(target_tokens & keywords))
        # If the ID itself appears verbatim in the file text, that's a strong
        # signal — make sure such licenses get fetched and scored.
        if lic_id.lower() in target_tokens:
            overlap += 5.0
        return overlap

    candidates = sorted(licenses, key=shortlist_key, reverse=True)
    results: list[tuple[str, float]] = []
    for lic in candidates[:top]:
        cand_id = lic["licenseId"]
        try:
            text = fetch_spdx_text(cand_id)
        except (SystemExit, urllib.error.URLError):
            continue
        results.append((cand_id, score(text, target_words)))
    results.sort(key=lambda pair: pair[1], reverse=True)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)

    p_cmp = sub.add_parser("compare", help="compare license file(s) against an SPDX ID")
    p_cmp.add_argument("files", nargs="+", type=Path, help="license files to check")
    p_cmp.add_argument("--spdx-id", required=True, help="SPDX identifier, e.g. MIT")
    p_cmp.add_argument("--spdx-text", type=Path, default=None,
                       help="use this local canonical text instead of fetching")

    p_id = sub.add_parser("identify", help="guess the SPDX ID of a license file")
    p_id.add_argument("file", type=Path, help="license file")
    p_id.add_argument("--top", type=int, default=8, help="candidates to score (default 8)")

    args = parser.parse_args()

    if args.mode == "identify":
        results = identify(args.file, args.top)
        for lic_id, ratio in results:
            print(f"{ratio:6.1%}  {lic_id}")
        best_id, best = results[0] if results else ("", 0.0)
        if best < 0.95:
            print(f"\nNo confident match (best {best_id} at {best:.1%}). "
                  "Treat as unidentifiable; report closest candidates.", file=sys.stderr)
            return 1
        print(f"\nBest match: {best_id} ({best:.1%})")
        return 0

    canonical = (args.spdx_text.read_text(encoding="utf-8")
                 if args.spdx_text else fetch_spdx_text(args.spdx_id))
    canon_words = normalize(canonical)

    any_mismatch = False
    for path in args.files:
        if not path.exists():
            print(f"{path}: NOT FOUND")
            any_mismatch = True
            continue
        words = normalize(path.read_text(encoding="utf-8", errors="replace"))
        if words == canon_words:
            print(f"{path}: OK — terms match SPDX {args.spdx_id}")
            continue
        any_mismatch = True
        print(f"{path}: MISMATCH vs SPDX {args.spdx_id}")
        diffs = word_diff(canon_words, words)
        if diffs:
            print("  (word-level differences; whitespace/wrapping ignored)")
            print("\n".join(diffs))
        else:
            print("  word sequences identical; only copyright lines / "
                  "formatting differ — check attribution separately")

    return 1 if any_mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
