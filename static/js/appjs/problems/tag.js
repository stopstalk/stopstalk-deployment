(function($) {
    "use strict";

    $(document).ready(function() {
        var curr_url = window.location.href;
        var vars = curr_url.split("?");
        var params = {
            'q': '',
            'page': '1',
            'site': ''
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
                if (pair[0] === "site") {
                    if (params[pair[0]].length === 0) {
                        params[pair[0]] = [pair[1]];
                    } else {
                        params[pair[0]].push(pair[1]);
                    }
                } else {
                    params[pair[0]] = pair[1];
                }
            }
        }

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