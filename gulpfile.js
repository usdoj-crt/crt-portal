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

/**
 * See package.json for reference commit SHA from
 * https://github.com/uswds/uswds-gulp
 *
 * Primary differences on our side:
 * - We also use this to minify our own JavaScript
 * - We did not port over the SVG sprite maker
 *   (but may in future, if we need it)
 */

const autoprefixer = require("autoprefixer");
const csso = require("postcss-csso");
const gulp = require("gulp");
const pkg = require("./node_modules/@uswds/uswds/package.json");
const postcss = require("gulp-postcss");
const replace = require("gulp-replace");
const rename = require("gulp-rename");
const uglify = require("gulp-uglify");
const sass = require("gulp-sass")(require("sass"));
const sourcemaps = require("gulp-sourcemaps");
const uswds = "./node_modules/@uswds/uswds";
const shepherd = "./node_modules/shepherd.js";
const jquery = "./node_modules/jquery";
const datatable_js = "./node_modules/datatables.net";
const datatable_css = "./node_modules/datatables.net-dt";

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
const PROJECT_SASS_SRC = "./crt_portal/static/sass";

// Images destination
const IMG_DEST = "./crt_portal/static/img";

// Fonts destination
const FONTS_DEST = "./crt_portal/static/fonts";

// Javascript destination
const JS_DEST = "./crt_portal/static/js";
const JS_FILES = [`${JS_DEST}/*.js`, `!${JS_DEST}/*.min.js`];
const JS_VENDOR_FILES = [`${shepherd}/dist/js/**/**.min.js`, `${uswds}/dist/js/**/**.min.js`, `${jquery}/dist/**.min.js`, `${datatable_js}/js/**.min.js`];
const JS_VENDOR_DEST = "./crt_portal/static/vendor";

// Compiled CSS destination
const CSS_DEST = "./crt_portal/static/css/compiled";

// Site CSS destination
// Like the _site/assets/css directory in Jekyll, if necessary.
// If using, uncomment line 106
const SITE_CSS_DEST = "./path/to/site/css/destination";

/*
----------------------------------------
TASKS
----------------------------------------
*/

gulp.task("copy-uswds-setup", () => {
  return gulp
    .src(`${uswds}/dist/theme/**/**`)
    .pipe(gulp.dest(`${PROJECT_SASS_SRC}`));
});

gulp.task("copy-uswds-fonts", () => {
  return gulp.src(`${uswds}/dist/fonts/**/**`).pipe(gulp.dest(`${FONTS_DEST}`));
});

gulp.task("copy-uswds-images", () => {
  return gulp.src(`${uswds}/dist/img/**/**`).pipe(gulp.dest(`${IMG_DEST}`));
});

gulp.task('copy-vendor-js', () => {
  return gulp.src(JS_VENDOR_FILES)
    .pipe(gulp.dest(`${JS_VENDOR_DEST}`))
});

gulp.task('build-custom-js', function () {
  return gulp.src(JS_FILES)
    .pipe(sourcemaps.init())
    // Minify the file
    .pipe(uglify())
    .pipe(rename({
      suffix: '.min'
    }))
    .pipe(sourcemaps.write("."))
    // Output
    .pipe(gulp.dest(`${JS_DEST}`))
});

gulp.task(
  "build-js",
  gulp.parallel(
    "build-custom-js",
    "copy-vendor-js",
    )
);

gulp.task("build-sass", function (done) {
  var plugins = [
    // Autoprefix
    autoprefixer({
      cascade: false,
      grid: true,
    }),
    // Minify
    csso({ forceMediaMerge: false }),
  ];
  return (
    gulp
      .src([`${PROJECT_SASS_SRC}/*.scss`])
      .pipe(sourcemaps.init({ largeFile: true }))
      .pipe(
        sass({
          includePaths: [
            `${PROJECT_SASS_SRC}`,
            `${uswds}`,
            `${uswds}/packages`,
          ],
        })
      )
      .pipe(replace(/\buswds @version\b/g, "based on uswds v" + pkg.version))
      .pipe(postcss(plugins))
      .pipe(sourcemaps.write("."))
      // uncomment the next line if necessary for Jekyll to build properly
      //.pipe(gulp.dest(`${SITE_CSS_DEST}`))
      .pipe(gulp.dest(`${CSS_DEST}`))
  );
});

gulp.task(
  'build-css', () => {
    return gulp
      .src(`${datatable_css}/css/**.min.css`)
      .pipe(gulp.dest(`${CSS_DEST}`));
  });

gulp.task(
  "init",
  gulp.series(
    "copy-uswds-setup",
    "copy-uswds-fonts",
    "copy-uswds-images",
    "build-js",
    "build-css",
    "build-sass"
  )
);

gulp.task("watch-sass", function () {
  gulp.watch(`${PROJECT_SASS_SRC}/**/*.scss`, gulp.series("build-css", "build-sass", "watch-sass"));
});

gulp.task("watch-js", function () {
  gulp.watch(JS_FILES, gulp.series("build-js", "watch-js"));
});

gulp.task("build", gulp.parallel("build-css", "build-sass", "build-js"));

gulp.task("watch", gulp.parallel("watch-sass", "watch-js"));

gulp.task("default", gulp.series("watch"));
