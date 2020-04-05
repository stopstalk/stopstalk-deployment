(function($) {
    "use strict";

    var initializeInputFields = function($search, $generalizedTagSearch) {
        var value = $search.val();
        if (value === '') {
            $generalizedTagSearch.removeAttr('disabled');
        } else {
            $generalizedTagSearch.attr('disabled', 'disabled');
            $generalizedTagSearch.val('');
        }
        $generalizedTagSearch.material_select();

        value = $generalizedTagSearch.val();
        if (value.length === 0) {
            $search.removeAttr('disabled');
        } else {
            $search.val('');
            $search.attr('disabled', 'disabled');
        }
    };

    var changeTagInputListeners = function() {
        var $search = $('#search'),
            $generalizedTagSearch = $('#generalized-tag-search');

        initializeInputFields($search, $generalizedTagSearch);

        $search.on('input', function() {
            var value = $(this).val();
            if (value === '') {
                $generalizedTagSearch.removeAttr('disabled');
            } else {
                $generalizedTagSearch.attr('disabled', 'disabled');
                $generalizedTagSearch.val('');
            }
            $generalizedTagSearch.material_select();
        });

        $generalizedTagSearch.on('change', function() {
            var value = $(this).val();
            if (value === null || value.length === 0) {
                $search.removeAttr('disabled');
            } else {
                $search.val('');
                Materialize.updateTextFields();
                $search.attr('disabled', 'disabled');
            }
        })
    };

    $(document).ready(function() {

        var curr_url = window.location.href;
        var vars = curr_url.split("?");
        var params = {
            'q': '',
            'page': '1',
            'site': '',
            'generalized_tags': '',
            'orderby': ''
        };

        var objToURL = function(obj) {
            var str = Object.keys(obj).map(function(key) {
                if (obj[key].constructor === Array) {
                    var res = [];
                    for (var i = 0; i < obj[key].length; ++i) {
                        res.push(key + '=' + obj[key][i]);
                    }
                    return res.join('&');
                } else {
                    return key + '=' + obj[key];
                }
            }).join('&');
            return str;
        };

        if (vars.length > 1) {
            vars = vars[1];
            var allVars = vars.split("&"),
                pair;
            for (var i = 0; i < allVars.length; i++) {
                pair = allVars[i].split('=');
                pair[1] = pair[1].replace(/\+/g,' ');;
                if (pair[0] === "site" || pair[0] === "generalized_tags") {
                    if (params[pair[0]].length === 0) {
                        params[pair[0]] = [pair[1]];
                    } else {
                        params[pair[0]].push(pair[1]);
                    }
                } else {
                    params[pair[0]] = pair[1];
                }
            }

            $("#search").val(params["q"]);
            $("#generalized-tag-search").val(params["generalized_tags"]);
            $("#profile-site").val(params["site"]);
            $("#orderby-problems").val(params["orderby"]);
            $("select").material_select();

            if (pair[0] === "site") {

                } else if (pair[0] === "generalized_tags") {
                } else if (pair[0] === "q") {
                    $("#search").val(pair[1]);
                }
        }

        changeTagInputListeners();

        if (window.location.href != baseURL) {
            $.ajax({
                url: '/problems/tag.json/?' + objToURL(params),
                method: 'GET'
            }).done(function(response) {
                $('#page-selection').bootpag({
                    total: response['total_pages'],
                    page: parseInt(params['page']),
                    maxVisible: 10
                }).on("page", function(event, num) {
                    var tmpParams = params;
                    tmpParams["page"] = num.toString();
                    window.location.href = "/problems/tag/?" + objToURL(tmpParams);
                });
            });
        }
    });
})(jQuery);
