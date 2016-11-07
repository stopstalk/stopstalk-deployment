(function($) {
    "use strict";

    $(document).ready(function() {
        $.ajax({
            method: 'GET',
            url: '/default/submissions.json'
        }).done(function(page) {
            var pageCount = page['count'],
                currentUrl = window.location.href.split("/").slice(-1),
                currPage;

            if (currentUrl != "submissions") {
                currPage = currentUrl;
            } else {
                currPage = "1";
            }

            $('#solved-problems').html(page['solved_problems']);
            $('#page-selection').bootpag({
                total: pageCount,
                page: parseInt(currPage),
                maxVisible: 10
            }).on("page", function(event, num) {
                window.location.href = "/default/submissions/" + num.toString();
            });
        });
    });
})(jQuery);