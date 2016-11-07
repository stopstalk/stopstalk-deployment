(function($) {
    "use strict";

    $(document).ready(function() {

        $('button').click(function() {
            var thisButton = $(this),
                userID = thisButton.attr('data-userid'),
                buttonType = thisButton.attr('data-buttontype');

            if (buttonType != 'disabled') {
                if (buttonType == 'add-friend') {
                    thisButton.addClass('disabled');
                    thisButton.removeClass('waves-effect');
                    thisButton.removeClass('waves-light');
                    thisButton.attr('data-buttontype', 'disabled');
                    thisButton.attr('data-tooltip', 'Friend request pending');
                    thisButton.attr('data-userid', '');
                    $.ajax({
                        method: 'POST',
                        url: '/default/mark_friend/' + userID
                    }).done(function(response) {
                        $.web2py.flash(response);
                    });
                } else {
                    thisButton.removeClass('black');
                    thisButton.addClass('green');
                    thisButton.attr('data-buttontype', 'add-friend');
                    thisButton.attr('data-tooltip', 'Send friend request');
                    $.ajax({
                        method: 'POST',
                        url: '/default/unfriend/' + userID
                    }).done(function(response) {
                        var child = $(thisButton.children()[0]);
                        child.removeClass('fa-user-times');
                        child.addClass('fa-user-plus');
                        $.web2py.flash(response);
                    });
                }
            }
        });
    });

})(jQuery);