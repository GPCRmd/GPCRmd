$(document).ready(function () {
    var height_screen = screen.height;
    var descr_height = [(screen.height-468),"px"];
    var square_descr=$(document).find("#square_description");
    var height_square=$(square_descr).css("height",descr_height.join(""));
});  
