#!/bin/bash

set -e  # Don't continue if one of the below commands fails.

./teardown.sh

cf target -o sandbox-usdoj

This would happen once, as an infrequent / maintenance tasks:
cf create-service aws-rds micro-psql crt-sandbox-db
while cf service crt-sandbox-db | grep "create in progress" > /dev/null; do
  echo 'Waiting for crt-sandbox-db to be created, this takes a few minutes...'
  sleep 10
done

# This would happen with each deployment:
cf push -f manifest1.yml
cf push -f manifest2.yml

# This would happen once, as an infrequent / maintenance tasks:
cf set-env crt-portal-sandbox-worker2 DB_USER "analytics"
cf set-env crt-portal-sandbox-worker2 DB_PASS "secretpassword"

# This would happen with each deployment, to "bind" the service without
# credentials:
db_env="$(cf env crt-portal-sandbox-worker1 | awk '/VCAP_SERVICES/,/^}/' | sed 's/^VCAP_SERVICES: //')"

db_host="$(echo "$db_env" | jq -r '."aws-rds"[].credentials.host')"
db_port="$(echo "$db_env" | jq -r '."aws-rds"[].credentials.port')"
db_name="$(echo "$db_env" | jq -r '."aws-rds"[].credentials.db_name')"
cf set-env crt-portal-sandbox-worker2 DB_HOST "$db_host"
cf set-env crt-portal-sandbox-worker2 DB_PORT "$db_port"
cf set-env crt-portal-sandbox-worker2 DB_NAME "$db_name"

cf restart 'crt-portal-sandbox-worker2'
