(function($) {
    "use strict";

    var getArgument = function() {
        var url = window.location.href;
        var tempElement = document.createElement("a");
        tempElement.href = url;
        var path = tempElement.pathname;
        var argument = path.split("/").splice(-1);
        if (argument[0] == "filters" || argument[0] == "") {
            return "1";
        }
        return argument[0];
    };

    var getVars = function() {
        var qs = document.location.search;
        qs = qs.split("+").join(" ");
        var params = {},
            tokens,
            re = /[?&]?([^=]+)=([^&]*)/g;

        while (tokens = re.exec(qs)) {
            var tmp = decodeURIComponent(tokens[1]);
            if (params[tmp] === undefined) {
                params[tmp] = decodeURIComponent(tokens[2]);
            } else {
                /* Multiple values for a parameter */
                if (params[tmp].constructor != Array) {
                    params[tmp] = [params[tmp]];
                }
                params[tmp].push(decodeURIComponent(tokens[2]));
            }
        }
        return params;
    }

    $(document).ready(function() {
        $('#submission-switch').click(function() {
            var global = this.checked;
            var redirectURL = null;
            var params = getVars();
            var currentURL = window.location.href;
            if (global) {
                params['global'] = 'True';
            } else {
                params['global'] = 'False';
            }
            window.location.href = currentURL.split('?')[0] + '?' + $.param(params);
        });

        $('.datepicker').pickadate({
            selectMonths: true, // Creates a dropdown to control month
            selectYears: 10,
            format: 'yyyy-mm-dd',
            min: new Date(2013, 0, 1),
            max: new Date(),
            closeOnSelect: true
        });

        $('select').material_select();

        var currPage = getArgument();
        var totalPages = $('#total-pages').html();
        if (totalPages == "0") {
            totalPages = "1";
        }

        $('#page-selection').bootpag({
            total: parseInt(totalPages),
            page: parseInt(currPage),
            maxVisible: 10
        }).on("page", function(event, num) {
            window.location.href = "/default/filters/" +
                num.toString() +
                "?" +
                window.location.href.split("?").splice(-1);
        });
    });
})(jQuery);