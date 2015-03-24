
$(document).ready(function(){
    var pctBlack = $('#pct_blk');
    var pctBlackData = $('.pct-black-data');
    var pctHisp = $('#pct_hisp');
    var pctHispData = $('.pct-hispanic-data');
    var pctAsian = $('#pct_asian');
    var pctAsianData = $('.pct-asian-data');
    var pctWhite = $('#pct_white');
    var pctWhiteData = $('.pct-white-data');
    var pctMinority = $('#pct_min');
    var pctMinorityData = $('.pct-minority-data');
    var tractNumber = $('.tract-number');
    var tractPop = $('.tract-population');

    utfGrid.on('mouseover', function (e) {
        var d = e.data;
        if (d) {
            pctMinority.text(d.pct_minv1);
            pctMinorityData.attr('data-min', d.pct_minv1);
            pctMinorityData.css('width', ((d.pct_minv1/100)*85).toString()+'px');
            pctMinorityData.css('background-color', '#5c9897');

            pctBlack.text(d.pct_blk);
            pctBlackData.attr('data-min', d.pct_blk);
            pctBlackData.css('width', ((d.pct_blk/100)*85).toString()+'px');
            pctBlackData.css('background-color', '#7ea4be');

            pctHisp.text(d.pct_hisp);
            pctHispData.attr('data-min', d.pct_hisp);
            pctHispData.css('width', ((d.pct_hisp/100)*85).toString()+'px');
            pctHispData.css('background-color', '#c85954');
            
            pctAsian.text(d.pct_asian);
            pctAsianData.attr('data-min', d.pct_asian);
            pctAsianData.css('width', ((d.pct_asian/100)*85).toString()+'px');
            pctAsianData.css('background-color', '#ff931a');

            pctWhite.text(d.pct_white);
            pctWhiteData.attr('data-min', d.pct_white);
            pctWhiteData.css('width', ((d.pct_white/100)*85).toString()+'px');
            pctWhiteData.css('background-color', '#b9babc');

        } else {
            pctBlack.text('No Data');
            pctBlackData.data('min', 0);
            pctHisp.text('No Data');
            pctHispData.data('min', 0);
            pctAsian.text('No Data');
            pctAsianData.data('min', 0);
            pctWhite.text('No Data');
            pctWhiteData.data('min', 0);
        }
        tractNumber.text(d.tract);
        tractPop.text(d.tot_pop_et + ' Persons');

    });
});
