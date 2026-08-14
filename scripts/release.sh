#!/usr/bin/env bash
set -euo pipefail

# Release edify-cli + the edify plugin as one version: bump plugin.json (the
# source of truth), sync pyproject.toml to match, commit, tag, push, publish
# to PyPI, create the GitHub release, and bump the plugin's entry in the
# marketplace repo. Each external step probes what already landed before
# acting, so a release that dies partway can always be completed with
# `--resume` instead of redone by hand.
#
# Usage:
#   release.sh [patch|minor|major]   full release (defaults to patch)
#   release.sh --resume              complete a release that landed partially
#
# Run from the repo root; `just release` / `just resume-release` do that for
# you. Requires bash, jq, git, gh, uv, curl, and MARKETPLACE_DIR pointing at
# the claude-plugins repo.
#
# plugin.json is the version source of truth — the PyPI package is a support
# artifact published alongside it, not the driver. This mirrors
# claude-plugin-dev's release.sh (github + marketplace steps ported near
# verbatim) with a PyPI step spliced in; edify is the only PyPI-shaped
# consumer so far, so this stays a local copy rather than a toolkit feature.

unset CDPATH
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

manifest="plugin/.claude-plugin/plugin.json"
pypi_name="edify-cli"

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
note() { printf '%s\n' "$*"; }

mode="release"
bump="patch"
case "${1:-}" in
    --resume)          mode="resume" ;;
    "")                 ;;
    -*)                 die "unknown option: $1 (usage: release.sh [patch|minor|major|--resume])" ;;
    patch|minor|major)  bump="$1" ;;
    *)                  die "unknown bump type: $1 (usage: release.sh [patch|minor|major|--resume])" ;;
esac
acted=0

check_marketplace_writable() {
    local probe
    probe=$(mktemp "$marketplace_dir/.release-writability-check.XXXXXX" 2>/dev/null) \
        || die "$marketplace_dir is not writable — release needs to replace marketplace.json there. If this is a Claude Code sandbox restriction: rerun this Bash call with dangerouslyDisableSandbox, or run '/add-dir $MARKETPLACE_DIR' first."
    rm -f "$probe"
}

common_preflight() {
    [ -f "$manifest" ] || die "$manifest not found — run from the repo root"
    git diff --quiet HEAD -- . ':(exclude)memory' || die "uncommitted changes"
    branch=$(git symbolic-ref -q --short HEAD || echo "")
    main_branch=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||' || echo "main")
    [ "$branch" = "$main_branch" ] || die "must be on $main_branch (currently $branch)"

    [ -n "${MARKETPLACE_DIR:-}" ] \
        || die "MARKETPLACE_DIR not set (set in .envrc to the claude-plugins repo root)"
    marketplace_json="$MARKETPLACE_DIR/.claude-plugin/marketplace.json"
    [ -f "$marketplace_json" ] || die "$marketplace_json not found"
    marketplace_dir=$(dirname "$marketplace_json")
    [ "$mode" = "release" ] && check_marketplace_writable
    plugin_name=$(jq -r .name "$manifest")
    if jq -e --arg n "$plugin_name" 'any(.plugins[]; .name == $n)' "$marketplace_json" >/dev/null; then
        marketplace_entry_exists=1
    else
        marketplace_entry_exists=0
        git remote get-url origin >/dev/null 2>&1 \
            || die "'$plugin_name' has no entry in $marketplace_json and no 'origin' remote to derive one from"
    fi
    git -C "$MARKETPLACE_DIR" diff --quiet HEAD -- . ':(exclude)memory' \
        || die "$MARKETPLACE_DIR has uncommitted changes"

    gh auth status >/dev/null 2>&1 || die "not authenticated with GitHub"
    [ -n "${UV_PUBLISH_TOKEN:-}" ] || die "UV_PUBLISH_TOKEN not set. Get token from https://pypi.org/manage/account/token/"
}

release_preflight() {
    plugin/bin/check-version-consistency.py \
        || die "plugin.json and pyproject.toml already disagree — fix that before releasing"
    manifest_version=$(jq -r .version "$manifest")
    latest_tag=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || true)
    if [ -n "$latest_tag" ] && [ "$manifest_version" != "$latest_tag" ]; then
        # shellcheck disable=SC2016  # backticks are literal markdown, not command substitution
        printf 'hint: plugin.json holds the LAST released version. `just release` bumps from there.\n' >&2
        printf '      revert any manual version bump and re-run.\n' >&2
        die "plugin.json version ($manifest_version) does not match latest tag (v$latest_tag)"
    fi
    V=$(jq -r --arg bump "$bump" '
      (.version | split(".") | map(tonumber)) as [$maj,$min,$pat]
      | if   $bump == "major" then [$maj+1, 0, 0]
        elif $bump == "minor" then [$maj, $min+1, 0]
        elif $bump == "patch" then [$maj, $min, $pat+1]
        else error("unknown bump type: " + $bump) end
      | map(tostring) | join(".")
    ' "$manifest")
    tag="v$V"
    ! git rev-parse -q --verify "refs/tags/$tag" >/dev/null || die "tag $tag already exists"
}

