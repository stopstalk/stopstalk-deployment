(function($) {
    "use strict";

    $(document).ready(function() {
        $("textarea#testimonial-content").characterCounter();
        setTimeout(function() { $(".content:after").css('content','none'); }, 1);
        $("#submit-testimonial").click(function(e) {
            e.preventDefault();
            var fieldLength = $("#testimonial-content").val().trim().length;
            if (fieldLength < 20) {
                $.web2py.flash("Please fill atleast 20 characters");
            } else if (fieldLength <= 400) {
                $("#testimonial-form").submit();
            } else {
                $.web2py.flash("Character Limit reached");
            }
        });

        $(".love-testimonial").click(function() {
            var $this = $(this),
                $loveCount = $($this.siblings()[0]),
                $heartIcon = $this.children()[0];

            if ($heartIcon.classList.contains("red-text")) {
                $.web2py.flash("Already voted the testimonial");
            } else {
                if (loggedIn === "False") {
                    $.web2py.flash("Please login to cast your vote");
                } else {
                    $.ajax({
                        url: loveTestimonialURL + "/" + $(this).data()["id"],
                        method: "POST",
                        success: function(response) {
                            $loveCount.html(response["love_count"]);
                            $heartIcon.classList.add("red-text");
                            $.web2py.flash("Vote submitted");
                        },
                        error: function(response) {
                            if (response.status === 401) {
                                $.web2py.flash("Please login to cast your vote");
                            } else {
                                $.web2py.flash("Error submitting your vote");
                            }
                        }
                    });
                }
            }
        });
    });

})(jQuery);
