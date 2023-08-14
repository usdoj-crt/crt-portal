# Run this locally or on CI/CD to set jupyter VCAP variables on Cloud Foundry.
#
# Note: this is only part of setting up a new instance of Jupyter.
# See maintenance_or_infrequent_tasks.md for more details.

if ! command -v jq &> /dev/null; then
  >&2 echo 'Please install jq to continue (https://github.com/jqlang/jq)'
  exit 127
fi

. env-helpers.sh crt-portal-django

function get_db_config() {
  cf_get_multiline_env VCAP_SERVICES \
    | jq '.["aws-rds"][0]["credentials"]'
}

function cf_set_env() {
  cf set-env "crt-portal-jupyter" "$1" "$2" 1>/dev/null
}

portal_services="$(get_db_config)"
cf_env_target crt-portal-jupyter
jupyter_services="$(get_db_config)"

db_name="$(echo "$portal_services" | jq -r '.["db_name"]')"
db_host="$(echo "$portal_services" | jq -r '.["host"]')"
db_port="$(echo "$portal_services" | jq -r '.["port"]')"
db_user="$(echo "$jupyter_services" | jq -r '.["username"]')"
db_password="$(echo "$jupyter_services" | jq -r '.["password"]')"

# Format needed for Python connections:
cf_set_env DATABASE_URL "postgresql://$db_user:$db_password@$db_host:$db_port/$db_name"

# Format needed for R connections:
cf_set_env DATABASE_HOSTNAME "$db_host"
cf_set_env DATABASE_PORT "$db_port"
cf_set_env DATABASE_USER "$db_user"
cf_set_env DATABASE_PASSWORD "$db_password"
