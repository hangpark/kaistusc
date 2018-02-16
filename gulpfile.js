var gulp = require('gulp');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var sass = require('gulp-sass');
var minifycss = require('gulp-minify-css');
var postcss = require('gulp-postcss');
var watch = require('gulp-watch');
var livereload = require('gulp-livereload');
var rev = require('gulp-rev');
var collect = require('gulp-rev-collector');
var clean = require('gulp-clean');
var autoprefixer = require('autoprefixer');
var merge = require('merge-stream');

var src = './static/src';
var dist = './static/dist';
var bower = './bower_components';

var jquery = bower + '/jquery/dist';
var jquery_ui = bower + '/jquery-ui';
var bootstrap = bower + '/bootstrap-sass/assets';
var bootstrapSelect = bower + '/bootstrap-select/dist';
var fontawesome = bower + '/font-awesome';

var template = {
	in : 'apps/**/*.jinja'
}

var js = {
	'in': [
		jquery + '/jquery.js',
		jquery_ui + '/jquery-ui.min.js',
		bootstrap + '/javascripts/bootstrap.js',
		bootstrapSelect + '/js/bootstrap-select.js',
    src + '/javascripts/**/*',
    '!' + src + '/javascripts/pdf.js',
    '!' + src + '/javascripts/pdf.worker.js',
	],
	'out': dist + '/js'
};

var pdfjs = {
	'in': [
    src + '/javascripts/pdf.js',
    src + '/javascripts/pdf.worker.js'
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
    'css': [
			fontawesome + '/css/font-awesome.css',
			bootstrapSelect + '/css/bootstrap-select.css'
		],
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
gulp.task('js', ['clean-js'], function () {
    return gulp.src(js.in)
		.pipe(concat('main.js'))
    .pipe(uglify())
		.pipe(gulp.dest(js.out))
    .pipe(livereload());
});

gulp.task('fonts', ['clean-fonts'], function() {
  return gulp.src(fonts.in)
    .pipe(gulp.dest(fonts.out));
});

gulp.task('css', ['clean-css'], function() {
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

gulp.task('revision:rename', ['js', 'css', 'fonts'], () =>
  gulp.src([dist + '/**/*.css', dist + '/**/*.js'], { base: './' })
  .pipe(rev())
  .pipe(gulp.dest('./'))
  .pipe(rev.manifest({ path: 'manifest.json' }))
  .pipe(gulp.dest(dist))
);

gulp.task('revision:updateReferences', ['revision:rename'], () =>
  gulp.src([dist + '/rev-manifest.json', dist + '/**/*.{json,css,js}'],  { base: './' })
  .pipe(collect())
  .pipe(gulp.dest('./'))
);

gulp.task('pdfjs', ['clean-js'], function() {
  return gulp.src(pdfjs.in)
        .pipe(gulp.dest(pdfjs.out));	
});

gulp.task('clean-js', function() {
  return gulp.src(js.out, { read: false })
        .pipe(clean());
})

gulp.task('clean-css', function() {
  return gulp.src(css.out, { read: false })
        .pipe(clean());
})

gulp.task('clean-fonts', function() {
  return gulp.src(fonts.out, { read: false })
        .pipe(clean());
})

gulp.task('default', [
  'clean-js', 
  'clean-css', 
  'clean-fonts', 
  'js', 
  'pdfjs',
  'fonts', 
  'css', 
  'revision:rename', 
  'revision:updateReferences', 
  'images',
]);

gulp.task('images', ['revision:updateReferences'], function() {
    return gulp.src(images.in)
           .pipe(gulp.dest(images.out));
});

gulp.task('watch', ['default'], function() {
	livereload.listen();
	gulp.watch(css.in.scss, ['clean-css', 'css']);
	gulp.watch(js.in, ['clean-js', 'js']);
	gulp.watch([dist + '/**', template.in]).on('change', livereload.changed);
});