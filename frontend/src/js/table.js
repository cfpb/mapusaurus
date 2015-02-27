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
// NOTE: hack depends on data-sortclass attribute applied to table header cells in thead template.


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
    var tableData;
    var $dataContainer = $('#data-container');
    var $chartContainer = $('#plot-container');
    var $tableContainer = $('#table-container');
    
    // set up table templates
    _.templateSettings.variable = "data";
    var theadTemplate = _.template(
        $( "script.thead-template" ).html()
    );
    var rowTemplate =  _.template(
        $( "script.row-template" ).html()
    );

    // get table data from api
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
        });
    }
    
    
    // Proactively request table data to reduce lag.
    // This could be delayed until the table is actually toggled.
    var msaData = getTableData();
    
    
    
    /* Process data returned from api for display in table */
    function decimalToPercentage(val) {
        var num = parseFloat(val);
        if (!isNaN(num)) {
            return +(num * 100).toFixed(2);
        }
    }

    function prepNumbers (data) {
        _.each(['lma_pct', 'mma_pct', 'hma_pct'], function (i) {
            data[i] = decimalToPercentage(data[i]) || 0;
        });
    }

    function prepTableData(tableData) {
        msa = tableData.lender;
        msa.odds = tableData.odds;
        tableData.msa = msa;
        
        _.each([tableData.lender, tableData.peers],function (i) {
            prepNumbers(i);
        });
        _.each(tableData.counties, function (c) {
            prepNumbers(c);
            prepNumbers(c.peers);
            _.each((c || {}).tracts, function (t){
                prepNumbers(t);
                prepNumbers(t.peers);
            })
        })
    }

    

    /* Build out a table when the toggle is clicked */
    
    function createTable(showPeers) {    
        var tableData = fakeTableData();
        prepTableData(tableData);            
        var $tbl = buildTable(tableData, showPeers);
        $('#table-container').append($tbl);
        activateTable($tbl);  
        msaData.done(function (res) {
            if (!tableData) {
                tableData = res['table_data'];
                prepTableData(tableData);
            }
            var $tbl = buildTable(tableData, showPeers);
            activateTable($tbl);
        });
    }

    function activateTable ($tbl) {
        $tableContainer.append($tbl);
        activateTableSorting($tbl)
        activateExpandables($tbl);
        $tbl.show();
    }
    
    function activateTableSorting($tbl) {
        // activate tablesorter plugin
        $tbl.tablesorter({
            headerTemplate: '',
            widgets: [ 'sortTbody', 'stickyHeaders' ],
            widgetOptions: {
                stickyHeaders_attachTo : '#data-container'
            }
        });
    }
    
    function activateExpandables($tbl) {
        // hide tract expandables
        $tbl.find('.tablesorter-childTbody').hide();

        // show tract expandables when county target is clicked
        // Note: cf-expandables will not currently work since the 
        // expandable target & content are adjacent tbodies and
        // do not have a unique common parent.
        $tbl.find('.county-tbody').click(function (e) {
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
    }

    // destroy chart or table when toggled off
    function destroyData() {
        if (currentChart === 'chart-toggle__lar-chart') {
            // destroy chart
            destroyLarChart();
            $chartContainer.hide();
        } else {
            // destroy table
            $(".summary-data-table")
                    .trigger("destroy")
                    .remove();
            $tableContainer.hide();
        }
    }
    
    // show or hide data container, update showDataContainer global toggle,
    // and set map height
    function toggleDataContainer(showData) {
        showDataContainer = showData;
        $dataContainer[showData ? 'show' : 'hide']();
        setMapHeight();
    }

    /* chart/table toggle listener */
    $('.chart-toggle').click(function (e) {
        var $target = $(e.target).closest('.chart-toggle'),
            id = $target.attr('id');
        
        if (currentChart) {
            destroyData();
        }
        
        if (currentChart != id) {
            if (id === 'chart-toggle__basic-table' || id === 'chart-toggle__peer-table') {
                createTable(id === 'chart-toggle__peer-table');
                $tableContainer.show();
            } else if (id === 'chart-toggle__lar-chart') {
                plotLarVolume();
                $chartContainer.show();
            }
            currentChart = id;
            toggleDataContainer(true);
            
        } else {
            currentChart = null;
            toggleDataContainer(false);
        }        
    });
    
    /* Table Generation */
    
    // build a summary data table
    function buildTable(tableData, showPeers) {
        // create table element
        var $tbl = $('<table>', {
            class: 'summary-data-table ' + (showPeers ? 'peer-table' : 'basic-table')
        });
        
        // add thead
        var thead = buildTableHead(showPeers);
        $tbl.append(thead);
        
        // add contents
        var contents = buildTableContents(tableData, showPeers);
        $tbl.append(contents);

        return $tbl;
    }

    // returns thead html string
    function buildTableHead(showPeers) {
      return theadTemplate({showPeers: showPeers});              
    }

    // returns array of tbodies, one for the msa, and two for each county:
    // a county tbody and a county tract tbody
    function buildTableContents(tableData, showPeers) {
      var tbodies = [];

      // msa tbody
      var $msaTbody = buildTableBody('MSA');
      var msaRows = buildTableRows(tableData.msa, 'MSA', showPeers ? tableData.peers : null);
      $msaTbody.append(msaRows);
      tbodies.push($msaTbody);

      _.each(tableData.counties, function (county) {
          // county tbodies
          var $countyTbody = buildTableBody('County');
          var countyRows = buildTableRows(county, 'County', showPeers ? county.peers : null);
          $countyTbody.append(countyRows);
          tbodies.push($countyTbody);
          
          // tract tbodies
          var $tractTbody = buildTableBody('Tract');
          _.each(county.tracts, function (tract) {
              var tractRows = buildTableRows(tract, 'Tract', showPeers ? tract.peers : null);
              $tractTbody.append(tractRows);
          });
          tbodies.push($tractTbody);
      });
      return tbodies;
    }

    // returns jquery tbody element with appropriate classes for this row
    function buildTableBody(rowType) {
      // possible rowTypes are "MSA", "County", and "Tract"
      var className = rowType.toLowerCase() + '-tbody';
      // classes needed for tablesorter plugin
      if (rowType === "MSA") {
        className += " tablesorter-infoOnly";
      } else if (rowType === "Tract") {
        className += " tablesorter-childTbody";
      }

      return $('<tbody>', {class: className});
    }

    // returns array of html row strings
    // array will contain target row string
    // it will also contain peer row if peers are being shown
    function buildTableRows(data, rowType, peers) {
      var rows = [buildRow(data, rowType, 'Target', peers)];
      if (peers) {
        rows.push(buildRow(peers, rowType, 'Peers', peers));
      }
      return rows;
    }

    // returns an html string for one table row
    function buildRow(data, rowType, institutionType, peers) {
      var className;
      
      // add row & institution type information to template data
      var templateData = _.extend({
          institutionType: institutionType,
          rowType: rowType,
          showPeers: peers ? true : false
      }, data);
      // these aren't strictly necessary for underscore templates which allow
      // comparison logic
      templateData['is' + rowType] = true;
      templateData['is' + institutionType] = true;
      
      // set classes based on row type
      templateData.className = rowType.toLowerCase() + '-row ' + institutionType.toLowerCase() + '-row';
      if (institutionType === "Peers") {
        templateData.className += " tablesorter-childRow";
      }
      
      // generate table row 
      return rowTemplate(templateData);
    }
    
    
/* Generate test table data. */
var fakeTableData = function () {
    var data = {};
    data.lender = fakeRowData();
    data.odds = data.lender.odds;
    data.peers = fakeRowData();
    data.counties = fakeCountiesData();
    return data;
}

var fakeCountiesData = function () {
    var counties = [];
    for (var c = 0; c < _.random(5, 10); c ++) {
        var county = fakeRowData();
        county.peers = fakeRowData();
        var tracts = [];
        for (var t = 0; t < _.random(5, 10); t ++) {
            var tract = fakeRowData();
            tract.peers = fakeRowData();
            tracts.push(tract);
        }
        county.tracts = tracts;
        counties.push(county);
    }

    return counties;
}

var fakeRowData = function () {
    var mma_pct = _.random(1, 5) / 10;
    var lma_pct = _.random(1, 5) / 10;
    var hma_pct = 1 - (mma_pct + lma_pct);
    var pop = _.random(1000, 10000)
    return {
        geoid: _.random(100000, 900000),
        lma: parseInt(pop * lma_pct),
        mma: parseInt(pop * mma_pct),
        hma: parseInt(pop * hma_pct),
        lma_pct: lma_pct,
        mma_pct: mma_pct,
        hma_pct: hma_pct,
        odds: _.random(0, 75)/ 10
    }
}

});