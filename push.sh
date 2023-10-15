#!/bin/sh
version=`cat VERSION`

git push
git tag v$version
git push origin	v$version
