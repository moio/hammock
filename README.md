# Hammock

A set of agent skills, tools, and harnesses that take repetitive maintenance work off the open source maintainer's plate.

Started in [HackWeek 26](https://hackweek.opensuse.org/26/projects/project-hammock-llm-powered-oss-maintenance).

## Why

Much of what open source maintainers do is routine: keep dependencies current, review and merge low-risk PRs, cut releases, keep docs and tests from rotting. This work is important but often crowds out the work that actually needs a human. Each of these tasks is well-defined, has clear success criteria, and is verifiable — which makes them good candidates for delegation to coding agents.

Hammock aims to make that delegation practical and safe, so maintainers stay in the loop where it matters and stop being the bottleneck where it doesn't.

## Approach

Hammock is built as **agent skills and tools** rather than a monolithic CI bot:

- Skills are portable instructions that work with all agent harnesses, maintainers can run them locally or in automation.
- Tools and harnesses provide the plumbing and automation hooks.

## Status

Early — started at HackWeek 26. Expect the structure and scope to change. See [openSUSE HackWeek 26 project page](https://hackweek.opensuse.org/26/projects/project-hammock-llm-powered-oss-maintenance) for the current plan.
