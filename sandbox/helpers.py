import json
import os
import psycopg2


def get_uri_from_env():
    # First, see if there's a bound service (this should be worker1)
    try:
        return json.loads(os.getenv('VCAP_SERVICES'))['aws-rds'][0]['credentials']['uri']
    except KeyError:
        print('Worker is not set up to read RDS from VCAP_SERVICES')

    # Then, see if there's env vars (should be worker2)
    try:
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASS')
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        dbname = os.getenv('DB_NAME')

        env = [user, password, host, port, dbname]
        if any(v is None for v in env):
            print(f"Something was unset: {env}")
        return f"postgres://{user}:{password}@{host}:{port}/{dbname}"
    except KeyError:
        pass

    print("Really couldn't find any DB credentials, that's not good")
    return None


def create_analytics_user():
    """Creates a user for worker2 to make read requests."""
    connection = None
    cursor = None
    db_uri = get_uri_from_env()
    try:
        db_name = json.loads(os.getenv('VCAP_SERVICES'))['aws-rds'][0]['credentials']['db_name']
    except KeyError:
        return "No VCAP_SERVICES, can't create users"
    try:
        connection = psycopg2.connect(db_uri)
        cursor = connection.cursor()
        cursor.execute("CREATE ROLE analytics WITH LOGIN PASSWORD 'secretpassword'")
        cursor.execute(f"GRANT CONNECT ON DATABASE {db_name} TO analytics;")
        cursor.execute("GRANT SELECT ON TABLE test TO analytics")
        connection.commit()
        return 'ok'
    except Exception as e:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        return f"Wasn't able to create user: {e}"


def modify():
    """Creates a table, adds records, and deletes records."""
    db_uri = get_uri_from_env()
    connection = None
    cursor = None
    result = None
    try:
        connection = psycopg2.connect(db_uri)
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS test;")
        cursor.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
        cursor.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))
        cursor.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (200, "abc'def"))
        cursor.execute("DELETE FROM test WHERE num=200")
        cursor.execute("SELECT * FROM test;")
        connection.commit()
        result = json.dumps(cursor.fetchall())
    except Exception as e:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        return f"Wasn't able to modify: {e}"
    return f"Modified table to contain: {result}"


def read():
    """Reads from the test table. Assumes modify ran successfully."""
    db_uri = get_uri_from_env()
    connection = None
    cursor = None
    result = None
    try:
        connection = psycopg2.connect(db_uri)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM test;")
        result = json.dumps(cursor.fetchall())
    except Exception as e:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        return f"Wasn't able to read: {e}"
    return f"Read from table: {result}"
