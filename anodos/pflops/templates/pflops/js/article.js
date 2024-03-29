{% if perms.pflops.can_edit %}

// Загрузка нового изображения в каталог
var new_assistant_element_progressbar = document.getElementById('new-assistant-element-progressbar');

UIkit.upload('#new-assistant-element-upload', {

    url: '/ajax/load-assistant-element-image/',
    multiple: true,
    mime: 'image/*',

    beforeSend: function (environment) {
        console.log('beforeSend', arguments);
        // The environment object can still be modified here.
        // var {data, method, headers, xhr, responseType} = environment;
    },
    beforeAll: function () {
        console.log('beforeAll', arguments);
    },
    load: function () {
        console.log('load', arguments);
    },
    error: function () {
        console.log('error', arguments);
    },
    complete: function () {
        console.log('complete', arguments);
    },
    loadStart: function (e) {
        console.log('loadStart', arguments);
        new_assistant_element_progressbar.removeAttribute('hidden');
        new_assistant_element_progressbar.max = e.total;
        new_assistant_element_progressbar.value = e.loaded;
    },
    progress: function (e) {
        console.log('progress', arguments);
        new_assistant_element_progressbar.max = e.total;
        new_assistant_element_progressbar.value = e.loaded;
    },
    loadEnd: function (e) {
        console.log('loadEnd', arguments);
        new_assistant_element_progressbar.max = e.total;
        new_assistant_element_progressbar.value = e.loaded;
    },
    completeAll: function (e) {
        console.log('completeAll', arguments);
        setTimeout(function () {
            new_assistant_element_progressbar.setAttribute('hidden', 'hidden');
        }, 1000);
        data = JSON.parse(e.responseText);
            UIkit.notification({
                message: data.id,
                pos: 'bottom-right',
                timeout: 5000
            });
        $('#new-assistant-element-image-view').html('<img src="' + data.url + '" >');
        $('#new-assistant-element-image').val(data.id);
    }
});

// Сохранение нового элемента помощи
$("body").delegate("[data-do='save-new-assistant-element']", "click", function(){
    $.post('/ajax/save-new-assistant-element/', {
        title: $('#new-assistant-element-title').val(),
        slug: $('#new-assistant-element-slug').val(),
        image: $('#new-assistant-element-image').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            location.reload();
        }
    }, "json");
    return false;
});

{% endif %}
