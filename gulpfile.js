var gulp = require('gulp');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var sass = require('gulp-sass');
var minifycss = require('gulp-minify-css');
var postcss = require('gulp-postcss');
var autoprefixer = require('autoprefixer');

var src = './static/src';
var dist = './static/dist';
var bower = './bower_components';

var jquery = bower + '/jquery/dist';
var bootstrap = bower + '/bootstrap-sass/assets';

var js = {
	'in': [
		jquery + '/jquery.js',
		bootstrap + '/javascripts/bootstrap.js',
        src + '/javascripts/**/*'
	],
	'out': dist + '/js'
};

var fonts = {
	'in': bootstrap + '/fonts/**/*',
	'out': dist + '/fonts'
};

var scss = {
	'in': src + '/stylesheets/main.scss',
	'out': dist + '/css',
	'opts': {
		errLogToConsole: true,
		includePaths: [bootstrap + '/stylesheets']
	}
};

gulp.task('js', function() {
	return gulp.src(js.in)
		.pipe(concat('main.js'))
		.pipe(uglify())
		.pipe(gulp.dest(js.out));
});

gulp.task('fonts', function() {
	return gulp.src(fonts.in)
		.pipe(gulp.dest(fonts.out));
});

gulp.task('scss', ['fonts'], function() {
	return gulp.src(scss.in)
		.pipe(sass(scss.opts))
		.pipe(postcss([ autoprefixer() ]))
		.pipe(minifycss())
		.pipe(gulp.dest(scss.out));
});

gulp.task('default', ['js', 'fonts', 'scss']);
