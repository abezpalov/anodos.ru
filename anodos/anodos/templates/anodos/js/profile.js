// Открыть окно профиля
$("body").delegate("[data-do*='open-user-profile']", "click", function(e){
    $('#modal-user-profile').modal('show');
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