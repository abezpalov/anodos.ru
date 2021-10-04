// Привязать вендора как есть
$("body").delegate("[data-do*='do-vendor-as-is']", "click", function(e){
    id = $(this).data('id');
    $.post('/distributors/ajax/do-vendor-as-is/', {
        id: id,
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            td_id = '#' + id + '-to-pflops';
            $(td_id).text(data.name);
        }
    }, "json");
    return false;
});

// Отвязать вендора
$("body").delegate("[data-do*='erase-vendor-link']", "click", function(e){
    id = $(this).data('id');
    $.post('/distributors/ajax/erase-vendor-link/', {
        id: id,
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            td_id = '#' + id + '-to-pflops';
            $(td_id).text('-');
        }
    }, "json");
    return false;
});

// Открыть диалоговое окно выбора вендора open-vendor-list
$("body").delegate("[data-do*='erase-vendor-link']", "click", function(e){



    return false;
});