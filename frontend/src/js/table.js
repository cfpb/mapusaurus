var theadTemplate,
    rowTemplate,
    tableData,
    currentChart,
    msaData;

$(document).ready(function () {
    // Set up underscore table templates.
    _.templateSettings.variable = "data";
    theadTemplate = _.template(
        $( "script.thead-template" ).html()
    );
    rowTemplate =  _.template(
        $( "script.row-template" ).html()
    );
    
    // Create/destroy table when chart toggle is clicked.
    $('.chart-toggle').click(function (e) {
        var $target = $(e.target).closest('.chart-toggle'),
            id = $target.attr('id');
        
        $('.chart-toggle').removeClass('active-layer');
        $target.addClass('active-layer');

        if (currentChart) {
            destroyData();
        }

        if (currentChart != id) {

            createTable(id === 'chart-toggle__peer-table');
            $('#table-container').show();

            currentChart = id;
            toggleDataContainer(true);

        } else {
            currentChart = null;
            toggleDataContainer(false);
            $('.chart-toggle').removeClass('active-layer');
        }        
    });

});

/**
 * @name getTableData
 *
 * @description Gets 'lender' and 'metro' params from URL,
 * and uses them to construct a request for table data from
 * table api endpoint.
 *
 * @return {obj} $.ajax promise
 * 
 * 
 */
function getTableData() {
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
        url: '/api/tables/', 
        data: params, 
        traditional: true,
        success: console.log('get API All Data request successful')
    }).fail( function( status ){
        console.log( 'no data was available at' + endpoint + '. status: ' + status );
    });
}

/**
 * @name createTable
 *
 * @description Makes request for table data if has 
 * not already been initiated. When table data is returned,
 * preps table data, builds & activates table, and
 * appends table to DOM.
 *
 * @params {boolean} showPeers indicates whether peer value
 * rows should be shown in table
 * 
 * 
 */

function createTable(showPeers) {
    msaData || (msaData = getTableData()); 
    msaData.done(function (res) {
        if (!tableData) {
          tableData = res;
          prepTableData(tableData);
        }
        var $tbl = buildTable(tableData, showPeers);
        activateTable($tbl);
        $('#tableLoadImage').hide();
        $tbl.appendTo($('#table-container')).show();

        $('#closeTable').on('click', function(){
            toggleDataContainer(false);
            currentChart = 'undefined';  
            $('.chart-toggle').removeClass('active-layer');
        });
        generateTooltips('#table-container', [0,-1]);
    });
}

/**
 * @name prepTableData
 *
 * @description Preps table data for display.
 * Processes MSA object & each county object in 
 * county array. Converts their '_pct' values from 
 * decimals, and pulls their '_peer' values into a peerData object.
 *
 * @params {obj} data table data object to process
 * @return {obj} processed data object
 * 
 */
function prepTableData(data) {
    var msa = data.msa;
    _.extend(msa, prepNumbers(msa));
    msa.peerData = getPeerData(msa);
    
    _.each(data.counties, function (county, key) {
        _.extend(county, prepNumbers(county));
        county.peerData = getPeerData(county);
        county.geoid = key;
    });
    
    return data;
}

/**
 * @name decimalToPercentage
 *
 * @description converts decimals to percentages
 *
 * @params {number|string} val decimal value to convert
 * @return {number|null} number in percentage format
 * 
 * 
 */
function decimalToPercentage(val) {
    var num = parseFloat(val);
    if (!isNaN(num)) {
        return +(num * 100).toFixed(2);
    }
}

/**
 * @name prepNumbers
 *
 * @description Checks an object for properties ending with '_pct',
 * and then converts those properties from decimal to percentage.
 *
 * @params {obj} data object containing converted values
 * 
 * 
 */
function prepNumbers(data) {
    var obj = {},
        suffix = '_pct',
        len = suffix.length;
    
    _.each(data, function (val, key) {        
        if (key.indexOf(suffix, key.length - len) !== -1) {
            obj[key] = decimalToPercentage(val) || 0;
        }
    });
    
    return obj;
}

/**
 * @name getPeerData
 *
 * @description Returns an object containing all the properties
 * on an object that start with 'peer_'.
 *
 * @params {obj} data object to be searched for peer values
 * @return {obj} object containing all peer properties
 * 
 */
function getPeerData(data) {
    var peerData = {isPeer: true};
        
    _.each(data, function (val, key) {
        var strs = key.split('_');
        if (strs[0] === 'peer') {
            peerData[strs.slice(1).join('_')] = val;
        }
    });

    return peerData;
}


/* Table Generation */

/**
 * @name buildTable
 *
 * @description Builds a table.
 *
 * @params {obj} tableData data to use in table
 * @params {boolean} showPeers whether to show peer rows in table
 * @return {obj} jquery table object
 * 
 */
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

