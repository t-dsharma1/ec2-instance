#!/usr/bin/env bash

set -eu

version=""
env_name=""
service_name="api"
remote_name="origin"

usage() {
 echo "Usage: $0 -e <env_name> -v <version_name> [OPTIONS]"
 echo "Options:"
 echo " -h, --help      Display this help message"
 echo " -v, --version   Version tag name"
 echo " -e, --env       Environment name (develop / prod)"
 echo " -r, --remote    Git remote name (default: ${remote_name})"
}

has_argument() {
    [[ ("$1" == *=* && -n ${1#*=}) || ( ! -z "$2" && "$2" != -*)  ]];
}

extract_argument() {
  echo "${2:-${1#*=}}"
}

# Function to handle options and arguments
handle_options() {
  while [ $# -gt 0 ]; do
    case $1 in
      -h | --help)
        usage
        exit 0
        ;;
      -v | --version*)
        if ! has_argument $@; then
          echo "Error: Version not specified." >&2
          usage
          exit 1
        fi

        version=$(extract_argument $@)

        shift
        ;;
      -e | --env*)
        if ! has_argument $@; then
          echo "Error: Env not specified." >&2
          usage
          exit 1
        fi

        env_name=$(extract_argument $@)

        shift
        ;;
      -r | --remote*)
        if ! has_argument $@; then
          echo "Error: Remote not specified." >&2
          usage
          exit 1
        fi

        remote_name=$(extract_argument $@)

        shift
        ;;
      *)
        echo "Invalid option: $1" >&2
        usage
        exit 1
        ;;
    esac
    shift
  done
}

# Main script execution
handle_options "$@"


if [ -z "${version}" ]; then
  echo -e "Error: Version not specified.\n" >&2
  usage
  exit 1
fi

if [ -z "${env_name}" ]; then
  echo -e "Error: Env name not specified.\n" >&2
  usage
  exit 1
fi

echo -e "----------"
echo "Releasing"
echo -e " Version: ${version}"
echo -e " Env name: ${env_name}"
echo -e "----------\n"

git fetch "${remote_name}" -a

if [[ `git status --porcelain --untracked-files=no` ]]; then
  echo -e "Error: There are changes in your local repository. Please stash them before running this command.\n" >&2
  exit 1
fi

current_branch_name=$(git rev-parse --abbrev-ref HEAD)
release_branch="release/${env_name}/${service_name}"

git checkout "${release_branch}"
git reset --hard "${remote_name}/${release_branch}"
git merge "${version}"
git push
git checkout "${current_branch_name}"

echo -e "\n----------"
echo "Deploy started:"
echo -e " Version: ${version}"
echo -e " Env name: ${env_name}"
echo -e " Deploy actions: https://github.com/bcgx-pi-deep-ai-core/genie-llm-api/actions/workflows/api.yaml"
echo -e "----------\n"
