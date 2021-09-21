// Открыть окно профиля
$("body").delegate("[data-do*='open-user-login']", "click", function(e){
    $('#modal-user-login').modal('show');
});


// Авторизоваться
$("body").delegate("[data-do='apply-login']", "click", function(){
    $.post('/ajax/login/', {
        username: $('#login-username').val(),
        password: $('#login-password').val(),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if (data.status == 'success'){
            location.reload();
        } else if (data.status == 'error'){
            $('#modal-login-alert').html('<div class="ui message"><i class="close icon"></i><div class="header">Ошибка!</div>' + data.message + '</div>');
        }
    }, "json");
    return false;
});


// Выйти
$("body").delegate("[data-do='apply-logout']", "click", function(){
    $.post('/ajax/logout/', {
        csrfmiddlewaretoken : '{{ csrf_token }}'
    },
    function(data) {
        if (data.status == 'success'){
            location.reload();
        }
    }, "json");
    return false;
});