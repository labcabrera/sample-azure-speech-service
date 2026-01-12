#!/usr/bin/env bash
set -euo pipefail

# Make script executable by default for repository consumers (chmod required locally)

usage() {
  echo "Usage: $0 <tag>"
  echo "Example: $0 v1.2.3"
  exit 1
}

if [ "$#" -ne 1 ]; then
  usage
fi

TAG="$1"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required but not installed." >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --staged --quiet; then
  echo "Working tree is dirty. Commit or stash changes before creating a release." >&2
  git status --porcelain
  exit 1
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# git-flow usually expects releases to be started from 'develop'
if [ "$CURRENT_BRANCH" != "develop" ]; then
  echo "Warning: current branch is '$CURRENT_BRANCH'. git-flow release is normally started from 'develop'."
  read -p "Continue anyway? [y/N] " yn
  case "$yn" in
    [Yy]*) ;;
    *) echo "Aborting."; exit 1;;
  esac
fi

echo "Starting git-flow release '$TAG'..."

if command -v git-flow >/dev/null 2>&1; then
  GITFLOW_CMD="git flow"
else
  GITFLOW_CMD="git flow" # try git flow as subcommand
fi

# Start release
echo "Running: git flow release start $TAG"
if ! $GITFLOW_CMD release start "$TAG"; then
  echo "Failed to start git-flow release." >&2
  exit 1
fi

echo "Finishing release '$TAG'..."
# Finish release (this will tag and merge into master and develop)
if ! $GITFLOW_CMD release finish -m "Release $TAG" "$TAG"; then
  echo "Failed to finish git-flow release." >&2
  echo "You may need to finish the release manually: git flow release finish $TAG" >&2
  exit 1
fi

echo "Pushing branches and tags to origin..."
# Push master and develop and tags
git push origin master
git push origin develop
git push --tags

echo "Release $TAG created and pushed successfully."
