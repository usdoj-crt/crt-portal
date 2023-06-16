PATH="$PATH:/home/vcap/deps/0/bin"

if [[ "$VCAP_SERVICES" != "{}" ]]; then
  echo -n 'Database name [via VCAP]: '
  echo "$VCAP_SERVICES" | jq -r '."aws-rds"[].credentials.db_name'

  echo -n 'Database username [via VCAP]: '
  echo "$VCAP_SERVICES" | jq -r '."aws-rds"[].credentials.username'
else
  echo -n 'Database name [via env]: '
  echo "$DB_NAME"

  echo -n 'Database username [via env]: '
  echo "$DB_USER"
fi

echo -n 'Can import dependencies? '
echo "$(curl -s 'localhost:8080/try_to_import_prod')"

echo -n 'Can import dev dependencies? '
echo "$(curl -s 'localhost:8080/try_to_import_dev')"
