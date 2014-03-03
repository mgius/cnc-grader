#! /bin/bash
set -ex

mkdir -p working
pushd working
cp /submission/submission .
chmod +x ./submission
for infile in $(ls /inputs)
do
    suffix=$(echo $infile | grep -oP "\d+")
    ./submission < /inputs/$infile | diff -wBb - /outputs/out$suffix
done
popd

