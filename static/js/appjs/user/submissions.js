(function($) {
    "use strict";

    $(document).ready(function() {
        var currentURL = window.location.href,
            handle,
            page,
            index;

        index = currentURL.indexOf("=");
        if (index == -1) {
            page = "1";
        } else {
            page = currentURL.slice(index + 1);
        }

        $.ajax({
            method: 'GET',
            url: submissionsJSON + "?page=" + page
        }).done(function(response) {

            var pageCount = response['page_count'];
            $('#page-selection').bootpag({
                total: pageCount,
                page: parseInt(page),
                maxVisible: 10
            }).on("page", function(event, num) {
                window.location.href = submissionsURL + "?page=" + num.toString();
            });

        });
    });

})(jQuery);
