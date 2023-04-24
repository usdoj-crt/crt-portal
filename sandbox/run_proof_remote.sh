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

echo -n 'Can modify database? '
echo "$(curl -s 'localhost:8080/modify')"

echo -n 'Can create database users? '
echo "$(curl -s 'localhost:8080/create_analytics_user')"

echo -n 'Can read from database? '
echo "$(curl -s 'localhost:8080/read')"
