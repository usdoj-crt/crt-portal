This was the result of a discovery sprint, I am in the process of cleaning it up for easier local install.

## Local set up

This is using Pipenv and Postgres

### Pipenv info

 https://github.com/pypa/pipenv

### Postgres

 https://www.postgresql.org/download/

I recommend [pgcli](https://www.pgcli.com/) for interfacing with postgres


In pgcli or your sql shell command to create datebase with:

    create database crt_portal;


commands to create local db user for app, replace `username` and `userpass` with your choices:

    CREATE USER username WITH PASSWORD 'userpass' CREATEDB;
    GRANT permissions ON DATABASE crt_portal TO username;


(I would like the local set up to be in docker next. so we don't need to to the previous steps)

Once you crate the crt_portal postgres database, set the variables in your local environment accordingly.

    export =''
    export DB_USER=''
    export DB_PASSWORD=''
    export DB_HOST='local'
    export SECRET_KEY=''
    export ENV='LOCAL'

Add those variables to your bash_profile so that you don't have to set them going forward.

For start up after you have initially installed the project, activate the environment, change directory to the app and run the server:

    pipenv shell
    cd crt_portal
    python manage.py runserver


The 'Local' setting will trigger the local_settings.py for easier setup.

If you have pipenv installed and your database set up, you can run the following commands to get the project running:

    pipenv install

    cd crt_portal

apply the data migrations

    python manage.py migrate

create a superuser for admin access

    python manage.py createsuperuser

run the server on localhost:8000

    python manage.py runserver

add some test data after you log in at `/admin`


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

in another terminal if you are doing front end work

    gulp watch



## cloud.gov set up

- create postgres DB and S3 with development settings:
 cf create-service aws-rds shared-psql crt-db
 cf create-service s3 basic-public crt-s3

(or basic-sandbox if in sandbox)


- store environment variables
 cf cups VCAP_SERVICES -p "{'SECRET_KEY': 'replace-with-your-secret-key'}"

(I had to give it the varable name in this command and follow up with the secret key, I am not sure why)

Need to ssh to create superuser (would like to do this automatically in another PR)

    cf ssh crt-portal-django

once in, activate local env

Needed to enable CORS via awscli https://cloud.gov/docs/services/s3/#allowing-client-side-web-access-from-external-applications (would like to do this automatically in another PR)

