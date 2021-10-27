{% if perms.pflops.can_edit %}

// Загрузка нового изображения в каталог
var new_catalog_element_progressbar = document.getElementById('new-catalog-element-progressbar');

UIkit.upload('#new-catalog-element-upload', {

    url: '/ajax/load-catalog-element-image/',
    multiple: true,

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

        new_catalog_element_progressbar.removeAttribute('hidden');
        new_catalog_element_progressbar.max = e.total;
        new_catalog_element_progressbar.value = e.loaded;
    },

    progress: function (e) {
        console.log('progress', arguments);

        new_catalog_element_progressbar.max = e.total;
        new_catalog_element_progressbar.value = e.loaded;
    },

    loadEnd: function (e) {
        console.log('loadEnd', arguments);

        new_catalog_element_progressbar.max = e.total;
        new_catalog_element_progressbar.value = e.loaded;
    },

    completeAll: function (e) {
        console.log('completeAll', arguments);

        setTimeout(function () {
            new_catalog_element_progressbar.setAttribute('hidden', 'hidden');
        }, 1000);

        data = JSON.parse(e.responseText);
            UIkit.notification({
                message: data.id,
                pos: 'bottom-right',
                timeout: 5000
            });

        $('#new-catalog-element-image-view').html('<img src="' + data.url + '" >');
        $('#new-catalog-element-image').val(data.id);
    }
});

// Сохранение нового элемента в каталог
$("body").delegate("[data-do='save-new-catalog-element']", "click", function(){

    alert($('#new-catalog-element-image').val());

    $.post('/ajax/save-new-catalog-element/', {
        title: $('#new-catalog-element-title').val(),
        slug: $('#new-catalog-element-slug').val(),
        image: $('#new-catalog-element-image').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            UIkit.notification({
                message: data.id,
                pos: 'bottom-right',
                timeout: 5000
            });
            UIkit.notification({
                message: data.title,
                pos: 'bottom-right',
                timeout: 5000
            });
            UIkit.notification({
                message: data.image,
                pos: 'bottom-right',
                timeout: 5000
            });
            UIkit.notification({
                message: data.test,
                pos: 'bottom-right',
                timeout: 5000
            });
        }
    }, "json");
    return false;




});


{% endif %}
