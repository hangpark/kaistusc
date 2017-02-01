var gulp = require('gulp');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var sass = require('gulp-sass');
var minifycss = require('gulp-minify-css');
var postcss = require('gulp-postcss');
var autoprefixer = require('autoprefixer');
var merge = require('merge-stream');

var src = './static/src';
var dist = './static/dist';
var bower = './bower_components';

var jquery = bower + '/jquery/dist';
var bootstrap = bower + '/bootstrap-sass/assets';
var fontawesome = bower + '/font-awesome';

var js = {
	'in': [
		jquery + '/jquery.js',
		bootstrap + '/javascripts/bootstrap.js',
        src + '/javascripts/**/*'
	],
	'out': dist + '/js'
};

var fonts = {
	'in': [
        bootstrap + '/fonts/**/*',
        fontawesome + '/fonts/**/*',
    ],
	'out': dist + '/fonts'
};

var css = {
	'in': {
        'scss': src + '/stylesheets/main.scss',
        'css': fontawesome + '/css/font-awesome.css',
    },
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

gulp.task('css', ['fonts'], function() {
    var scss_stream = gulp.src(css.in.scss)
        .pipe(sass(css.opts));

    var css_stream = gulp.src(css.in.css);
    
	return merge(scss_stream, css_stream)
        .pipe(concat('main.css'))
		.pipe(postcss([ autoprefixer() ]))
		.pipe(minifycss())
		.pipe(gulp.dest(css.out));
});

gulp.task('default', ['js', 'fonts', 'css']);
