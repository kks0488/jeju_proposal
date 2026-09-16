# Project working instructions

<!-- REVIEWED_GITHUB_SYNC_20260916 -->
## Local workspace and reviewed GitHub updates

This repository is worked on under `~/projects/jeju_proposal`. The default branch is `master`.

The user authorized publishing completed, requested project updates to this repository. Preserve all earlier instructions and existing evidence/data. This authorization is not permission to add unrelated content, publish credentials, change repository visibility, or launch local servers.

Before editing, inspect `git status`, fetch `origin`, and read the latest branch/commit and relevant project guidance. With a clean working tree, `git pull --ff-only origin master` incorporates upstream changes. If there is existing work or divergent history, preserve both sides and reconcile deliberately; never use `reset --hard`, automatic stashing, or force push to resolve it.

After completing a requested update, run the relevant project checks, inspect the diff, stage only the reviewed files for that task, and make a meaningful commit. Do not blanket-stage the repository or commit unfinished work solely to trigger a sync.

On the owner's configured PC, a local `post-commit` hook attempts a normal push of reviewed commits to this repository's `master` branch. It checks the expected destination/branch, upstream divergence, and common credential/runtime paths and token signatures. These checks are an extra guard, not an exhaustive secret or privacy audit. Review the actual content before committing, especially for public repositories.

The hook does not auto-stage, auto-commit, or upload mere file saves. A failed push leaves the local commit intact and reports `NOT SYNCED`; never call an update synchronized until GitHub's branch commit has been verified. For a retry after deliberate reconciliation, run `~/.local/bin/project-github-sync jeju_proposal publish`. Use `prepare` before new work on a clean tree, and `status` to inspect the last recorded result.

Hooks are local to this clone, not carried by a Git clone. In other environments, perform the same reviewed workflow and a normal explicit push. Do not assume background bidirectional synchronization. Repository visibility stays unchanged. Temporarily opt out on this clone with `git config project.autopushEnabled false`; re-enable with `true` only when publishing is intended.
<!-- END_REVIEWED_GITHUB_SYNC_20260916 -->
