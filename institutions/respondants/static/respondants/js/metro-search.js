'use strict';

$(document).ready(function() {
    var search = new Bloodhound({
        datumTokenizer: function(d) {
            return Bloodhound.tokenizers.whitespace(d.name);
        },
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/shapes/search/?auto=1&q=%QUERY',
            filter: function(resp) { return resp.geos;}
        }
    }),
        searchNameBox = $('#geoid');
    search.initialize();

    searchNameBox.typeahead({
        highlight: true
    }, {
        displayKey: 'name',
        source: search.ttAdapter()
    }).on('keydown', function() {
        $('#msa-field').val('');
        $('input[type=submit]').prop('disabled', true);
    }).on('typeahead:selected', function(ev, suggestion) {
        $('#msa-field').val(suggestion.geoid);
        $('input[type=submit]').prop('disabled', false);
    });
});

