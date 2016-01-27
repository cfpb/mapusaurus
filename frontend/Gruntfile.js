module.exports = function(grunt) {

  'use strict';

  var isCI = !!(process.env.JENKINS_URL || process.env.CONTINUOUS_INTEGRATION);
  
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
          'frontend/src/less/leaflet.rrose.css',
          'frontend/bower_components/leaflet-minimap/dist/Control.MiniMap.min.css'
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
          sourceMap: !isCI,
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
        compress: {},
        mangle: false,
        beautify: true,
        sourceMap: !isCI,
        sourceMapIncludeSources: !isCI
      },
      vendor: {
        src: [
          'frontend/bower_components/jquery/dist/jquery.min.js',
          'frontend/bower_components/jquery.easing/js/jquery.easing.js',
          'frontend/bower_components/typeahead/dist/typeahead.bundle.js',
          'frontend/bower_components/cf-expandables/src/js/cf-expandables.js',
          'frontend/bower_components/tooltipsy/tooltipsy.min.js',
          'frontend/bower_components/tablesorter/dist/js/jquery.tablesorter.min.js',
          'frontend/bower_components/tablesorter/dist/js/jquery.tablesorter.widgets.min.js'
        ],
        dest: 'frontend/dist/basestyle/js/vendor.min.js'
      },
      vendor_map: {
        src: [
          'frontend/bower_components/underscore/underscore.js',
          'frontend/bower_components/blockui/jquery.blockUI.js',
          'frontend/src/js/leaflet/leaflet.js',
          'frontend/bower_components/leaflet-hash/leaflet-hash.js',
          'frontend/bower_components/Leaflet.utfgrid/dist/leaflet.utfgrid.js',
          'frontend/bower_components/leaflet-rrose/rrose-src.js',
          'frontend/bower_components/numeral-js/min/numeral.min.js',
          'frontend/bower_components/leaflet-MiniMap/dist/Control.MiniMap.min.js'
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
        src: [
          'frontend/src/js/map.js',
          'frontend/src/js/minorityKey.js',
          'frontend/src/js/asyncHandlers.js',
          'frontend/src/js/drawCircles.js',
          'frontend/src/js/drawKey.js',
          'frontend/src/js/helpers.js'
        ],
        dest: 'frontend/dist/map/js/map.min.js'
      },
      table: {
        src: ['frontend/src/js/table.js'],
        dest: 'frontend/dist/map/js/table.min.js'
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
          /* Source images that were manually downloaded to the src/img folder */
          {
            expand: true,
            flatten: true,
            src: ['frontend/src/img/*'],
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
            dest: 'mapusaurus/basestyle/static/basestyle/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: 'frontend/dist/search/',
            src: ['**'],
            dest: 'mapusaurus/respondents/static/respondents/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: 'frontend/dist/map/',
            src: ['**'],
            dest: 'mapusaurus/mapping/static/mapping/',
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
