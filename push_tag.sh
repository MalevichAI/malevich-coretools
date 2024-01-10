#!/bin/sh
version=`cat VERSION`
echo $version

git tag v$version
git push origin	v$version
