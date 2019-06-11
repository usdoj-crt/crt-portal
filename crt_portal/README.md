

## local set up

crate postgres database

export DB_NAME=''
export DB_USER=''
export DB_PASSWORD=''
export DB_HOST=''
export SECRET_KEY=''


    export VCAP_SERVICES="""{
        'aws-rds':
            [
                {
                    'credentials':
                        {
                            'db_name': '',
                            'host': '',
                            'password': '',
                            'port': '',
                            'username': ''
                        },
                },
            ],
        'user-provided':
            [
                {
                    'credentials':
                        {
                            'SECRET_KEY': ''},
                        }
                }
            ]
    }"""

python manage.py migrate

python manage.py runserver



## cloud set up

- create postgres DB and S3 with development settings:
 cf create-service aws-rds shared-psql crt-db
 cf create-service s3 basic-public crt-s3

- store environment variables
 cf cups VCAP_SERVICES -p "{'SECRET_KEY': 'replace-with-your-secret-key'}"
