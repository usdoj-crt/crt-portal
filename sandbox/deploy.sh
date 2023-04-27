#!/bin/bash

set -e  # Don't continue if one of the below commands fails.

./teardown.sh

cf target -o sandbox-usdoj

# This would happen once, as an infrequent / maintenance tasks:
cf create-service aws-rds micro-psql "crt-sandbox-db-$(whoami)"
while cf service "crt-sandbox-db-$(whoami)" | grep "create in progress" > /dev/null; do
  echo "Waiting for crt-sandbox-db-$(whoami) to be created, this takes a few minutes..."
  sleep 10
done

# This would happen with each deployment:
cat manifest1.yml.tpl | sed "s/WHOAMI/$(whoami)/g" > manifest1.yml
cat manifest2.yml.tpl | sed "s/WHOAMI/$(whoami)/g" > manifest2.yml
cf push -f manifest1.yml
cf push -f manifest2.yml
rm manifest1.yml manifest2.yml

# This would happen once, as an infrequent / maintenance tasks:
cf set-env "crt-portal-sandbox-worker2-$(whoami)" DB_USER "analytics"
cf set-env "crt-portal-sandbox-worker2-$(whoami)" DB_PASS "secretpassword"

# This would happen with each deployment, to "bind" the service without
# credentials:
db_env="$(cf env "crt-portal-sandbox-worker1-$(whoami)" | awk '/VCAP_SERVICES/,/^}/' | sed 's/^VCAP_SERVICES: //')"

db_host="$(echo "$db_env" | jq -r '."aws-rds"[].credentials.host')"
db_port="$(echo "$db_env" | jq -r '."aws-rds"[].credentials.port')"
db_name="$(echo "$db_env" | jq -r '."aws-rds"[].credentials.db_name')"
cf set-env "crt-portal-sandbox-worker2-$(whoami)" DB_HOST "$db_host"
cf set-env "crt-portal-sandbox-worker2-$(whoami)" DB_PORT "$db_port"
cf set-env "crt-portal-sandbox-worker2-$(whoami)" DB_NAME "$db_name"

cf restart "crt-portal-sandbox-worker2-$(whoami)"
