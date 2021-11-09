// Фокус на поиске при загрузке страницы
$("#main-search").focus();

// Заказать обратный звонок
$("body").delegate("[data-do='save-conversion-call']", "click", function(){
    $.post('/ajax/save-conversion-call/', {
        phone: $('#form-conversion-call-phone').val(),
        name: $('#form-conversion-call-name').val(),
        url: $('#form-conversion-call-url').val(),
        csrfmiddlewaretoken : '{{ csrf_token }}'
    },
    function(data) {
        if (data.status == 'success'){
            UIkit.modal($('#modal-conversion-call')).hide();
        }
        UIkit.notification({
            message: data.message,
            status: data.status,
            pos: 'bottom-right',
            timeout: 5000
        });

    }, "json");
    return false;
});