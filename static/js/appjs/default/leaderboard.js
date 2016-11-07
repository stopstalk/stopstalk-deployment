(function($) {
    "use strict";

    var getVars = function() {
        // @Todo: Better and generalised way to do this?
        var url = window.location.href,
            params = url.split('?'),
            finalObject = {},
            param;

        if (params.length == 1) {
            return {};
        }

        params = params.splice(-1)[0];
        params = params.split('&');
        $.each(params, function(key, value) {
            param = value.split('=');
            finalObject[param[0]] = param[1];
        });
        return finalObject;
    };

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
            var parameterString = "";
            $.each(params, function(key, value) {
                parameterString += key + '=' + value + '&';
            });
            window.location.href = currentURL.split('?')[0] + '?' + parameterString.slice(0, -1);
        });
    });
})(jQuery);