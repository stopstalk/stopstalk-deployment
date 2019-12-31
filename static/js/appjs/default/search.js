(function($) {
    "use strict";

    var getData = function() {
        if (country === "" && institute === "" && searchQuery === "") {
            return;
        }

        var $throbber = $("#view-submission-preloader").clone();
        $throbber.attr('id', 'searchPageThrobber');
        $('#user-list').html($throbber);

        $.ajax({
            url: searchURL,
            method: "GET",
            data: {country: country, institute: institute, q: searchQuery},
            success: function(resp) {
                $("#user-list").html(resp["table"]);
            },
            error: function(err) {
                $.web2py.flash("Error retrieving users");
                console.log(err);
            }
        });
    };

    $(document).ready(function() {

        getData();

        $('#searchUserForm').submit(function() {
            if ($('#searchInput').val() === '' && $("#institute option:selected").val() === '' && $("#country option:selected").val() === '') {
                $.web2py.flash('Please add search filters');
                return false;
            }
        });

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
                    $.web2py.flash(response);
                });
            }
        });
    });

})(jQuery);
