PATH="$PATH:/home/vcap/deps/0/bin"

echo -n 'Can import dependencies? '
echo "$(curl -s 'localhost:8080/try_to_import_prod')"

echo -n 'Can import dev dependencies? '
echo "$(curl -s 'localhost:8080/try_to_import_dev')"
