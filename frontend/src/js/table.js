// The summary table is structured so that county data is contained within a tbody
// & the county's tracts are contained in an adjacent tbody. This is mainly
// done to allow for the possibility of applying the CF expandable to them (it is
// not currently applied since it requires a shared parent element, but it's possible
// that it could be adjusted to work with sibling elements without a direct parent
// expandable.)
// The tablesorter plugin, however, currently only sorts WITHIN tbodies, not between
// them.
// As per this discussion (https://github.com/Mottie/tablesorter/pull/195),
// the maintainer of the plugin is working on a widget to allow sorting between tbodies.
//
// This is an interim hack, based on the outlines of the in-development widget
// from the thread above. It should be replaced once the official widget is available.
//
// Alternatively, the county rows could be moved into the tract tbody and set to infoOnly.
// This would make the widget unnecessary, but it would also be incompatible with CF expandables.
// Instead, the display of all the tract rows would be toggled when the county was expanded.

(function($){
"use strict";
var ts = $.tablesorter;

   ts.addWidget({
       id: 'sortTbody',
       priority: 100,
       options: {
           sortTbody_primaryCell : null,
           sortTbody_type: 'Natural'
       },
       init: function(table, thisWidget, c, wo){
           var tbodies = c.$table.children('tbody:not(".tablesorter-childTbody, .tablesorter-infoOnly")');
           var tbodyChildren = {};
           tbodies.each(function (i, t) {
              var $t = $(t);
              $t.data('rowid', i);
              tbodyChildren[i] = $t.next('.tablesorter-childTbody')
           });
           c.$table
               .unbind('sortEnd.sortTbody')
               .bind('sortEnd.sortTbody', function(x){
                   var sortType = wo.sortTbody_type.toLowerCase() === 'text' ? 'sortText' : 'sortNatural';
                   var tbl = c.$table;
                   var method = 'sortNatural';
                   var sortedBy = tbl.find('th[aria-sort="ascending"], th[aria-sort="descending"]');
                   var direction = sortedBy.attr('aria-sort') == 'ascending' ? 0 : 1;
                   var colCl = $(sortedBy).data('sortclass');

                   tbodies.sort(function(a, b) {
                       var $a = $(direction ? b : a),
                           $b = $(direction ? a : b);
                       return ts[method]($a.find('tr:first ' + '.' + colCl).text(), $b.find('tr:first ' + '.' + colCl).text());
                   });
                   
                   // hide entire table to improve sort performance
                   c.$table.hide();
                   tbodies.each(function (i, t) {
                       var $t = $(t);
                       $t.appendTo(c.$table);
                       $(tbodyChildren[$t.data('rowid')]).appendTo(c.$table);
                   })
                   c.$table.show();
               });
       },
       remove : function(table, c, wo){
           c.$table.unbind('sortEnd.sortTbody');
       }
   });

})(jQuery);


  
$(document).ready(function(){
  var currentChart;
  var tableData = {};

  function getTableData(lender) {
    var params = {};
    var endpoint = '/api/tables/';
  
    // Set the lender parameter based on the current URL param
    if ( urlParam('lender') ){
      params['lender'] = urlParam('lender');
    } else {
      console.log(' Lender parameter is required.');
      return false;
    }
  
    // Set the metro parameter based on the current URL param
    if ( urlParam('metro') ){
        params.metro = urlParam('metro');
    } else {
        console.log("No metro area provided");
    }
    
    return $.ajax({
          url: endpoint, 
          data: params, 
          traditional: true,
          success: console.log('get API All Data request successful')
      }).fail( function( status ){
          console.log( 'no data was available at' + endpoint + '. status: ' + status );
      }).done( function(res){
          tableData = res['table_data'];
          prepTableData(tableData);
      });
  }

  function prepNumbers(data) {
    _.each(['lma_pct', 'mma_pct', 'hma_pct'], function (i) {
      var num = parseFloat(data[i]);
      if (!isNaN(num)) {
        data[i] = +(num * 100).toFixed(2);
      }
    });
  }
  
  function prepTableData(tableData) {
    _.each([tableData.lender, tableData.peers],function (i) {
      prepNumbers(i);
    });
    _.each(tableData.counties, function (c) {
      prepNumbers(c);
      _.each((c || {}).tracts, function (t){
        prepNumbers(t);
      })
    })
  }
  
  // Get table data
  var msaData = getTableData();

  function buildTable(showPeers) {
    msaData.done(function () {
      var template, tbl, msa;
      
      // Get table data from api response
      msa = tableData.lender;
      msa.peers = tableData.peers;
      msa.odds = tableData.odds;
      msa.counties = tableData.counties;
      msa.showPeers = showPeers;
      
      // Populate table template with table data
      _.templateSettings.variable = "msa";
      template = _.template(
        $( "script.table-template" ).html()
      );
      tbl = $(template(msa));

      // Add table to its container
      $('#table-container').append(tbl);
    })
    
  }

  function activateTable () {
    var tbl = $(".summary-data-table");
  
    // activate tablesorter plugin
    tbl.tablesorter({
      headerTemplate: '',
      widgets: [ 'sortTbody', 'stickyHeaders' ],
      widgetOptions: {
        stickyHeaders_attachTo : '#data-container'
      }
    });

    // hide tract expandables
    $('.tablesorter-childTbody').hide();

    // show tract expandables when county target is clicked
    // Note: cf-expandables will not currently work since the 
    // expandable target & content are adjacent tbodies and
    // do not have a unique common parent.
    $('.county-tbody').click(function (e) {
      var $target = $(e.target);
      var $tbody = $target.closest('tbody');
      var child = $tbody.next('.tablesorter-childTbody');
      if ($(child).is(':visible')) {
        $(child).hide();
        $tbody.find('.expandable_cue-open').show();
        $tbody.find('.expandable_cue-close').hide();
      } else {
        $(child).show();
        $tbody.find('.expandable_cue-open').hide();
        $tbody.find('.expandable_cue-close').show();
      }
    });
    
    // show table & its container
    tbl.show();
    $('#table-container').show();
  }

  function destroyData() {
    if (currentChart == 'chart-toggle__basic-table' || currentChart == 'chart-toggle__peer-table') {
      // destroy table
      $(".summary-data-table").trigger("destroy");
      $(".summary-data-table").remove();
      $('#table-container').hide();
    } else if (currentChart === 'chart-toggle__lar-chart') {
      destroyLarChart();
      $('#plot-container').hide();
    }
  }

  function hideData() {
    if (!currentChart) {return;}
    destroyData();
    showDataContainer = false;
    $('#data-container').hide();
    currentChart = null;
    setMapHeight();
  }
  
  $('.chart-toggle').click(function (e) {
    var $target = $(e.target).closest('.chart-toggle'),
    id = $target.attr('id');

    if (currentChart != id) {
      if (currentChart) {
        destroyData();
      }
      showDataContainer = true;
      if (id === 'chart-toggle__basic-table' || id === 'chart-toggle__peer-table') {
        buildTable(id === 'chart-toggle__peer-table');
        activateTable();
        $('#table-container').fadeIn();
      } else if (id === 'chart-toggle__lar-chart') {
        plotLarVolume();
        $('#plot-container').show();
      } 
      currentChart = id;
      $('#data-container').show();
      setMapHeight();
    } else {
      hideData();
    }
  });

});