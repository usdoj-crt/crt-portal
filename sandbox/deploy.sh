#!/bin/bash

set -e  # Don't continue if one of the below commands fails.

./teardown.sh

cf target -o sandbox-usdoj

# This would happen with each deployment:
cat manifest1.yml.tpl | sed "s/WHOAMI/$(whoami)/g" > manifest1.yml
cf push -f manifest1.yml
rm manifest1.yml
