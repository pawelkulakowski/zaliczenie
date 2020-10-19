document.addEventListener('DOMContentLoaded', function () {
    var btn = this.getElementById('addContactBtn')

    $('.disabled').click(function (e) {
        e.preventDefault();
    });

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

    $("body").on('click', ".offerContactList", function (e) {
        e.preventDefault();
        $.get(this.href, function (data) {
            $('#offerContactListContainer').html(data);
        });
    });

    $("body").on('click', ".offerContactList-hide", function (e) {
        e.preventDefault();
        $.get(this.href, function (data) {
            $('#offerContactListContainer').empty();
        });
    });

    $("body").on('click', ".offerAddressList", function (e) {
        e.preventDefault();
        $.get(this.href, function (data) {
            $('#offerAddressListContainer').html(data);
        });
    });

    $("body").on('click', ".offerAddressList-hide", function (e) {
        e.preventDefault();
        $.get(this.href, function (data) {
            $('#offerAddressListContainer').empty();
        });
    });

    $("body").on('click', ".close-modal", function (e) {
        e.preventDefault();
        $("#staticBackdrop").modal('hide');
        window.location.reload();
    });

    $('[data-toggle=tooltip]').tooltip({ delay: { "show": 200, "hide": 100 } });

    $('.products-toggle-btn').click(function(e){
        var btn = $(e.target)
        console.log(btn.data('position_id'))
        $(document.getElementById(btn.data('position_id'))).toggle(500)
     });


    //this changes delay time for hyperlink icons

})

