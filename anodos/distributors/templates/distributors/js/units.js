// Привязать вендора как есть
$("body").delegate("[data-do='do-parameter-as-is']", "click", function(e){
    $.post('/distributors/ajax/do-parameter-as-is/', {
        parameter_: $(this).data('parameter_'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.parameter_ + '-to-pflops').text(data.name);
            //TODO
        }
    }, "json");
    return false;
});

// Отвязать вендора
$("body").delegate("[data-do='erase-parameter-link']", "click", function(e){
    $.post('/distributors/ajax/erase-parameter-link/', {
        parameter_: $(this).data('parameter_'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.parameter_ + '-to-pflops').text('-');
            //TODO
        }
    }, "json");
    return false;
});

// Открыть диалоговое окно выбора вендора open-parameter-list
$("body").delegate("[data-do='open-parameter-list']", "click", function(e){
    $('#modal-parameter-list-parameter_').val($(this).data('parameter_'))
    $('#modal-parameter-list-parameter').val('');
    $('#modal-parameter-list').find('div.text').text('');
    $('#modal-parameter-list').find('div.item').removeClass('active');
    $('#modal-parameter-list').find('div.item').removeClass('selected');
    $('#modal-parameter-list').modal('show');
    return false;
});

// Привязать вендора к выбранному в диалоговом окне
$("body").delegate("[data-do='apply-link-parameter']", "click", function(e){
    $.post('/distributors/ajax/link-parameter/', {
        parameter_: $('#modal-parameter-list-parameter_').val(),
        parameter: $('#modal-parameter-list-parameter').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.parameter_ + '-to-pflops').text(data.name);
            //TODO
        }
    }, "json");
    return false;
});

// Открыть диалоговое окно редактирования вендора
$("body").delegate("[data-do='open-parameter-editor']", "click", function(e){
    $('#modal-parameter-editor-id').val($(this).data('parameter'));
    $('#modal-parameter-editor-name').val($(this).data('name'));
    $('#modal-parameter-editor').modal('show');
    return false;
});

// Сохранить изменеия при редактировании вендора
$("body").delegate("[data-do='save-parameter']", "click", function(e){
    $.post('/distributors/ajax/save-parameter/', {
        parameter: $('#modal-parameter-editor-id').val(),
        name: $('#modal-parameter-editor-name').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('td[data-parameter="' + data.id + '"]').text(data.name);
            $('button[data-parameter="' + data.id + '"]').data('name', data.name);
        }
    }, "json");
    return false;
});