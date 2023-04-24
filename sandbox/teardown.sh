#!/bin/bash

set -e  # Don't continue if one of the below commands fails.

cf target -o sandbox-usdoj

cf delete-service -w -f crt-sandbox-db

cf delete -rf crt-portal-sandbox-worker1
cf delete -rf crt-portal-sandbox-worker2
