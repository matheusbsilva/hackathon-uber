// Get Color Attribute
// Set the background book color
$("li.book-item").each(function () {
    var $this = $(this);

    $this.find(".bk-front > div").css('background-color', $(this).data("color"));
    $this.find(".bk-left").css('background-color', $(this).data("color"));
    $this.find(".back-color").css('background-color', $(this).data("color"));
    $this.find(".icon-color").css('color', $(this).data("color"));
});
