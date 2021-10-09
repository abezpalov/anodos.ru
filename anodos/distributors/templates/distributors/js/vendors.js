// Привязать вендора как есть
$("body").delegate("[data-do*='do-vendor-as-is']", "click", function(e){
    $.post('/distributors/ajax/do-vendor-as-is/', {
        vendor_: $(this).data('vendor_'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.vendor_ + '-to-pflops').text(data.name);
            //TODO
        }
    }, "json");
    return false;
});

// Отвязать вендора
$("body").delegate("[data-do*='erase-vendor-link']", "click", function(e){
    $.post('/distributors/ajax/erase-vendor-link/', {
        vendor_: $(this).data('vendor_'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.vendor_ + '-to-pflops').text('-');
            //TODO
        }
    }, "json");
    return false;
});

// Открыть диалоговое окно выбора вендора open-vendor-list
$("body").delegate("[data-do*='open-vendor-list']", "click", function(e){
    $('#modal-vendor-list-vendor_').val($(this).data('vendor_'))
    $('#modal-vendor-list-vendor').val('');
    $('#modal-vendor-list').find('div.text').text('');
    $('#modal-vendor-list').find('div.item').removeClass('active');
    $('#modal-vendor-list').find('div.item').removeClass('selected');
    $('#modal-vendor-list').modal('show');
    return false;
});

// Привязать вендора к выбранному в диалоговом окне
$("body").delegate("[data-do*='apply-link-vendor']", "click", function(e){
    $.post('/distributors/ajax/link-vendor/', {
        vendor_: $('#modal-vendor-list-vendor_').val(),
        vendor: $('#modal-vendor-list-vendor').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#' + data.vendor_ + '-to-pflops').text(data.name);
            //TODO
        }
    }, "json");
    return false;
});

// Открыть диалоговое окно редактирования вендора
$("body").delegate("[data-do*='open-vendor-editor']", "click", function(e){
    $('#modal-vendor-editor-id').val($(this).data('vendor'));
    $('#modal-vendor-editor-name').val($(this).data('name'));
    $('#modal-vendor-editor').modal('show');
    return false;
});

// Сохранить изменеия при редактировании вендора
$("body").delegate("[data-do*='save-vendor']", "click", function(e){
    $.post('/distributors/ajax/save-vendor/', {
        vendor: $('#modal-vendor-editor-id').val(),
        name: $('#modal-vendor-editor-name').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('td[data-vendor*="' + data.id + '"]').text(data.name);
            $('button[data-vendor*="' + data.id + '"]').data('name', data.name);
        }
    }, "json");
    return false;
});