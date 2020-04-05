var setEditorialVoteEventListeners = function() {
    $(document).on('click', '.love-editorial', function() {
        var $this = $(this),
            $loveCount = $($this.siblings()[0]),
            $heartIcon = $this.children()[0];
        if ($heartIcon.classList.contains('red-text')) {
            $.web2py.flash('Already voted the editorial');
        } else {
            if (isLoggedIn === false) {
                $.web2py.flash('Please login to cast your vote');
            } else {
                $.ajax({
                    url: loveEditorialURL + '/' + $(this).data()['id'],
                    method: 'POST',
                    success: function(response) {
                        $loveCount.html(response['love_count']);
                        $heartIcon.classList.add('red-text');
                        $.web2py.flash('Vote submitted');
                    },
                    error: function(response) {
                        if (response.status === 401) {
                            $.web2py.flash('Please login to cast your vote');
                        } else {
                            $.web2py.flash('Error submitting your vote');
                        }
                    }
                });
            }
        }
    });
};

var initTooltips = function() {
    $('.tooltipped').tooltip({
        delay: 50
    });
};

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

    /* Get a url parameter by the key from a string url */
    var getParameterByName = function (name, url) {
        if (!url) {
          url = window.location.href;
        }
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    };

    var markPulseButtonClick = function(elementID, key) {
        if (isLoggedIn && !clickedButton[key]) {
            $.ajax({
                url: markReadURL,
                data: {key: key},
                success: function() {
                    clickedButton[key] = true;
                    $('#' + elementID).removeClass('pulse');
                }
            });
        }
    };

    var problemDifficultyResponseHandler = function(response) {
        if(response["score"]) $(".difficulty-list-item input[value='" + response["score"] + "']").prop("checked", true);
        $("#problem-difficulty-modal-form").attr("data-problem", response["problem_id"]);
    };

    var getNextProblem = function(explicitClick, problemId) {
        explicitClick = explicitClick || false;
        problemId = problemId || null;

        if(explicitClick) $('#problem-difficulty-modal-form').trigger('reset');

        $.ajax({
            url: getNextProblemURL,
            method: 'GET',
            data: {problem_id: problemId},
            success: function(response) {
                if(response["result"] == "all_caught") {
                    $('#problem-difficulty-actual-content').addClass("hide");
                    $('#problem-difficulty-all-caught-up').removeClass("hide");
                } else {
                    $('#problem-difficulty-actual-content').removeClass("hide");
                    $('#problem-difficulty-all-caught-up').addClass("hide");
                    $('#problem-difficulty-title').html("How difficult is " + response["plink"] + "?");
                    problemDifficultyResponseHandler(response);
                }
                $('#problem-difficulty-modal').modal('open');
                problemDifficultyModalOpen = true;
            },
            error: function(e) {
                console.log("Failed to get the next problem", e);
            }
        });
    };

    var openProblemDifficultyModal = function(explicitClick, problemId) {
        var cacheValue = localStorage.getItem("lastShowedProblemDifficulty");
        if (!isLoggedIn ||
            (cacheValue &&
             (Date.now() - cacheValue < 72 * 60 * 60 * 1000) && !explicitClick)) {
            // Modal showed less than 72 hours before;
            return;
        }

        getNextProblem(explicitClick, problemId);
    };

    var initProblemDifficultySubmitHandler = function() {
        $(document).on("change", "input[type=radio][name=problem_difficulty_value]", function() {
            var $thisForm = $('#problem-difficulty-modal-form'),
                $thisTitle = $('#problem-difficulty-title'),
                $thisProblemLink = $("#problem-details-link");

            $.ajax({
                method: 'POST',
                url: problemDifficultySubmitURL + '.json',
                data: {
                    "score":  $("input[name='problem_difficulty_value']:checked").val(),
                    "problem_id": $("#problem-difficulty-modal-form").attr("data-problem")
                },
                success: function(response) {
                    if(response["result"] == "all_caught") {
                        $('#problem-difficulty-actual-content').addClass("hide");
                        $('#problem-difficulty-all-caught-up').removeClass("hide");
                        return;
                    }
                    setTimeout(function() {
                        $('#problem-difficulty-actual-content').removeClass("hide");
                        $('#problem-difficulty-all-caught-up').addClass("hide");
                        problemDifficultyResponseHandler(response);
                        $('#problem-difficulty-modal-submit-button').val('Submit');
                        $('#problem-difficulty-modal-submit-button').removeClass('disabled');

                        $thisForm.trigger('reset');

                        $thisForm.fadeOut(function() {
                            $thisForm.fadeIn();
                        });

                        $thisTitle.fadeOut(function() {
                            $thisTitle.html("How difficult is " + response["plink"] + "?");
                            $thisTitle.fadeIn();
                        });
                    }, 100);
                },
                error: function(err) {
                    console.log(err);
                }
            });
            e.preventDefault();
        });
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

        $("#welcome a").on('touchend', function(){
            window.location.href = $(this).attr('href');
        });

        $('.collapsible').collapsible({
            accordion: false // A setting that changes the collapsible behavior to expandable instead of the default accordion style
        });

        $('select').material_select();

        $('#problem-difficulty-modal').modal({
            dismissible: true,
            complete: function() {
                localStorage.setItem("lastShowedProblemDifficulty", Date.now());
                problemDifficultyModalOpen = false;
            }
        });

        $(document).on('click', '#problem-difficulty-title .problem-listing', function() {
            localStorage.setItem("lastShowedProblemDifficulty", Date.now());
        });

        $(document).on('click', '#skip-this-problem', function() {
            getNextProblem(true);
        });

        initTooltips();

        if(loggedInUserId < thresholdUserId)  openProblemDifficultyModal();

        initProblemDifficultySubmitHandler();

        $(document).on('click', '#explain-problem-difficulty', function() {
            if (!isLoggedIn) {
                $.web2py.flash("Login to suggest problem difficulty!");
                return;
            } else {
                showProblemDifficultyOnboarding = "False";
                openProblemDifficultyModal(true);
                $.ajax({
                    url: markReadURL,
                    data: {key: "problem_difficulty"}
                });
            }
        });

        $(document).on('click', '#problem-page-difficulty-button', function() {
            openProblemDifficultyModal(true, problemId);
            $("#problem-difficulty-modal-form").attr("data-problem", problemId);
        });

        $('#open-side-nav').click(function() {
            if (typeof ga !== 'undefined') {
                ga('send', {
                    hitType: 'event',
                    eventCategory: 'button',
                    eventAction: 'click',
                    eventLabel: 'Open Side Navbar'
                });
            }
        });

        $('#open-side-nav').sideNav();

        // Remove focus from any focused element
        if (document.activeElement) {
            document.activeElement.blur();
        }

        var todoTrSelectors = ".submissions-table tr," +
                              ".user-editorials-table tr," +
                              "#problem-setter-page-table tr," +
                              "#problem-response tr," +
                              ".trendings-html-table tr," +
                              ".todo-list-icon";

        $(document).on('mouseenter', todoTrSelectors, function() {
            var todoIcon = $(this).find('.add-to-todo-list');
            todoIcon.css("display", "inline-flex");
        });

        $(document).on('mouseleave', todoTrSelectors, function() {
            var todoIcon = $(this).find('.add-to-todo-list');
            todoIcon.hide();
        });

        $(document).on('click', '.add-to-todo-list', function() {
            var stopstalkLink = this.parentElement.firstChild["href"],
                problemLink = getParameterByName("plink", stopstalkLink),
                thisElement = this,
                $thisElement = $(this),
                problemId = $thisElement.data()["pid"];
            $.ajax({
                url: addTodoURL,
                method: 'POST',
                data: {pid: problemId},
                success: function(response) {
                    var tooltipID = thisElement.getAttribute("data-tooltip-id");
                    $thisElement.remove();
                    $('#' + tooltipID).remove();
                    $.web2py.flash(response);
                },
                error: function(e) {
                    $.web2py.flash("Some error occurred");
                }
            });
        });

        $(document).on('click', '.delete-editorial', function() {
            var result = confirm("Are you sure you want to DELETE the editorial ?")
            if(!result) return;
            var $this = $(this);
            $.ajax({
                url: deleteEditorialURL + '/' + $this.data('id'),
                method: 'POST',
                success: function(response) {
                    if (response === "SUCCESS") {
                        $this.parent().parent().fadeOut();
                        $.web2py.flash("Editorial deleted successfully!");
                    } else {
                        $.web2py.flash("Can't delete accepted Editorial!");
                    }
                },
                error: function(err) {
                    $.web2py.flash("Something went wrong!");
                }
            });
        });

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

            $viewModal.modal({
                complete: onViewModalClose
            });

            $viewModal.modal('open');

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
                    solutionText = "// Unable to retrieve submission from " + site + "\n" + "/* Possible reasons :-\n\t * " + site + " is down\n\t * The submission is from an ongoing contest\n\t * There was some error from our side. \n\t   Please write to us (https://www.stopstalk.com/contact_us)\n */";
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
                            $viewModal.modal('close');
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

        $(document).on('click', '#heart-button', function() {
            markPulseButtonClick('heart-button', 'heart_button');
        });

        $(document).on('click', '#onboarding-button', function() {
            markPulseButtonClick('onboarding-button', 'onboarding_button');
        });

        $(document).on('click', '.download-submission-button', function() {
            var site = $(this).data('site');
            var viewLink = $(this).data('view-link');

            var onDownloadModalClose = function() {
                /* Callback function on Modal close */
                $downloadButton.addClass('disabled');
                $('#file_name').val('');
            };

            $downloadModal.modal({
                complete: onDownloadModalClose
            });

            $downloadModal.modal('open');

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
                            $downloadModal.modal('close');
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
