var gulp = require('gulp');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var sass = require('gulp-sass');
var minifycss = require('gulp-minify-css');
var postcss = require('gulp-postcss');
var watch = require('gulp-watch');
var livereload = require('gulp-livereload');
var autoprefixer = require('autoprefixer');
var merge = require('merge-stream');

var src = './static/src';
var dist = './static/dist';
var bower = './bower_components';

var jquery = bower + '/jquery/dist';
var bootstrap = bower + '/bootstrap-sass/assets';
var bootstrapSelect = bower + '/bootstrap-select/dist';
var bootstrapDatetimepicker = bower + '/eonasdan-bootstrap-datetimepicker/build';
var fontawesome = bower + '/font-awesome';
var moment = bower + '/moment';

var template = {
	in : 'apps/**/*.jinja'
}

var js = {
	'in': [
		jquery + '/jquery.js',
		bootstrap + '/javascripts/bootstrap.js',
		bootstrapSelect + '/js/bootstrap-select.js',
		moment + '/min/moment.min.js',
		bootstrapDatetimepicker + '/js/bootstrap-datetimepicker.min.js',
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
		'scss': src + '/stylesheets/*.scss',
        'main': src + '/stylesheets/main.scss',
        'css': [
			fontawesome + '/css/font-awesome.css',
			bootstrapSelect + '/css/bootstrap-select.css',
			bootstrapDatetimepicker + '/css/bootstrap-datetimepicker.min.css',
		],
    },
	'out': dist + '/css',
	'opts': {
		errLogToConsole: true,
		includePaths: [bootstrap + '/stylesheets']
	}
};

// process JS files and return the stream.
gulp.task('js', function () {
    return gulp.src(js.in)
		.pipe(concat('main.js'))
        .pipe(uglify())
		.pipe(gulp.dest(js.out))
		.pipe(livereload());
});

gulp.task('fonts', function() {
	return gulp.src(fonts.in)
		.pipe(gulp.dest(fonts.out));
});

gulp.task('css', function() {
    var scss_stream = gulp.src(css.in.main)
        .pipe(sass(css.opts));

    var css_stream = gulp.src(css.in.css);
    
	return merge(scss_stream, css_stream)
        .pipe(concat('main.css'))
		.pipe(postcss([ autoprefixer() ]))
		.pipe(minifycss())
		.pipe(gulp.dest(css.out))
		.pipe(livereload());
});

gulp.task('default', ['js', 'fonts', 'css']);

gulp.task('watch', ['default'], function() {
	livereload.listen();
	gulp.watch(css.in.scss, ['css']);
	gulp.watch(js.in, ['js']);
	gulp.watch([dist + '/**', template.in]).on('change', livereload.changed);
});