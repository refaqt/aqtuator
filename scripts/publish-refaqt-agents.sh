#!/usr/bin/env bash
# Publish the vendored .agents/ tree to refaqt/refaqt-agents and optionally
# convert this repo's .agents directory into a git submodule.
#
# Usage (from aqtuator root, with write access to both remotes):
#   bash scripts/publish-refaqt-agents.sh
#   bash scripts/publish-refaqt-agents.sh --convert-submodule
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KIT_REMOTE="${KIT_REMOTE:-https://github.com/refaqt/refaqt-agents.git}"
BRANCH="${KIT_BRANCH:-cursor/kit-populate-37ab}"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

echo "Cloning $KIT_REMOTE ..."
git clone "$KIT_REMOTE" "$WORKDIR/kit"
cd "$WORKDIR/kit"
git checkout -B "$BRANCH" origin/main 2>/dev/null || git checkout -B "$BRANCH"

rsync -a --delete \
  --exclude '.git' \
  --exclude '.gitattributes' \
  "$ROOT/.agents/" "$WORKDIR/kit/"

git add -A
if git diff --cached --quiet; then
  echo "No kit changes to publish."
else
  git -c user.email="${GIT_AUTHOR_EMAIL:-cursoragent@cursor.com}" \
      -c user.name="${GIT_AUTHOR_NAME:-Cursor Agent}" \
      commit -m "feat(kit): sync portable rules, skills, templates, and bootstrap"
  git push -u origin "$BRANCH"
  echo "Pushed $BRANCH to $KIT_REMOTE"
fi

if [[ "${1:-}" == "--convert-submodule" ]]; then
  SHA="$(git rev-parse HEAD)"
  cd "$ROOT"
  git rm -rf .agents
  git submodule add "$KIT_REMOTE" .agents
  git -C .agents checkout "$SHA"
  git add .gitmodules .agents
  echo "Converted .agents/ to submodule at $SHA"
  echo "Commit this change in aqtuator when ready."
fi
