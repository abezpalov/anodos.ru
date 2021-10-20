$("body").delegate("[data-do*='show-image']", "click", function(e){
    $("[data-do*='show-image']").removeClass('green');
    $(this).addClass('green');
    src=$(this).data('src');
    $('#showed-image').attr("src", src);
});
