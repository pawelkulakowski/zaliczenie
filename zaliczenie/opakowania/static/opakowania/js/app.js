document.addEventListener('DOMContentLoaded', function () {
    var btn = this.getElementById('addContactBtn')

    // $("#addContactBtn").click(function () {
    //     $("#staticBackdrop").modal();
    // });


    $("body").on('click', ".generic-modal", function (e) {
        e.preventDefault();
        console.log(this.href);
        $.get(this.href, function (data) {
            $('#modalContainer').html(data);
            console.log(data);
            $("#staticBackdrop").modal();

            $("body").on("submit", "#modalContainer form", function (e) {
                e.preventDefault();
                $.post(this.action, $(this).serialize(), function () {
                    window.location.reload();
                }).fail(function (data) {
                    $('#modalContainer').html(data.responseText);
                    // console.log(data)
                    $("#staticBackdrop").modal();
                });
            });
        });
    });

    $("body").on('click', ".close-modal", function (e) {
        e.preventDefault();
        $("#staticBackdrop").modal('hide');
        window.location.reload();
    });

    $('[data-toggle=tooltip]').tooltip({delay: { "show": 200, "hide": 100 }});


    //this changes delay time for hyperlink icons

})

