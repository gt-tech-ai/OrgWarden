parse_and_add_tags() {
    tag="$1"

    # validate tag and capture major/minor/patch
    if [[ ! "$tag" =~ ^([^0-9]*)([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        echo "Invalid semantic version tag: $tag" >&2
        exit 1
    fi
    prefix="${BASH_REMATCH[1]}"
    major="${BASH_REMATCH[2]}"
    minor="${BASH_REMATCH[3]}"
    patch="${BASH_REMATCH[4]}"

    # create new tags
    major_tag="${prefix}${major}"
    minor_tag="${prefix}${major}.${minor}"
    patch_tag="${prefix}${major}.${minor}.${patch}"

    # apply tags
    git tag "$major_tag" -f
    git tag "$minor_tag" -f
    git tag "$patch_tag" # shouldn't have to force, if we do, something has gone wrong
}

# update package tags
package_tag=$(uv run autogitsemver src --no-branch-name --no-metadata --quiet)
parse_and_add_tags "$package_tag"

# update action tags
action_tag=$(uv run autogitsemver action-version --no-branch-name --no-metadata --quiet)
parse_and_add_tags "$action_tag"

# push tags
git push --tags --force