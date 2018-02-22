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
var eslint = require('gulp-eslint');
var autoprefixer = require('autoprefixer');
var merge = require('merge-stream');

var src = './static/src';
var dist = './static/dist';
var bower = './bower_components';
var npm = './node_modules';

var jquery = bower + '/jquery/dist';
var bootstrap = bower + '/bootstrap-sass/assets';
var bootstrapSelect = bower + '/bootstrap-select/dist';
var bootstrapDatetimepicker = bower + '/eonasdan-bootstrap-datetimepicker/build';
var fontawesome = bower + '/font-awesome';
var moment = bower + '/moment';
var swiper = bower + '/swiper/dist';

var template = {
	in : 'apps/**/*.jinja'
};

var js = {
	'in': [
		jquery + '/jquery.js',
		bootstrap + '/javascripts/bootstrap.js',
		bootstrapSelect + '/js/bootstrap-select.js',
		moment + '/min/moment.min.js',
		bootstrapDatetimepicker + '/js/bootstrap-datetimepicker.min.js',
    src + '/javascripts/**/*',
    swiper + '/js/swiper.min.js',
	],
	'out': dist + '/js'
};

var pdfjs = {
	'in': [
    npm + '/pdfjs-dist/build/pdf.js',
    npm + '/pdfjs-dist/build/pdf.worker.js',
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
      swiper + '/css/swiper.min.css',
		],
  },
	'out': dist + '/css',
	'opts': {
		errLogToConsole: true,
		includePaths: [bootstrap + '/stylesheets']
	}
};

// process JS files and return the stream.
gulp.task('js', ['clean-js'], function () {
    return gulp.src(js.in)
    .pipe(eslint({
      useEslintrc: false,
    }))
    .pipe(eslint.format())
    .pipe(eslint.failAfterError())
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

    var css_stream = gulp.src(css.in.css);
	return merge(scss_stream, css_stream)
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

gulp.task('revision:update-references', ['revision:rename'], () =>
  gulp.src([dist + '/manifest.json', dist + '/**/*.{json,css,js}'],  { base: './' })
  .pipe(collect())
  .pipe(gulp.dest('./'))
);

gulp.task('rename-css', ['clean-css', 'css'], function() {
  return (
    gulp.src([dist + '/**/*.css'], { base: './' })
        .pipe(rev())
        .pipe(gulp.dest('./'))
        .pipe(rev.manifest({ path: 'manifest.json' }))
        .pipe(gulp.dest(dist))
  );

});

gulp.task('update-references-css', ['clean-css', 'css', 'rename-css'], function() {
  return (
    gulp.src([dist + '/manifest.json', dist + '/**/*.{css}'],  { base: './' })
        .pipe(collect())
        .pipe(gulp.dest('./'))
  );
});

gulp.task('rename-js', ['clean-js', 'js'], function() {
  return (
    gulp.src([dist + '/**/*.js'], { base: './' })
        .pipe(rev())
        .pipe(gulp.dest('./'))
        .pipe(rev.manifest({ path: 'manifest.json' }))
        .pipe(gulp.dest(dist))
  );

});

gulp.task('update-references-js', ['clean-js', 'js', 'rename-js'], function() {
  return (
    gulp.src([dist + '/manifest.json', dist + '/**/*.{js}'],  { base: './' })
        .pipe(collect())
        .pipe(gulp.dest('./'))
  );
});

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

gulp.task('clean-fonts', function() { return gulp.src(fonts.out, { read: false })
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
  'revision:update-references',
]);

gulp.task('watch', ['default'], function() {
	livereload.listen();
	gulp.watch(css.in.scss, ['clean-css', 'css', 'rename-css', 'update-references-css']);
	gulp.watch(js.in, ['clean-js', 'js', 'rename-js', 'update-references-js']);
	gulp.watch([dist + '/**', template.in]).on('change', livereload.changed);
});