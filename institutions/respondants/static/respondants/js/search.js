'use strict';

$(document).ready(function() {
    var search = new Bloodhound({
        datumTokenizer: function(d) {
            return Bloodhound.tokenizers.whitespace(d.name);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/institutions/search/?auto=1&q=%QUERY',
            filter: function(resp) { return resp.institutions;}
        }
    });
    search.initialize();

    $('#search_name').typeahead(null, {
        displayKey: 'name',
        source: search.ttAdapter()
    });
});
