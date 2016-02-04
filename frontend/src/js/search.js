$(document).ready(function() {

    var $typeahead = $('#institutions_search input.search_institution');
    var $year = $('#search-year');
    var selectedYear = getYear();
    
    initTypeahead();

    $year.on('change', function() {
        selectedYear = getYear();
        $typeahead.typeahead('destroy');
        $typeahead.val('');
        initTypeahead();
    });

    function getYear() {
        return parseInt($year.val());
    }

    function initTypeahead() {
        var search = new Bloodhound({
            initialize: false,
            datumTokenizer: function(d) {
                return Bloodhound.tokenizers.whitespace(d.name);
            },
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: {
                url: '/institutions/search/?auto=1&year=' + selectedYear + '&q=%QUERY',
                filter: function(resp) { return resp.institutions; }
            }
        });

        search.initialize();

        $('#institutions_search').find('#search_year').val(selectedYear);
        $typeahead.typeahead({
            highlight: true
        }, {
            displayKey: 'formatted_name',
            source: search.ttAdapter()
        });
    }

});
