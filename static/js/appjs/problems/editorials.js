(function($) {
  $(document).ready(function() {
    $(".love-editorial").click(function() {
      var $this = $(this),
          $loveCount = $($this.siblings()[0]),
          $heartIcon = $this.children()[0];
      console.log($heartIcon.classList);
      if ($heartIcon.classList.contains("red-text")) {
        $.web2py.flash("Already voted the editorial");
      } else {
        if (loggedIn === "False") {
          $.web2py.flash("Please login to cast your vote");
        } else {
          $.ajax({
            url: loveEditorialURL + "/" + $(this).data()["id"],
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
    var simplemde = new SimpleMDE({
        autofocus: false,
        autosave: {
            enabled: true,
            uniqueId: "MyUniqueID",
            delay: 1000,
        },
        autoDownloadFontAwesome: true,
        element: document.getElementById("simplemde"),
        forceSync: true,
        indentWithTabs: false,
        lineWrapping: false,
        parsingConfig: {
            allowAtxHeaderWithoutSpace: true,
            strikethrough: false,
            underscoresBreakWords: true,
        },
        placeholder: "Start writing your editorial here ...",
        promptURLs: true,
        renderingConfig: {
            singleLineBreaks: false,
            codeSyntaxHighlighting: true,
        },
        shortcuts: {
            drawTable: "Cmd-Alt-T"
        },
        showIcons: ["code", "table"],
        spellChecker: false,
        status: false,
        status: ["autosave", "lines", "words", "cursor"], // Optional usage
        styleSelectedText: false,
        tabSize: 2,
        toolbarTips: true
    });
  });
})(jQuery);