{% if perms.pflops.can_edit %}

// Загрузка нового изображения в каталог
var product_image_progressbar = document.getElementById('product-image-progressbar');
UIkit.upload('#product-image-upload', {

    url: '/ajax/product-image-upload/',
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
        product_image_progressbar.removeAttribute('hidden');
        product_image_progressbar.max = e.total;
        product_image_progressbar.value = e.loaded;
    },
    progress: function (e) {
        console.log('progress', arguments);
        product_image_progressbar.max = e.total;
        product_image_progressbar.value = e.loaded;
    },
    loadEnd: function (e) {
        console.log('loadEnd', arguments);
        product_image_progressbar.max = e.total;
        product_image_progressbar.value = e.loaded;
    },
    completeAll: function (e) {
        console.log('completeAll', arguments);

        setTimeout(function () {
            product_image_progressbar.setAttribute('hidden', 'hidden');
        }, 1000);
        data = JSON.parse(e.responseText);
            UIkit.notification({
                message: data.id,
                pos: 'bottom-right',
                timeout: 5000
            });
        $.post('/ajax/product-image-link/', {
            image: data.id,
            product: '{{ product.id }}',
            csrfmiddlewaretoken: '{{ csrf_token }}'
        },
        function(data) {
            if ('success' == data.status){
                UIkit.notification({
                    message: data.id,
                    pos: 'bottom-right',
                    timeout: 5000
                });
            }
        }, "json");
    }
});

// Загрузка информации о продукте из базы для редактирования
$("body").delegate("[data-do='open-product-editor']", "click", function(e){
    product_id = $(this).data('product');
    $.post('/distributors/ajax/get-product/', {
        product: product_id,
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            alert(data.id);
        }
    }, "json");
    return false;
});


{% endif %}