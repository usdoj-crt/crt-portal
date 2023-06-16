#!/bin/bash

set -e  # Don't continue if one of the below commands fails.

cf target -o sandbox-usdoj

cf delete -rf "crt-portal-sandbox-worker1-$(whoami)"
