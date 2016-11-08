(function($) {
    "use strict";

    $(document).ready(function() {
        var curr_url = window.location.href;
        var vars = curr_url.split("?");
        var params = {
            'q': '',
            'page': ''
        };

        if (vars.length > 1) {
            vars = vars[1];
            var allVars = vars.split("&");
            var firstParam = allVars[0].split("=");
            params[firstParam[0]] = firstParam[1];
            var secondParam = allVars[1].split("=");
            params[secondParam[0]] = secondParam[1];
        }

        $.ajax({
            url: '/problems/tag.json/?q=' + params['q'] + '&page=1',
            method: 'GET'
        }).done(function(response) {
            $('#page-selection').bootpag({
                total: response['total_pages'],
                page: parseInt(params['page']),
                maxVisible: 10
            }).on("page", function(event, num) {
                window.location.href = "/problems/tag/?q=" + params['q'] + "&page=" + num.toString();
            });
        });
    });

})(jQuery);