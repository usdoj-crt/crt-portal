#!/bin/bash
# make sure migrations are applied
echo migrate database...
python /code/crt_portal/manage.py migrate

echo USWDS gulp commands...
# running USWDS https://github.com/uswds/uswds-gulp
npm install autoprefixer css-mqpacker cssnano gulp@^4.0.0 gulp-notify gulp-postcss gulp-rename gulp-replace gulp-sass gulp-sourcemaps path uswds@latest uswds-gulp@github:uswds/uswds-gulp --save-dev

echo Starting Django Server…
python /code/crt_portal/manage.py compress
python /code/crt_portal/manage.py runserver 0.0.0.0:8000
