(function($) {
    "use strict";

    $(document).ready(function() {

        $('.modal-trigger').leanModal();

        $('.friends-button').click(function() {
            var thisButton = $(this),
                userID = thisButton.attr('data-user-id'),
                buttonType = thisButton.attr('data-type');

            if (buttonType != 'disabled') {
                if (buttonType == 'add-friend') {
                    if (isLoggedIn === 'True') {
                        thisButton.addClass('disabled');
                        thisButton.removeClass('waves-effect');
                        thisButton.removeClass('waves-light');
                        thisButton.attr('data-type', 'disabled');
                        thisButton.attr('data-tooltip', 'Friend request pending');
                        thisButton.attr('data-user-id', '');
                        $.ajax({
                            method: 'POST',
                            url: '/default/mark_friend/' + userID
                        }).done(function(response) {
                            $.web2py.flash(response);
                        }).error(function(httpObj, textStatus) {
                            thisButton.removeClass('disabled');
                            thisButton.addClass('green');
                            thisButton.attr('data-type', 'add-friend');
                            thisButton.attr('data-tooltip', 'Send friend request');
                            $.web2py.flash("[" + httpObj.status + "]: Unexpected error occurred");
                        });
                    } else {
                        $.web2py.flash("Login to send friend request");
                    }
                } else {
                    thisButton.removeClass('black');
                    thisButton.addClass('green');
                    thisButton.attr('data-type', 'add-friend');
                    thisButton.attr('data-tooltip', 'Send friend request');
                    $.ajax({
                        method: 'POST',
                        url: '/default/unfriend/' + userID
                    }).done(function(response) {
                        var child = $(thisButton.children()[0]);
                        child.removeClass('fa-user-times');
                        child.addClass('fa-user-plus');
                        $.web2py.flash(response);
                    }).error(function(httpObj, textStatus) {
                        $.web2py.flash("Unexpected error occurred");
                    });
                }
            }
        });

    });
})(jQuery);