#!/bin/bash

set -e  # Don't continue if one of the below commands fails.

cf target -o sandbox-usdoj

cf delete-service -w -f "crt-sandbox-db-$(whoami)"

cf delete -rf "crt-portal-sandbox-worker1-$(whoami)"
cf delete -rf "crt-portal-sandbox-worker2-$(whoami)"
