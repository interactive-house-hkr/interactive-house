# Contributing / Workflow (Interactive House)

This guide shows how to go from picking a task/issue to getting your code merged into `main`.

## Quick rules
- **Never commit directly to `main`.** Work in a **branch**.
- All changes go to `main` via a **Pull Request (PR)**.
- At least **1 approval** is required before merge (and any required checks must be green).
- Every PR should be linked to an **Issue** (traceability).
- Update the **Project board** status manually (Todo → In progress → In review → Done) unless we decide otherwise.

---

## 1) Pick an issue/task
1. Go to **GitHub Projects** (or the repo **Issues** list).
2. Pick an issue in **Todo** that isn’t taken, or ask in Discord before taking it.
3. **Assign yourself** to the issue and set the Project status to **In progress**.

Tip: If the issue is unclear, comment on it before you start coding.

---

## 2) Create a branch

### Branch naming convention
Use:

`<area>/<issueNumber>-short-description`

Examples:
- `server/123-add-health-endpoint`
- `units/88-light-toggle-ui`
- `device/45-simulate-temperature`
- `free/210-voice-to-action`
- `docs/12-update-readme`

Areas we use: `server`, `units`, `device`, `db`, `free`, `docs`, `integration`.

### Option A: Create a branch in GitHub (easy)
1. Open the Issue on GitHub.
2. If you see **Create a branch**, click it.
3. GitHub creates the branch and links it to the Issue.

### Option B: Create a branch in a terminal (common)
Open a terminal (Git Bash or PowerShell) in your repo folder.

1. Make sure `main` is up to date:
```bash
git checkout main
git pull
```

2. Create and switch to a new branch:
```bash
git checkout -b server/123-add-health-endpoint
```

---

## 3) Code locally
- Make your changes in the correct folders.
- Run relevant build/tests if available.

---

## 4) Stage and commit your changes
1. Check what changed:
```bash
git status
```

2. Stage files:
```bash
git add .
```
(or stage specific files: `git add path/to/file`)

3. Commit:
```bash
git commit -m "Add health endpoint"
```

Tip: Keep commit messages short and descriptive.

---

## 5) Push your branch to GitHub
First push (new branch):
```bash
git push -u origin server/123-add-health-endpoint
```

After that:
```bash
git push
```

---

## 6) Open a Pull Request (PR)
After pushing, create a PR using either method:

### Option A: The quick banner (recommended)
GitHub often shows:
> “Branch <name> had recent pushes — Compare & pull request”

1. Click **Compare & pull request**
2. Verify:
   - **base**: `main`
   - **compare**: your branch
3. Write a clear title + description.

### Option B: The “manual” way
1. Repo → **Pull requests** → **New pull request**
2. base = `main`, compare = your branch
3. Create PR.

### Link the PR to the Issue (important)
In the PR description, include one of these:
- `Closes #123` (auto-closes the issue when merged), or
- `Relates to #123` (if it shouldn’t auto-close)

---

## 7) Not finished yet? Use Draft PR / WIP
If you want early feedback but you’re not done:
- Mark the PR as **Draft**, or
- Put **[WIP]** in the PR title.

Don’t merge Draft/WIP PRs.

---

## 8) Reviews: who merges?
**Default rule:** The PR author merges their own PR **after**:
- At least **1 approval**
- All review comments are addressed / resolved
- Required checks (CI) are green

If you’re unsure, ask in the PR comments: “Ready to merge?”

---

## 9) Apply review feedback
If you get requested changes:

1. Update code locally
2. Commit and push again:
```bash
git add .
git commit -m "Address review feedback"
git push
```

The PR updates automatically.

---

## 10) Merge the PR
When approved and ready:

1. Click **Merge** on GitHub (**Squash and merge**)
2. Make sure the linked Issue closes (if you used `Closes #...`)
3. Click **Delete branch** (recommended) after merge

---

## 11) Sync your local `main` after merge
```bash
git checkout main
git pull
```

(Optional) delete the local branch:
```bash
git branch -d server/123-add-health-endpoint
```

---

## Common problems

### “I can’t push”
If it’s your first push for the branch, you may need upstream:
```bash
git push -u origin <your-branch>
```

### “My PR has merge conflicts”
1. Update `main`:
```bash
git checkout main
git pull
```

2. Merge `main` into your branch:
```bash
git checkout <your-branch>
git merge main
```

3. Resolve conflicts, then:
```bash
git add .
git commit -m "Resolve merge conflicts"
git push
```

### “I created a branch on GitHub but can’t see it locally”
Branches created on GitHub are **remote-only** until you fetch and check them out.

1. Fetch all remotes:
```bash
git fetch --all
```

2. Create a local tracking branch:
```bash
git switch <branch>
```
(or `git checkout <branch>`)

Tip: `git branch -r` lists remote branches. `git branch` shows only local branches.

---

## PR checklist (before marking Ready for review)
- [ ] PR is linked to an Issue (`Closes #...` or `Relates to #...`)
- [ ] Changes are focused (not 10 unrelated things)
- [ ] Only relevant files are changed (check the high-level structure in README to avoid touching other areas by mistake)
- [ ] Build/run works locally (if applicable)
- [ ] No unfinished TODOs (unless intentional and tracked)
- [ ] Project status updated (In progress / In review / Done)