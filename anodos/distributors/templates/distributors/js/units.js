// Привязать вендора как есть
$("body").delegate("[data-do='do-unit-as-is']", "click", function(e){
    $.post('/distributors/ajax/do-unit-as-is/', {
        unit_: $(this).data('unit_'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.unit_ + '-to-pflops').text(data.name);
            //TODO
        }
    }, "json");
    return false;
});

// Отвязать вендора
$("body").delegate("[data-do='erase-unit-link']", "click", function(e){
    $.post('/distributors/ajax/erase-unit-link/', {
        unit_: $(this).data('unit_'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.unit_ + '-to-pflops').text('-');
            //TODO
        }
    }, "json");
    return false;
});

// Открыть диалоговое окно выбора вендора open-unit-list
$("body").delegate("[data-do='open-unit-list']", "click", function(e){
    $('#modal-unit-list-unit_').val($(this).data('unit_'))
    $('#modal-unit-list-unit').val('');
    return false;
});

// Привязать вендора к выбранному в диалоговом окне
$("body").delegate("[data-do='apply-link-unit']", "click", function(e){
    $.post('/distributors/ajax/link-unit/', {
        unit_: $('#modal-unit-list-unit_').val(),
        unit: $('#modal-unit-list-unit').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.unit_ + '-to-pflops').text(data.name);
            //TODO
        }
    }, "json");
    return false;
});

// Открыть диалоговое окно редактирования вендора
$("body").delegate("[data-do='open-unit-editor']", "click", function(e){
    $('#modal-unit-editor-id').val($(this).data('unit'));
    $('#modal-unit-editor-name').val($(this).data('name'));
    return false;
});

// Сохранить изменеия при редактировании вендора
$("body").delegate("[data-do='save-unit']", "click", function(e){
    $.post('/distributors/ajax/save-unit/', {
        unit: $('#modal-unit-editor-id').val(),
        name: $('#modal-unit-editor-name').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('td[data-unit="' + data.id + '"]').text(data.name);
            $('button[data-unit="' + data.id + '"]').data('name', data.name);
        }
    }, "json");
    return false;
});
