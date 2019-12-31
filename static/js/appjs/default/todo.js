(function($) {
    "use strict";

    $(document).ready(function() {
        $(".remove-from-todo").click(function() {
            var plink = this.getAttribute("data-link"),
                $this = $(this);

            $.ajax({
                url: removeTodoURL,
                method: "POST",
                data: {"plink": plink},
                success: function (resp) {
                    $this.parent().parent().fadeOut(300, function() {
                        $(this).remove();
                    });
                    $.web2py.flash("Problem removed from Todo list");
                },
                error: function(e) {
                    $.web2py.flash("Error deleting problem");
                }
            });
        });
    });
})(jQuery);
