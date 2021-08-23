#!/bin/bash

ORIG="$(cd "$(dirname "$0")" || exit; pwd)"

if ! command -v yq > /dev/null; then
    echo "You need yq to use this script. You can download it from:"
    echo "https://github.com/mikefarah/yq/releases"
    exit 2
fi

agnosticv_assert_args() {
    if [ -z "${1}" ] || [ -z "${2}" ] || [ -z "${3}" ]; then
        echo "argument missing: agnosticv ACCOUNT CATALOGITEM STAGE"
        exit 2
    fi
}

agnosticv_get_yaml() {
    agnosticv_assert_args "$@"
    local repo_dir=${ORIG}

    # Merge all yaml files in the right order
    echo '---'
    flist=()
    for yamlfile in "${repo_dir}"/common.y{a,}ml \
                                 "${repo_dir}/${1}"/common.y{a,}ml \
                                 "${repo_dir}/${1}"/account*.y{a,}ml \
                                 "${repo_dir}/${1}/${2}"/common.y{a,}ml \
                                 "${repo_dir}/${1}/${2}/${3}"*.y{a,}ml ; do
        if [ -e "${yamlfile}" ]; then
            echo "# ${yamlfile//${repo_dir}/}"
            flist+=("${yamlfile}")
        fi
    done
    if [ -n "${SHOW_META}" ]; then
        yq m -x "${flist[@]}"
    else
        yq m -x "${flist[@]}" | yq d - agnosticv_meta
    fi
}


SHOW_META=yes agnosticv_get_yaml "$@"
