'use strict';

$(document).ready(function() {
    var searchNameBox = $('#geoid'),
        msaField = $('#msa-field'),
        search = new Bloodhound({
            datumTokenizer: function(d) {
                return Bloodhound.tokenizers.whitespace(d.name);
            },
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: {
                url: '/shapes/search/?auto=1&q=%QUERY',
                filter: function(resp) {
                    return resp.geos;
                }
            }
        });

    search.initialize();

    searchNameBox
        .typeahead({ highlight: true }, {
                displayKey: 'name',
                source: search.ttAdapter()
        })
        .on('keyup', function() {
            //  Not all key changes affect the selected name
            if (searchNameBox.val() !== msaField.data('name')) {
                msaField.val('');
                $('input[type=submit]').prop('disabled', true);
            }
        })
        .on('typeahead:selected', function(ev, suggestion) {
            msaField.val(suggestion.geoid).data('name', suggestion.name);
            $('#metro-search__submit').prop('disabled', false).removeClass('btn__disabled');
        });
});

