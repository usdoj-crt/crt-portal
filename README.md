

## local set up

crate postgres database and set the variables below accordingly

    export =''
    export DB_USER=''
    export DB_PASSWORD=''
    export DB_HOST='local'
    export SECRET_KEY=''
    export ENV='LOCAL'



python manage.py migrate

python manage.py runserver



## cloud set up

- create postgres DB and S3 with development settings:
 cf create-service aws-rds shared-psql crt-db
 cf create-service s3 basic-public crt-s3

- store environment variables
 cf cups VCAP_SERVICES -p "{'SECRET_KEY': 'replace-with-your-secret-key'}"


Need to ssh to create superuser (will do this automatically in another PR)
