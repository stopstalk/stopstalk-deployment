(function($) {
    "use strict";

    var handleSubmissionsPagination = function() {
        $.ajax({
            method: 'GET',
            url: pageURL + '.json'
        }).done(function(page) {
            var pageCount = page['count'],
                currentUrl = window.location.href.split("/").slice(-1),
                currPage;

            if (currentUrl != "submissions") {
                currPage = currentUrl;
            } else {
                currPage = "1";
            }

            $('#page-selection').bootpag({
                total: pageCount,
                page: parseInt(currPage),
                maxVisible: 10
            }).on("page", function(event, num) {
                window.location.href = pageURL + '/' + num.toString();
            });
        });
    };

    $(document).ready(function() {
        handleSubmissionsPagination();
    });
})(jQuery);
