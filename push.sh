#!/bin/sh
version=`cat VERSION`
echo $version

git push
git tag v$version
git push origin	v$version
