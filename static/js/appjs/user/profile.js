(function($) {
    "use strict";

    $(document).ready(function() {

        $('.modal-trigger').leanModal();

        $('.friends-button').click(function() {
            var thisButton = $(this),
                userID = thisButton.attr('data-user-id'),
                buttonType = thisButton.attr('data-type'),
                child = $(thisButton.children()[0]);

            if (buttonType == 'add-friend') {
                if (isLoggedIn === 'True') {
                    thisButton.removeClass('green');
                    thisButton.addClass('black');
                    thisButton.attr('data-type', 'unfriend');
                    thisButton.attr('data-tooltip', 'Unfriend');
                    child.removeClass('fa-user-plus');
                    child.addClass('fa-user-times');

                    $.ajax({
                        method: 'POST',
                        url: '/default/mark_friend/' + userID
                    }).done(function(response) {
                        $.web2py.flash(response);
                    }).error(function(httpObj, textStatus) {
                        thisButton.removeClass('black');
                        thisButton.addClass('green');
                        thisButton.attr('data-type', 'add-friend');
                        thisButton.attr('data-tooltip', 'Add friend');
                        $.web2py.flash("[" + httpObj.status + "]: Unexpected error occurred");
                    });
                } else {
                    $.web2py.flash("Login to add friend");
                }
            } else if (buttonType == 'unfriend') {
                thisButton.removeClass('black');
                thisButton.addClass('green');
                thisButton.attr('data-type', 'add-friend');
                thisButton.attr('data-tooltip', 'Add friend');
                child.removeClass('fa-user-times');
                child.addClass('fa-user-plus');

                $.ajax({
                    method: 'POST',
                    url: '/default/unfriend/' + userID
                }).done(function(response) {
                    child.removeClass('fa-user-times');
                    child.addClass('fa-user-plus');
                    $.web2py.flash(response);
                }).error(function(httpObj, textStatus) {
                    $.web2py.flash("[" + httpObj.status + "]: Unexpected error occurred");
                    $.web2py.flash("Unexpected error occurred");
                });
            }
        });
    });
})(jQuery);