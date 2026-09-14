# Spec Kit Execution & Automation Guide

This guide explains the complete directory structure and how to run Spec Kit commands for the current and future features on **Anshita Makeover**.

---

## 1. Directory Structure

Your project now follows the official Spec-Driven Development (SDD) standard:

```
.specify/
├── memory/
│   └── constitution.md              <-- Foundational rules, architectural mandates, aesthetic principles
├── specs/
│   └── SPEC-001-vector-curtain-entrance.md <-- Feature requirements, user stories, acceptance criteria
├── plans/
│   └── PLAN-001-vector-curtain-entrance.md <-- Architecture, DOM design, timing sequences
└── tasks/
    └── TASKS-001-vector-curtain-entrance.md <-- Granular tasks (TSK-01 through TSK-08)
```

---

## 2. The 5 Spec Kit Workflow Phases & Commands

In Spec-Driven Development, every feature moves through 5 systematic phases:

```
┌───────────────────────────┐
│ 1. CONSTITUTION           │  Establish core laws, non-negotiables, aesthetics
│    /speckit.constitution  │  File: .specify/memory/constitution.md
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 2. SPECIFY                │  Define requirements, user stories, what we build
│    /speckit.specify       │  File: .specify/specs/SPEC-###.md
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 3. PLAN                   │  Technical blueprint, files touched, architecture
│    /speckit.plan          │  File: .specify/plans/PLAN-###.md
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 4. TASKS                  │  Granular work breakdown, dependencies, checklists
│    /speckit.tasks         │  File: .specify/tasks/TASKS-###.md
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 5. IMPLEMENT              │  Code execution, tests, browser verification
│    /speckit.implement     │  Execute TSK-01 -> TSK-08 in sequence
└───────────────────────────┘
```

---

## 3. How to Execute Remaining Spec Kit Tasks

To execute the current feature (`SPEC-001: Vector Entrance & Dual Curtain System`), the tasks are executed step-by-step:

### Step 1: Execute TSK-01 (Vector Monogram SVG)
Create the bespoke SVG vector monogram at:
`anshita_project/core/static/core/images/brand/anshita_crest.svg`
with interlocking calligraphy "AM" crest and gold gradient paths.

### Step 2: Execute TSK-02 & TSK-03 (CSS Physics & Stroke Animation)
Add the curtain split styles and `@keyframes` stroke animation to:
`anshita_project/core/static/core/css/style.css`

### Step 3: Execute TSK-04 & TSK-05 (DOM Refactor & Session Guard)
Purge the `<video>` element from `anshita_project/core/templates/core/base.html` and install the dual curtains (`.curtain-left`, `.curtain-right`) with zero-flicker `<head>` session guard.

### Step 4: Execute TSK-06 & TSK-07 (Micro-Interactions & WebGL Sync)
Implement the `Escape` key / click bypass listener and link curtain parting to the Three.js canvas wave burst.

### Step 5: Execute TSK-08 (Browser Subagent Verification)
Launch a browser subagent to test the live animation at `http://127.0.0.1:8000/`, capture visual recording, and verify session persistence when navigating.

---

## 4. How to Use Spec Kit for Future Features

When you want to build any future feature (e.g., WhatsApp booking automation, Instagram live reel sync, pricing calculator):

1. **To Define Feature**:
   Tell the assistant: *"Create specification for [Feature Name]"* (or type `/speckit.specify [Feature Name]`).
   This will generate `.specify/specs/SPEC-002-[feature].md`.

2. **To Create Blueprint**:
   Tell the assistant: *"Create technical plan for SPEC-002"* (or type `/speckit.plan`).
   This will generate `.specify/plans/PLAN-002-[feature].md`.

3. **To Break into Tasks**:
   Tell the assistant: *"Generate task list for PLAN-002"* (or type `/speckit.tasks`).
   This will generate `.specify/tasks/TASKS-002-[feature].md`.

4. **To Execute Code**:
   Tell the assistant: *"Implement tasks TSK-01 to TSK-N"* (or type `/speckit.implement`).
