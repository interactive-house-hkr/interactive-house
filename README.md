# Interactive House

Course project (DA330B, VT26): an Interactive/Smart House system with **Devices (simulation)**, a **Server + Database (DB)**, and **Units (clients)** (e.g., mobile + computer).  


> This README is intentionally short for now. We’ll expand it as the project evolves.

## Repository structure (initial)
Planned high-level layout (may change):
- `apps/` — Units (mobile/web)
- `services/` — Server/API + DB assets (migrations, seeds, etc.)
- `devices/` — Device simulation(s)
- `shared/` — Shared contracts/utilities (API DTOs, schemas, etc.)
- `docs/` — Project documentation

The Free group can create a separate folder depending on what we choose to build in the “free” part (e.g., voice-to-action, more simulated devices, etc.). If it fits better, they can also place their work inside an existing folder (e.g., `apps/`).

## Project board
We use **GitHub Projects** for planning and tracking:
- Items are tagged with **Area**, **Iteration**, **Work type**, and **Priority**.
- The person doing the work should **self-assign** the issue when starting.

## How we work
- Work happens in **branches** and gets merged via **Pull Requests** into `main`.
- Minimum **1 review** is required before merge.
- See **[CONTRIBUTING.md](CONTRIBUTING.md)** for the step-by-step workflow.

## Timeline (May change)

```mermaid
gantt
title Interactive House – Project Timeline
dateFormat  YYYY-MM-DD

section Phases
Inception        :2026-01-21, 2026-02-12
Elaboration      :2026-02-13, 2026-03-20
Construction     :2026-03-21, 2026-05-12
Transition       :2026-05-13, 2026-05-26

section Iterations (timeboxes)
Iteration 0 (to PM1)        :2026-01-21, 2026-02-12
Iteration 1 (to PM2)        :2026-02-13, 2026-03-05
Iteration 2 (to PM3)        :2026-03-06, 2026-03-20
Iteration 3 (to Midterm)    :2026-03-21, 2026-04-07
Iteration 4 (to PM4)        :2026-04-08, 2026-04-28
Iteration 5 (to PM5)        :2026-04-29, 2026-05-12
Iteration 6 (to Final)      :2026-05-13, 2026-05-26

section Gates (milestones)
PM1                :milestone, 2026-02-12, 1d
PM2                :milestone, 2026-03-05, 1d
PM3                :milestone, 2026-03-20, 1d
Midterm            :milestone, 2026-04-07, 1d
PM4                :milestone, 2026-04-28, 1d
PM5                :milestone, 2026-05-12, 1d
Final              :milestone, 2026-05-26, 1d
```
