#!/bin/sh
version=`cat VERSION`

git tag v$version
git push --follow-tags
