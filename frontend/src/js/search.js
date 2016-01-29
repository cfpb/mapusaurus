'use strict';

$(document).ready(function() {

    $('form.year').hide();

    $('#search-year').on('change', function() {
        var year = $(this).val();
        $('form.year').hide();
        $('form.year.' + year).show();

        var search = new Bloodhound({
            initialize: false,
            datumTokenizer: function(d) {
                return Bloodhound.tokenizers.whitespace(d.name);
            },
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: {
                url: '/institutions/search/?auto=1&year=' + year + '&q=%QUERY',
                filter: function(resp) { return resp.institutions;}
            }
        });
        
        search.initialize();
        
        $('form.year.' + year + ' .search_institution').typeahead({
            highlight: true
        }, {
            displayKey: 'formatted_name',
            source: search.ttAdapter()
        });
    });

});
