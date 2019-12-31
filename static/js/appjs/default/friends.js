(function($) {
    "use strict";

    $(document).ready(function() {
        $(document).on('click', 'button', function() {
            var thisButton = $(this),
                userID = thisButton.attr('data-userid'),
                buttonType = thisButton.attr('data-buttontype'),
                child = $(thisButton.children()[0]);

            if (buttonType == 'add-friend') {
                thisButton.addClass('black');
                thisButton.removeClass('green');
                thisButton.attr('data-buttontype', 'unfriend');
                thisButton.attr('data-tooltip', 'Unfriend');
                child.removeClass('fa-user-plus');
                child.addClass('fa-user-times');

                $.ajax({
                    method: 'POST',
                    url: '/default/mark_friend/' + userID
                }).done(function(response) {
                    $('.tooltipped').tooltip();
                    $.web2py.flash(response);
                });
            } else if (buttonType == 'unfriend') {
                thisButton.removeClass('black');
                thisButton.addClass('green');
                thisButton.attr('data-buttontype', 'add-friend');
                thisButton.attr('data-tooltip', 'Add friend');
                child.removeClass('fa-user-times');
                child.addClass('fa-user-plus');

                $.ajax({
                    method: 'POST',
                    url: '/default/unfriend/' + userID
                }).done(function(response) {
                    $('.tooltipped').tooltip();
                    $.web2py.flash(response);
                });
            }
        });
    });

})(jQuery);