resume_preflight() {
    V=$(jq -r .version "$manifest")
    tag="v$V"
    git rev-parse -q --verify "refs/tags/$tag" >/dev/null || {
        printf 'hint: no release was started at this version.\n' >&2
        # shellcheck disable=SC2016  # backticks are literal markdown, not command substitution
        printf '      run `just release <bump>` instead.\n' >&2
        die "no tag $tag for plugin.json version $V"
    }
}

bump_commit_tag() {
    plugin/bin/bump-plugin-version.py "$V"
    visible-uv-version "$V"
    plugin/bin/check-version-consistency.py
    git add "$manifest" pyproject.toml uv.lock
    git commit -m "🔖 Release $V"
    git tag -a "$tag" -m "Release $V"
    acted=1
    note "manifest + tag: $tag created locally"
}

visible-uv-version() {
    uv version "$1" >/dev/null
}

push_branch() {
    local remote_head
    remote_head=$(git ls-remote origin "refs/heads/$branch" | cut -f1)
    if [ -n "$remote_head" ] && [ "$remote_head" = "$(git rev-parse HEAD)" ]; then
        note "branch $branch: already pushed"
        return
    fi
    git push
    acted=1
    note "branch $branch: pushed"
}

push_tag() {
    local remote_tag local_tag
    remote_tag=$(git ls-remote origin "refs/tags/$tag" | cut -f1)
    local_tag=$(git rev-parse "$tag")
    if [ -n "$remote_tag" ]; then
        [ "$remote_tag" = "$local_tag" ] \
            || die "$tag on origin points at $remote_tag, not $local_tag — refusing to move a published tag"
        note "github tag $tag: already pushed"
        return
    fi
    git push origin "$tag"
    acted=1
    note "github tag $tag: pushed"
}

publish_pypi() {
    if curl -sf -o /dev/null "https://pypi.org/pypi/$pypi_name/$V/json"; then
        note "pypi $pypi_name $V: already published"
        return
    fi
    uv build
    uv publish dist/*"$V"*
    acted=1
    note "pypi $pypi_name $V: published"
}

create_github_release() {
    if gh release view "$tag" >/dev/null 2>&1; then
        note "github release $tag: already created"
        return
    fi
    gh release create "$tag" --title "$V" --generate-notes
    acted=1
    note "github release $tag: created"
}

bump_marketplace() {
    local mp_tmp repo_slug mp_branch mp_remote_head mp_local_head committed=0
    mp_tmp=$(mktemp)
    if [ "$marketplace_entry_exists" = 1 ]; then
        jq --arg n "$plugin_name" --arg v "$V" \
            '(.plugins[] | select(.name == $n) | .version) = $v' \
            "$marketplace_json" > "$mp_tmp"
    else
        repo_slug=$(git remote get-url origin | sed -E 's#\.git$##; s#^.*[:/]([^/]+/[^/]+)$#\1#')
        jq --arg v "$V" --arg repo "$repo_slug" --slurpfile m "$manifest" '
          .plugins += [{
            name: $m[0].name,
            source: { source: "github", repo: $repo },
            description: ($m[0].description // ""),
            version: $v,
            author: ($m[0].author // { name: "" }),
            repository: ($m[0].repository // $m[0].homepage // ("https://github.com/" + $repo)),
            license: ($m[0].license // "MIT")
          }]
        ' "$marketplace_json" > "$mp_tmp"
    fi
    if cmp -s "$mp_tmp" "$marketplace_json"; then
        rm -f "$mp_tmp"
    else
        check_marketplace_writable
        mv "$mp_tmp" "$marketplace_json"
        git -C "$MARKETPLACE_DIR" add .claude-plugin/marketplace.json
    fi
    if git -C "$MARKETPLACE_DIR" diff --cached --quiet; then
        :
    else
        git -C "$MARKETPLACE_DIR" commit -m "release: $plugin_name $V"
        committed=1
        acted=1
    fi

    mp_branch=$(git -C "$MARKETPLACE_DIR" symbolic-ref -q --short HEAD || echo "")
    mp_remote_head=$(git -C "$MARKETPLACE_DIR" ls-remote origin "refs/heads/$mp_branch" | cut -f1)
    mp_local_head=$(git -C "$MARKETPLACE_DIR" rev-parse HEAD)
    if [ "$mp_remote_head" = "$mp_local_head" ]; then
        if [ "$committed" = 1 ]; then
            note "marketplace: $([ "$marketplace_entry_exists" = 1 ] && echo "bumped to $V" || echo "entry created at $V")"
        else
            note "marketplace: already at $V"
        fi
        return
    fi

    git -C "$MARKETPLACE_DIR" push
    acted=1
    if [ "$committed" = 1 ]; then
        note "marketplace: $([ "$marketplace_entry_exists" = 1 ] && echo "bumped to $V" || echo "entry created at $V")"
    else
        note "marketplace: committed earlier, pushed now"
    fi
}

common_preflight
if [ "$mode" = "release" ]; then
    release_preflight
    bump_commit_tag
else
    resume_preflight
fi
push_branch
push_tag
publish_pypi
create_github_release
bump_marketplace
if [ "$mode" = "resume" ] && [ "$acted" = 0 ]; then
    note "release $tag is already complete (nothing to do)"
else
    note "Release $tag complete"
fi
