# 🤖 ITR-TaxPilot — Milestone & Task Execution Prompt

> This is the master execution prompt and protocol for AI coding agents (and developers) working on **ITR-TaxPilot**.  
> Every milestone and task implementation must strictly adhere to the instructions defined in this file.

---

## 🎯 Purpose

This document provides a strict, standardized execution workflow for picking up any milestone/task from [`milestones/`](file:///D:/Projects/ITR-TaxPilot/milestones), creating dedicated Git branches from `main`, implementing code deterministically, validating tests, and keeping the [`DASHBOARD.md`](file:///D:/Projects/ITR-TaxPilot/DASHBOARD.md) updated.

---

## 📋 The 6-Step Execution Protocol

Whenever you are instructed to execute a Milestone or Task, execute these steps in order:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. Git Branching (Create milestone branch from main)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Context Intake (Read README.md, milestone & task specs)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Implementation (Deterministic code, schemas, services)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Verification & Testing (Pytest, linting, security audit) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Update Status (Task file, Milestone README, DASHBOARD.md)│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Commit & Merge (Merge verified milestone branch to main) │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 1: Git Branch Creation & Switching

1. Ensure the workspace is clean and on the latest `main` branch:
   ```bash
   git checkout main
   ```
2. Create and switch to the designated branch for the milestone:
   - Branch naming format: `milestone/<milestone-folder-name>`
   - Examples:
     - `milestone/m01-project-setup`
     - `milestone/m02-backend-core`
     - `milestone/m06-assessment-year-rules`
     - `milestone/m07-deterministic-tax-engine`
   ```bash
   git checkout -b milestone/<milestone-folder-name> main
   ```
3. Update [`DASHBOARD.md`](file:///D:/Projects/ITR-TaxPilot/DASHBOARD.md):
   - Set **Current Active Branch** to `milestone/<milestone-folder-name>`.
   - Set the Milestone's status in the table to 🟡 `In Progress`.

---

### Step 2: Context & Specification Intake

1. Read the core design guidelines and constraints in [`README.md`](file:///D:/Projects/ITR-TaxPilot/README.md).
2. Open and review the target milestone directory:
   - [`milestones/<milestone-folder>/README.md`](file:///D:/Projects/ITR-TaxPilot/milestones)
3. Open and review the specific task file:
   - `milestones/<milestone-folder>/<task-file>.md`
4. Verify all prerequisites and dependencies from earlier milestones are in place before writing code.

---

### Step 3: Implementation Rules & Constraints

Follow the **10 Core Rules** from Section 12 of [`README.md`](file:///D:/Projects/ITR-TaxPilot/README.md):

1. **AI does NOT own the tax calculation:** All tax calculations must be deterministic Python functions driven by versioned rules under `app/tax/rules/`.
2. **AI Provider Abstraction:** Never couple code to a specific LLM. Use `AIProvider` base classes (`ClaudeProvider`, `GeminiProvider`).
3. **Data Normalization:** Distinguish `0` from `unknown/not found`. Never guess missing tax values.
4. **Zero PII Logging:** Never log PAN, Aadhaar, names, salaries, or raw Form 16 text in logs or error traces.
5. **No Unnecessary Complexity:** Avoid unneeded microservices, vector DBs, or autonomous agent loops.
6. **Code Cleanliness:** Maintain clean separation between API routes, schemas, database models, document processors, tax rules, and AI services.

---

### Step 4: Verification & Testing

Every task MUST be tested before being marked as complete:

1. **Run Unit & Integration Tests:**
   ```bash
   pytest -v
   ```
2. **Run Linting & Formatting:**
   ```bash
   ruff check .
   black --check .
   ```
3. **Verify Boundary Conditions:**
   - Test slab transitions, Section 87A rebate edges, Standard Deduction limits, and 4% cess.
4. **Verify Container Build (when applicable):**
   ```bash
   docker compose up --build -d
   ```

---

### Step 5: Status Tracking & Dashboard Update

After implementation and testing pass:

1. **Update the individual task markdown file:**
   - Change `**Status:** 'Not Started'` to `**Status:** 'Completed'`.
   - Mark all acceptance criteria checkboxes as checked `[x]`.
2. **Update the milestone `README.md`:**
   - Mark the completed task item with `[x]` and `Status: Completed`.
   - If all tasks in the milestone are done, update **Overall Milestone Status** to `Completed`.
3. **Update [`DASHBOARD.md`](file:///D:/Projects/ITR-TaxPilot/DASHBOARD.md):**
   - Increment the completed task count.
   - Update the progress bar percentage calculation:
     $$\text{Progress \%} = \left(\frac{\text{Completed Milestones}}{18}\right) \times 100$$
   - Update the milestone row status in the table:
     - ⚪ `Pending` → 🟡 `In Progress` → 🟢 `Completed`
   - Update the **Last Updated** timestamp.

---

### Step 6: Git Commit & Merge Protocol

1. Stage and commit changes on the milestone branch using conventional commit format:
   ```bash
   git add .
   git commit -m "feat(m01): implement project setup and baseline health check"
   ```
2. Once the entire milestone is verified and all its tasks are completed:
   - Switch back to `main`:
     ```bash
     git checkout main
     ```
   - Merge the milestone branch into `main`:
     ```bash
     git merge --no-ff milestone/<milestone-folder-name> -m "chore: merge milestone/<milestone-folder-name> into main"
     ```
   - Update [`DASHBOARD.md`](file:///D:/Projects/ITR-TaxPilot/DASHBOARD.md) setting **Current Active Branch** back to `main` and marking the milestone as 🟢 `Completed`.

---

## ⚡ Quick Command Template for AI Coding Agents

When invoked by the user with:  
> *"Execute Milestone X"* or *"Run Task Y from Milestone X"*

**Run this prompt workflow:**

```markdown
1. Checkout from main: `git checkout -b milestone/mXX-<name> main`
2. Read `milestones/milestoneXX-<name>/<task>.md` and `README.md`.
3. Implement required code and tests.
4. Run `pytest` and verify 100% pass rate.
5. Update task file, milestone README.md, and `DASHBOARD.md`.
6. Commit changes to `milestone/mXX-<name>`.
7. If milestone complete, merge to `main` and mark completed in `DASHBOARD.md`.
```

---

*Governed by ITR-TaxPilot Engineering Blueprint ([`README.md`](file:///D:/Projects/ITR-TaxPilot/README.md)).*
