/*
* * * * * ==============================
* * * * * ==============================
* * * * * ==============================
* * * * * ==============================
========================================
========================================
========================================
----------------------------------------
USWDS SASS GULPFILE
----------------------------------------
*/

var autoprefixer  = require('autoprefixer');
var autoprefixerOptions = require('./node_modules/uswds-gulp/config/browsers');
var gulp          = require('gulp');
var pkg           = require('./node_modules/uswds/package.json');
var postcss       = require('gulp-postcss');
var replace       = require('gulp-replace');
var sass          = require('gulp-sass');
var sourcemaps    = require('gulp-sourcemaps');
var uswds         = require('./node_modules/uswds-gulp/config/uswds');

/*
----------------------------------------
PATHS
----------------------------------------
- All paths are relative to the
  project root
- Don't use a trailing `/` for path
  names
----------------------------------------
*/

// Project Sass source directory
const PROJECT_SASS_SRC = './crt_portal/static/sass';

// Compiled CSS destination
const CSS_DEST = './crt_portal/static/css/compiled';

/*
----------------------------------------
TASKS
----------------------------------------
*/

gulp.task('build-sass', function(done) {
  var plugins = [
    // Autoprefix
    autoprefixer(autoprefixerOptions),
  ];
  return gulp.src([
      `${PROJECT_SASS_SRC}/*.scss`
    ])
    .pipe(sourcemaps.init({ largeFile: true }))
    .pipe(sass({
        includePaths: [
          `${PROJECT_SASS_SRC}`,
          `${uswds}/scss`,
          `${uswds}/scss/packages`,
        ]
      }))
    .pipe(replace(
      /\buswds @version\b/g,
      'based on uswds v' + pkg.version
    ))
    .pipe(postcss(plugins))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(`${CSS_DEST}`));
});

gulp.task('watch-sass', function () {
  gulp.watch(`${PROJECT_SASS_SRC}/**/*.scss`, gulp.series('build-sass'));
});

gulp.task('watch', gulp.series('build-sass', 'watch-sass'));

gulp.task('default', gulp.series('watch'));
