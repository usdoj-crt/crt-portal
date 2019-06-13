These are a work in progress as I set things up

## local set up

add first time postgress and node set up instructions


Crate postgres database and set the variables below accordingly

    export =''
    export DB_USER=''
    export DB_PASSWORD=''
    export DB_HOST='local'
    export SECRET_KEY=''
    export ENV='LOCAL'

Set up node for front end files
[some of this won't need to be repeated]

    npm install
    npm install gulp-cli -g
    npm install autoprefixer css-mqpacker cssnano gulp@^4.0.0 gulp-notify gulp-postcss gulp-rename gulp-replace gulp-sass gulp-sourcemaps path uswds@^2.0.0 uswds-gulp@github:uswds/uswds-gulp --save-dev
    gulp init
    gulp inits

run server locally

    python manage.py compress
    python manage.py runserver



## cloud.gov set up

- create postgres DB and S3 with development settings:
 cf create-service aws-rds shared-psql crt-db
 cf create-service s3 basic-public crt-s3

- store environment variables
 cf cups VCAP_SERVICES -p "{'SECRET_KEY': 'replace-with-your-secret-key'}"


Need to ssh to create superuser (will do this automatically in another PR)
