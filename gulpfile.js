const gulp  = require("gulp"),
  rename = require('gulp-rename'),
  minify = require("gulp-minify");

function minifyjs() {
  return gulp.src('higher_health/static/js/main.js', { allowEmpty: true })
    .pipe(rename({
      extname: ".js"
    }))
    .pipe(minify({noSource: true}))
    .pipe(gulp.dest('higher_health/static/js/'))
}
//exports.default = minifyjs;
gulp.task('default', gulp.series(minifyjs));
