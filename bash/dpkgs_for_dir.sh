#! /bin/bash

# in case you whoopsie and delete a kind
# of important directory (but one that
# doesn't contain system-critical
# files)

chk_dir=$1
all_pkgs=$(dpkg --get-selections | awk '{ print $1 }')

for pkg in $all_pkgs; do
  dirs=$(dpkg-query -L $pkg)
  for dir in $dirs; do
    [[ $dir == $chk_dir** ]] && echo $pkg && break
  done
done
