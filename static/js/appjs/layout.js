(function($) {
    "use strict";

    /* Handle the case of single digit in a time stamp */
    var formatTimeStamp = function(num) {
        var strnum = num.toString();

        return strnum.length == 1 ? '0' + strnum : strnum;
    };

    /* Transform the timestamps from IST to client browser timestamp */
    var transformTimestamps = function() {
        var clientOffset = new Date().getTimezoneOffset() * 60 * 1000;
        var ISTOffset = -330 * 60 * 1000;
        var convertedTimestamp, ISTTimestamp, d;

        $('.stopstalk-timestamp').each(function(i, td) {
            ISTTimestamp = new Date(td.textContent.replace(/-/g, '/')).getTime();
            d = new Date(ISTTimestamp + ISTOffset - clientOffset);
            convertedTimestamp = [d.getFullYear(),
                d.getMonth() + 1,
                d.getDate()
            ].map(formatTimeStamp).join('-') + " " + [d.getHours(),
                d.getMinutes(),
                d.getSeconds()
            ].map(formatTimeStamp).join(':');
            $(this).html(convertedTimestamp);
        });
    };

    /* Download a submission as a file */
    var downloadSubmission = function(fileName, text) {
        var element = document.createElement('a');

        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', fileName);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    /* Copy the code to the clipboard */
    var copyToClipBoard = function(copyText) {
        var textField = document.createElement('textarea');

        textField.innerHTML = copyText;
        document.body.appendChild(textField);
        textField.select();
        document.execCommand("copy");
        textField.remove();

        $.web2py.flash("Copied to Clipboard");
    };

    /* Escape characters in html to be representable as string */
    var htmlifySubmission = function(solutionCode) {
        return solutionCode.replace(/&/g, "&amp;")
            .replace(/>/g, "&gt;")
            .replace(/</g, "&lt;")
            .replace(/"/g, "&quot;").trim(' ');
    };

    $(document).ready(function() {

        var $viewDownloadButton = $('#final-view-download-button'),
            $downloadButton = $('#final-download-button'),
            $downloadModal = $('#download-submission-modal'),
            $viewFileName = $('#view_download_file_name'),
            $viewPreLoader = $('#view-submission-preloader'),
            $viewPre = $('#view-submission-pre'),
            $viewModal = $('#view-submission-modal'),
            $linkToSite = $('#link-to-site');

        transformTimestamps();

        $('.collapsible').collapsible({
            accordion: false // A setting that changes the collapsible behavior to expandable instead of the default accordion style
        });

        $('select').material_select();

        $('.tooltipped').tooltip({
            delay: 50
        });

        // Remove focus from any focused element
        if (document.activeElement) {
            document.activeElement.blur();
        }

        $(document).on('click', '.view-submission-button', function() {
            var site = $(this).data('site');
            var viewLink = $(this).data('view-link');

            var onViewModalClose = function() {
                $viewDownloadButton.addClass('disabled');
                $viewFileName.val('');
                $viewPreLoader.removeClass('hide');
                $viewPre.addClass('hide');
                $viewPre.removeClass('prettyprint');
                $viewPre.removeClass('prettyprinted');
                $viewPre.html('');
                $('#copy-to-clipboard').addClass('hide');
                $linkToSite.html('');
                $linkToSite.attr('href', '');
            };

            $linkToSite.html('View on ' + site);
            $linkToSite.attr('href', viewLink);

            $viewModal.openModal({
                complete: onViewModalClose
            });

            $.ajax({
                method: 'GET',
                url: '/default/download_submission',
                data: {
                    site: site,
                    viewLink: viewLink
                }
            }).done(function(response) {
                var solutionText;

                $viewPreLoader.addClass('hide');
                $viewPre.removeClass('hide');

                $('#copy-to-clipboard').removeClass('hide');

                if (response != -1) {
                    solutionText = htmlifySubmission(response);
                } else {
                    solutionText = "// Unable to retrieve submission from " + site + "\n" + "/* Possible reasons :-\n\t * The submission is from an ongoing contest\n\t * There was some error from our side. \n\t   Please write to us (https://www.stopstalk.com/contact_us)\n */";
                }

                $viewPre.html(solutionText);
                $viewModal.one('click', '#copy-to-clipboard', function() {
                    if (response != -1) {
                        copyToClipBoard(response);
                    } else {
                        copyToClipBoard(solutionText);
                    }
                });

                $viewPre.addClass('prettyprint');
                PR.prettyPrint();
                if (response != -1) {
                    $viewDownloadButton.removeClass('disabled');
                    $viewFileName.on('keydown', function() {
                        if (event.which == 13) {
                            $('#final-view-download-button').trigger('click');
                        }
                    });

                    $(document).one('click', '#final-view-download-button', function() {
                        var fileName = $viewFileName.val();
                        if (fileName) {
                            downloadSubmission(fileName, response);
                            $viewModal.closeModal();
                            onViewModalClose();
                        } else {
                            $.web2py.flash("Please enter a file name");
                        }
                    });
                } else {
                    $.web2py.flash("Unable to Download");
                }
            });
        });

        $(document).on('click', '.download-submission-button', function() {
            var site = $(this).data('site');
            var viewLink = $(this).data('view-link');

            var onDownloadModalClose = function() {
                /* Callback function on Modal close */
                $downloadButton.addClass('disabled');
                $('#file_name').val('');
            };

            $downloadModal.openModal({
                complete: onDownloadModalClose
            });

            $.ajax({
                method: 'GET',
                url: '/default/download_submission',
                data: {
                    site: site,
                    viewLink: viewLink
                }
            }).done(function(response) {
                if (response != -1) {
                    $downloadButton.removeClass('disabled');
                    $('#file_name').on('keydown', function() {
                        if (event.which == 13) {
                            $('#final-download-button').trigger('click');
                        }
                    });

                    $(document).one('click', '#final-download-button', function() {
                        var fileName = $('#file_name').val();
                        if (fileName) {
                            downloadSubmission(fileName, response);
                            $downloadModal.closeModal();
                            onDownloadModalClose();
                        } else {
                            $.web2py.flash("Please enter a file name");
                        }
                    });
                } else {
                    $.web2py.flash("Unable to Download");
                }
            });
        });
    });
})(jQuery);