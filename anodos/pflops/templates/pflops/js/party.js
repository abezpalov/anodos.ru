$("body").delegate("[data-do*='show-parties']", "click", function(e){
    $.post('/ajax/get-parties/', {
        product: $(this).data('product'),
        csrfmiddlewaretoken: '{{ csrf_token }}'
    },
    function(data) {
        if ('success' == data.status){
            $('#modal-parties-content').html(data.html);
            $('#modal-parties').modal('show');
        }
    }, "json");
    return false;
});
