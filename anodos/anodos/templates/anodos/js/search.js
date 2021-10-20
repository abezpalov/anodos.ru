// Открыть окно профиля
$("body").delegate("[data-do*='apply-search']", "click", function(e){
    $('#form_search').submit();
});
