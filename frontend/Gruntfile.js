module.exports = function(grunt) {

  'use strict';

  grunt.initConfig({

    /**
     * Pull in the package.json file so we can read its metadata.
     */
    pkg: grunt.file.readJSON('package.json'),

    /**
     * Here's a banner with some template variables.
     * We'll be inserting it at the top of minified assets.
     */
    banner:
      '/*\n' +
      ' * ==========================================================================\n' +
      ' * Package name: <%= pkg.name %>\n' +
      ' * Version: <%= pkg.version %>\n' +
      ' * Last modified: <%= grunt.template.today("yyyy-mm-dd h:MM:ss TT") %>\n' +
      ' * URL: <%= pkg.homepage %>\n' +
      ' * A public domain work of the <%= pkg.author.name %>\n' +
      ' * ==========================================================================\n' +
      '*/\n\n',


    /* 
     * CONCAT
     * 
     * Combine vendor supplied CSS files
     * 
    */

    concat: {
      main: {
        src: [
          'frontend/bower_components/normalize.css/normalize.css',
          'frontend/bower_components/font-awesome/css/font-awesome.min.css'
        ],
        dest: 'frontend/dist/css/vendor.min.css',
      }
    },


    /**
     * LESS: https://github.com/gruntjs/grunt-contrib-less
     * 
     * Compile LESS files to CSS.
     * All of the cf-framework LESS files have been added to styles.css.
     */
    less: {
      main: {
        options: {
          paths: ['frontend/src/less']
        },
        files: {
          'frontend/dist/css/<%= pkg.name %>.css': ['<%= banner %>', 'frontend/src/less/<%= pkg.name %>.less']
        }
      }
    },

    /**
     * Autoprefixer: https://github.com/nDmitry/grunt-autoprefixer
     * 
     * Add vendor-specific css prefixes. Do not put the prefixes in your CSS code.
     *
     */
    autoprefixer: {
      options: {
        // Options we might want to enable in the future.
        diff: false,
        map: false
      },
      multiple_files: {
        // Prefix all CSS files found in `src/static/css` and overwrite.
        expand: true,
        src: 'frontend/dist/css/<%= pkg.name %>.css'
      },
    },



    /**
     * CSSMin: https://github.com/gruntjs/grunt-contrib-cssmin
     * 
     * Create a Minified CSS.
     * 
     */
    cssmin: {
      minify: {
        files: {
          'frontend/dist/css/<%= pkg.name %>.min.css': ['frontend/dist/css/<%= pkg.name %>.css']
        }
      }
    },

    /**
     * Uglify: https://github.com/gruntjs/grunt-contrib-uglify
     * 
     * Concatenate and Minify JS files.
     * We are excluding minified files with the final ! pattern.
     */
    uglify: {
      options: {
        compress: true,
        mangle: false,
        beautify: true,
        banner: '<%= banner %>'
      }
      ,
      vendor: {
        src: [
          'frontend/bower_components/jquery/dist/jquery.js',
          'frontend/bower_components/jquery.easing/js/jquery.easing.js',
          'frontend/bower_components/cf-expandables/src/js/cf-expandables.js'
        ],
        dest: 'frontend/dist/js/vendor.min.js'
      },
      main: {
        src: ['frontend/src/js/<%= pkg.name %>.js'],
        dest: 'frontend/dist/js/<%= pkg.name %>.min.js'
      }
      
    },

/*
    topdoc: {
      demo: {
        options: {
          source: 'demo/static/css/',
          destination: 'demo/',
          template: 'node_modules/cf-component-demo/' + ( grunt.option('tpl') || 'raw' ) + '/',
          templateData: {
            family: '<%= pkg.name %>',
            title: '<%= pkg.name %> demo',
            repo: '<%= pkg.homepage %>',
            ltIE8Source: 'static/css/main.lt-ie8.min.css',
            custom: '<%= grunt.file.read("demo/custom.html") %>'
          }
        }
      },
*/


    /**
     * Copy: https://github.com/gruntjs/grunt-contrib-copy
     */
    copy: {
      main: {
        files: [
          /* Vendor Packages */
          {
            expand: true,
            flatten: true,
            src: ['frontend/bower_components/font-awesome/font/*'],
            dest: 'frontend/dist/font/',
            filter: 'isFile'
          },
          {
            expand: true,
            flatten: true,
            src: ['frontend/bower_components/cf-icons/src/fonts/*'],
            dest: 'frontend/dist/fonts/',
            filter: 'isFile'
          },
          /* Source images that where manually downloaded to the src/img folder */
          {
            expand: true,
            flatten: true,
            src: ['frontend/src/img/*'],
            dest: 'frontend/dist/img/',
            filter: 'isFile'
          }
        ]
      },
      django: {
        files: [
          /* Copy the front/dist folder into the Django application's static assets folder */
          {
            expand: true,
            cwd: 'frontend/dist/',
            src: ['**'],
            dest: 'institutions/basestyle/static/basestyle/',
            filter: 'isFile'
          }
        ]
      }
    },

    /**
     * watch javascript and less files for changes, when they change run the build command
    */
    watch: {
      scripts: {
        files: ['frontend/src/**/*.js','frontend/src/**/*.less'],
        tasks: ['build']
      }
    }


  }); /* end grunt.initConfig  */

  /**
   * The above tasks are loaded here (in the same order).
   */
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-autoprefixer');
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  //grunt.loadNpmTasks('grunt-topdoc');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-watch');

  /**
   * Grunt is installed in a sub-directory called "front",  so back out one directory:
  ;*/
  grunt.file.setBase('../');

  /**
   * The 'default' task will run whenever `grunt` is run without specifying a task
   */
  grunt.registerTask('build', ['concat', 'less', 'autoprefixer', 'cssmin', 'uglify', 'copy']);
  grunt.registerTask('default', ['build']);

};