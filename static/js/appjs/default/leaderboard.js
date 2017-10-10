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

        $('#leaderboard-switch').click(function() {
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

        $('#custom-users-modal').modal({
            complete: function() {
                $('#custom-users-list').html('');
                $('#custom-users-modal-header').html(headerPlaceHolder);
            }
        });

        $('.custom-user-count').click(function() {
            var placeholder = $('#custom-users-modal-header').html(),
                $this = $(this);
            $('#custom-users-modal-header').html(headerPlaceHolder + $this.data("stopstalk-handle"));
            $('#custom-users-modal').modal('open');

            $.ajax({
                url: getCustomUserURL,
                method: 'GET',
                data: {'stopstalk_handle': $this.data('stopstalk-handle')},
                success: function(response) {
                    $('#custom-users-list').html(response["content"]);
                },
                error: function(err) {
                    $.web2py.flash("Something went wrong");
                }
            })
        });
    });
})(jQuery);