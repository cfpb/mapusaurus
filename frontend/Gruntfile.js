module.exports = function(grunt) {

  'use strict';

  grunt.initConfig({

    /**
     * Pull in the package.json file so we can read its metadata.
     */
    pkg: grunt.file.readJSON('package.json'),

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
        dest: 'frontend/dist/basestyle/css/vendor.css',
      },
      map: {
        src: [
          'frontend/bower_components/leaflet-rrose/leaflet.rrose.css'
        ],
        dest: 'frontend/dist/map/css/vendor.css',
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
          paths: ['frontend/src/less'],
          compress: false,
          sourceMap: true,
          sourceMapFilename: 'frontend/dist/basestyle/css/mapusaurus_sourcemap.css.map',
          sourceMapURL: '/static/basestyle/css/mapusaurus_sourcemap.css.map'
        },
        files: {
          'frontend/dist/basestyle/css/<%= pkg.name %>.css': ['frontend/src/less/<%= pkg.name %>.less']
        }
      }
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
          'frontend/dist/basestyle/css/<%= pkg.name %>.min.css': ['frontend/dist/basestyle/css/<%= pkg.name %>.css']
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
        beautify: true
      }
      ,
      vendor: {
        src: [
          'frontend/bower_components/jquery/dist/jquery.min.js',
          'frontend/bower_components/jquery.easing/js/jquery.easing.js',
          'frontend/bower_components/typeahead/dist/typeahead.bundle.js',
          'frontend/bower_components/cf-expandables/src/js/cf-expandables.js'
        ],
        dest: 'frontend/dist/basestyle/js/vendor.min.js'
      },
      vendor_map: {
        src: [
          'frontend/bower_components/underscore/underscore.js',
          // 'frontend/bower_components/leaflet-hash/leaflet-hash.js',
          'frontend/bower_components/leaflet-rrose/rrose-src.js',
        ],
        dest: 'frontend/dist/map/js/map-vendor.min.js'
      },
      search: {
        src: ['frontend/src/js/search.js'],
        dest: 'frontend/dist/search/js/search.min.js'
      },
      metro_search: {
        src: ['frontend/src/js/metro-search.js'],
        dest: 'frontend/dist/search/js/metro-search.min.js'
      },
      map: {
        src: ['frontend/src/js/map.js'],
        dest: 'frontend/dist/map/js/map.min.js'
      },
      map_layout: {
        src: ['frontend/src/js/map-layout.js'],
        dest: 'frontend/dist/map/js/map-layout.min.js'
      },
    },


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
            src: ['frontend/bower_components/font-awesome/fonts/*'],
            dest: 'frontend/dist/basestyle/fonts/',
            filter: 'isFile'
          },
          {
            expand: true,
            flatten: true,
            src: ['frontend/bower_components/cf-icons/src/fonts/*'],
            dest: 'frontend/dist/basestyle/fonts/',
            filter: 'isFile'
          },
          /* Source images that where manually downloaded to the src/img folder */
          {
            expand: true,
            flatten: true,
            src: ['frontend/src/img/logo_210.png'],
            dest: 'frontend/dist/basestyle/img/',
            filter: 'isFile'
          },
          {
            expand: true,
            flatten: true,
            src: ['frontend/src/img/font-awesome/*'],
            dest: 'frontend/dist/basestyle/img/font-awesome/',
            filter: 'isFile'
          },
          {
            expand: true,
            flatten: true,
            src: ['frontend/src/img/choropleth-key.svg'],
            dest: 'frontend/dist/basestyle/img/',
            filter: 'isFile'
          }
        ]
      },
      django: {
        files: [
          /* Copy the front/dist folder into the Django application's static assets folder */
          {
            expand: true,
            cwd: 'frontend/dist/basestyle/',
            src: ['**'],
            dest: 'institutions/basestyle/static/basestyle/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: 'frontend/dist/search/',
            src: ['**'],
            dest: 'institutions/respondants/static/respondants/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: 'frontend/dist/map/',
            src: ['**'],
            dest: 'institutions/mapping/static/mapping/',
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
  grunt.loadNpmTasks('grunt-contrib-cssmin');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-watch');

  /**
   * Grunt is installed in a sub-directory called "front",  so back out one directory:
  ;*/
  grunt.file.setBase('../');

  /**
   * The 'default' task will run whenever `grunt` is run without specifying a task
   */
  grunt.registerTask('build', ['concat', 'less', 'cssmin', 'uglify', 'copy']);
  grunt.registerTask('build-less', ['less', 'copy:django']);
  grunt.registerTask('default', ['build']);

};