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
var jquery_ui = bower + '/jquery-ui';
var bootstrap = bower + '/bootstrap-sass/assets';
var fontawesome = bower + '/font-awesome';

var template = {
	in : 'apps/**/*.jinja'
}

var js = {
	'in': [
		jquery + '/jquery.js',
		jquery_ui + '/jquery-ui.min.js',
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
		'scss': src + '/stylesheets/*.scss',
        'main': src + '/stylesheets/main.scss',
        'jquery_ui': jquery_ui + '/themes/base/jquery-ui.css', 
        'css': fontawesome + '/css/font-awesome.css',
    },
	'out': dist + '/css',
	'opts': {
		errLogToConsole: true,
		includePaths: [bootstrap + '/stylesheets']
	}
};

var images = {
	'in':[
		jquery_ui+'/themes/base/images/*',
	],
	'out':dist+'/css/images/'
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
 	var css_stream2 = gulp.src(css.in.jquery_ui);
	return merge(scss_stream, css_stream,css_stream2)
        .pipe(concat('main.css'))
		.pipe(postcss([ autoprefixer() ]))
		.pipe(minifycss())
		.pipe(gulp.dest(css.out))
		.pipe(livereload());
});

gulp.task('images', function() {
    return gulp.src(images.in)
           .pipe(gulp.dest(images.out));
});

gulp.task('default', ['js', 'fonts', 'css','images']);

gulp.task('watch', function() {
	livereload.listen();
	gulp.watch(css.in.scss, ['css']);
	gulp.watch(css.in.js, ['js']);
	gulp.watch([dist + '/**', template.in]).on('change', livereload.changed);
});