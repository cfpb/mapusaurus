var tableData = fakeTableData();
prepTableData(tableData);            
var $tbl = buildTable(tableData, showPeers);
$('#table-container').append($tbl);
activateTable($tbl);

    
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