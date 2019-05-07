#! /bin/bash

# automatically add and commit files to a repo
# args $2 and beyond are globs representing files not to
# add to commits: i.e. files you don't want to automatically 
# commit but don't want to add to a .gitignore either

repo_loc=$1

exclusion_fmt=":!%s "
exclusions=

shift
while (( $# )) ; do
  exclusions+=$(printf "$exclusion_fmt" $1)
  shift
done

if [[ -n $(git -C $repo_loc status -s) ]]; then
  git -C $repo_loc add $(readlink -f $repo_loc)** $exclusions
  git -C $repo_loc commit -m "auto-commit"
fi
