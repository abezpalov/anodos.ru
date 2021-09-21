// Открыть окно профиля
$("body").delegate("[data-do*='apply-distributors-search']", "click", function(e){
    $('#form_distributors_search').submit();
});
