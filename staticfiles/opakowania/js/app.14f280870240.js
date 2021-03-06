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


    $(document).on('shown.bs.modal', '.modal', function () {
        $('[data-toggle=tooltip]').tooltip({ delay: { "show": 200, "hide": 100 } });
        $('.table-row-link').click(function () {
            window.location = $(this).data("href");
        });
    });

    $('[data-toggle=tooltip]').tooltip({ delay: { "show": 200, "hide": 100 } });


    //toggle container to see product for selected position
    $('.products-toggle-btn').click(function (e) {
        var btn = $(e.target)
        if (btn.data('mode') === 'hidden') {
            btn.data('mode', 'visible');
            btn.text('Ukryj produkty');
            btn.removeClass('btn-outline-info');
            btn.addClass('btn-outline-danger');
        } else {
            btn.data('mode', 'hidden');
            btn.text('Pokaż produkty');
            btn.removeClass('btn-outline-danger');
            btn.addClass('btn-outline-info');
            //hideRows(btn.data('position_id'));

        };
        console.log('product_container_');
        var div = $(document.getElementById('product_container_' + btn.data('position_id')));
        div.toggle(200);
        var btn2 = $(document.getElementById('show_deleted_products_' + btn.data('position_id')));
        btn2.toggle(200);
    });

    //switch offer view to see only deleted positions
    $('#show-deleted-positions-btn').click(function (e) {
        e.preventDefault();
        var btn = $(e.target)
        if (btn.data('mode') === 'hidden') {
            btn.data('mode', 'visible')
            btn.text('Ukryj usunięte pozycje')
            btn.removeClass('btn-outline-info')
            btn.addClass('btn-outline-danger')
        } else {
            btn.data('mode', 'hidden')
            btn.text('Pokaż usunięte pozycje')
            btn.removeClass('btn-outline-danger')
            btn.addClass('btn-outline-info')

        }
        $('.position-container').toggle(200);
    });

    //unhide deleted products on product list
    $('.show-deleted-products-btn').click(function (e) {
        e.preventDefault();
        var btn = $(e.target)
        if (btn.data('mode') === 'hidden') {
            btn.data('mode', 'visible')
            btn.text('Ukryj usunięte produkty')
            btn.removeClass('btn-outline-info')
            btn.addClass('btn-outline-danger')
        } else {
            btn.data('mode', 'hidden')
            btn.text('Pokaż usunięte produkty')
            btn.removeClass('btn-outline-danger')
            btn.addClass('btn-outline-info')
        }
        var div = document.querySelector("#product_container_" + btn.data('position_id'));
        var rows = div.querySelectorAll(".delete-product-hidden-row");
        for (let i = 0; i < rows.length; i++) {
            $(rows[i]).toggle(200);
        }


    });
    //this changes delay time for hyperlink icons

})

function hideRows(id) {
    var div = document.querySelector("#product_container_" + id);
    var rows = div.querySelectorAll(".delete-product-hidden-row");
    var btn = document.querySelector("#show_deleted_products_" + id)
    console.log('hry')
    for (let i = 0; i < rows.length; i++) {
        $(rows[i]).hide()
    }
    btn.data('mode', 'hidden')
    btn.text('Pokaż usunięte produkty')
    btn.removeClass('btn-outline-danger')
    btn.addClass('btn-outline-info')
}