/**
 * @name buildTableHead
 *
 * @description Builds thead using theadTemplate.
 *
 * @params {boolean} showPeers whether to show peer rows in table
 * @return {str} theadTemplate content string
 * 
 */
function buildTableHead(showPeers) {
  return theadTemplate({showPeers: showPeers});              
}

/**
 * @name buildTableContents
 *
 * @description Build contents for table. 
 * Generates one tbody containing row(s) for the MSA data. 
 * The MSA tbody needs to be separate so the MSA rows 
 * won't be sorted with the counties.
 *
 * Also generates a tbody containing rows for all the counties.
 *
 * @params {obj} tableData data for table
 * @params {boolean} showPeers whether to show peer rows in table
 * @return {array} array of tbodies for table 
 * 
 */
function buildTableContents(tableData, showPeers) {
    var tbodies = [];
    
    var msaRows = buildTableRows(tableData.msa, 'MSA', showPeers);
    var $msaBody = $('<tbody>', {class: 'tablesorter-infoOnly'});
    $msaBody.append(msaRows);
    tbodies.push($msaBody);
    
    var $countyBody = $('<tbody>');
    _.each(tableData.counties, function (county) {
        var countyRows = buildTableRows(county, 'County', showPeers);
        $countyBody.append(countyRows);
    });
    tbodies.push($countyBody);
    
    return tbodies;
}


/**
 * @name buildTableRows
 *
 * @description Build table row(s) for a county or for MSA. 
 * Generates one row for the target institution. If showPeers
 * is true, also generates a row for the peer data.
 *
 * @params {obj} tableData data for table
 * @params {str} rowType either MSA or County
 * @params {boolean} showPeers whether to show peer rows in table
 * @return {array} array of html row strings for this MSA or County 
 * 
 */
function buildTableRows(data, rowType, showPeers) {
  var rows = [buildRow(data, rowType, showPeers)];
  
  if (showPeers) {
     rows.push(buildRow(data.peerData, rowType, showPeers));
  }
  
  return rows;
}

// returns an html string for one table row

/**
 * @name buildRow
 *
 * @description Builds a single table row. 
 * Generates classes for row based on row type:
 * peer or target institution, and MSA or County.
 *
 * @params {obj} tableData data for table
 * @params {str} rowType either MSA or County
 * @params {boolean} showPeers whether to show peer rows in table
 * @return {str} html string for one table row
 * 
 */
function buildRow(data, rowType, showPeers) {
  var className, 
      templateData;
  
  // add row & institution type information to template data
  templateData = _.extend({
      rowType: rowType,
      showPeers: showPeers
  }, data);
  
  // set classes based on row type
  templateData.className = rowType.toLowerCase() + '-row ';

  if (data.isPeer) {
      // peer rows are sorted with the preceding target institution
      // row, so they need the 'tablesorter-childRow' class.
      templateData.className += ' peer-row tablesorter-childRow';
  } else {
      templateData.className += ' target-row';
  }
  
  // generate table row 
  return rowTemplate(templateData);
}

/**
 * @name activateTable
 *
 * @description Activates table plugins.
 *
 * @params {obj} $tbl jQuery table object
 * @return {obj} $tbl
 * 
 */
function activateTable($tbl) {
    // Activate tablesorter plugin
    return $tbl.tablesorter({
        headerTemplate: '',
        widgets: [ 'stickyHeaders' ],
        widgetOptions: {
            stickyHeaders_attachTo : '#data-container'
        }
    });
}

/**
 * @name destroyData
 *
 * @description Checks for type of current chart,
 * and then calls either the table or LAR chart
 * destroy function & hides the appropriate container
 * element.
 * 
 */
function destroyData() {
    // destroy table        
    destroyTable();
    $('#table-container').hide();
    setMapHeight();

}

/**
 * @name destroyTable
 *
 * @description Triggers 'destroy' event
 * on table for tableSorter plugin, then removes
 * table from DOM.
 * 
 */
function destroyTable() {
    $(".summary-data-table")
        .trigger("destroy")
        .remove();
    
    setMapHeight();        
}

/**
 * @name toggleDataContainer
 *
 * @description Updates showDataContainer global, shows or hides
 * the data & table containers, and calls setMapHeight to update
 * map & data container heights.
 *
 *
 * @params {boolean} showData whether to show or hide data container
 *
 */
function toggleDataContainer(showData) {
    showDataContainer = showData;
    if (showData) {
        $('#data-container').show();
        $('#data-container-sizer').show();
    } else {
        $('#data-container').hide();
        $('#data-container-sizer').hide();
    }
    setMapHeight();
}


// Helper function to check Odds class
function getOddsClass( ratio ){
    var oddsClass = 'odds-normal';
    if( 0 < ratio && ratio <= .4 || ratio === 0 ){
        oddsClass = 'odds-warning';
    } else if ( .4 < ratio && ratio < .8 ){
        oddsClass = 'odds-caution';
    } else {
        oddsClass = 'odds-normal';
    }
    return oddsClass;
}