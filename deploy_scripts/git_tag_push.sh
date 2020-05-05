#!/bin/bash
ENV_TAG_PREFIX=""

#get highest tag number
VERSION=`git describe --match "$ENV_TAG_PREFIX[0-9]*" --abbrev=0 --tags`

BRANCH_NAME=`git rev-parse --abbrev-ref HEAD`
if [ "$BRANCH_NAME" != "master" ] ; then
  echo "Not pushing tags as not on master"
  exit 0
fi

#replace ENV_TAG_PREFIX with empty string for numeric increment
VERSION=${VERSION//$ENV_TAG_PREFIX/}

#replace . with space so can split into an array
VERSION_BITS=(${VERSION//./ })

#get number parts and increase last one by 1
MAJOR_VERSION=${VERSION_BITS[0]}
if [ "$MAJOR_VERSION" = "" ] ; then
  MAJOR_VERSION=0;
fi

MAJOR_VERSION=$((MAJOR_VERSION+1))

#create new tag
NEW_TAG="$ENV_TAG_PREFIX$MAJOR_VERSION.0"

echo "Last tag version $VERSION New tag will be $NEW_TAG"

#get current hash and see if it already has a tag
GIT_COMMIT=`git rev-parse HEAD`
NEEDS_TAG=`git describe --contains $GIT_COMMIT 2>/dev/null`

echo "-------------------------------------------------------------------------"
# only tag if no tag already (would be better if the git describe command above could have a silent option)
if [ -z "$NEEDS_TAG" ]; then
  echo "Tagged with $NEW_TAG"
  git tag $NEW_TAG
  git push origin $NEW_TAG
else
  echo "Current commit already has a tag $VERSION"
fi
echo "-------------------------------------------------------------------------"
