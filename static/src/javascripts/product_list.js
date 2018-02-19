$().ready(function(){
    $('#product-add-btn').on('click', function(e) {
        $('#product-form-row td').show();
        $('#product-add-btn').hide();
        $('#product-name-input').focus();
    });
    $('.product-delete-btn').on('click', deleteProduct);
    $('#product-submit-btn').on('click', addProduct);
    // 엔터, 서브밋 막아줌
    $('#product-form-row input').on('keydown', function(e) {
        if(e.which == 13) {
            e.preventDefault();
        }
    });
    $('#product-name-input').on('keyup', function(e) {
        validateScheduleAddInput();
        if(e.which == 13) {
            $('#product-price-input').focus();
        }
    });
    $('#product-price-input').on('keyup', function(e) {
        if(e.which == 13) {
            addProduct();
        }
    });
})

function validateProductAddInput() {
    var isValid = true;
    $('#product-form-row input').each(function(e) {
        if(!$(this).val()) {
            alert("'" + $(this).attr('placeholder') + "' is empty");
            isValid = false;
            return isValid;
        }
    })
    return isValid;
}

function deleteProduct(e) {
    if (!confirm($("#delete-product-warning").val())) return;
    id = $(this).closest('td').find('input').val();
    tr = $(this).closest('tr');
    csrfmiddlewaretoken = $('input[name*="csrfmiddlewaretoken"]').val();
    data = "csrfmiddlewaretoken=" + csrfmiddlewaretoken + "&id=" + id
    $.ajax({
        url: './product/'+id+'/delete/',
        type: 'POST',
        data: {
            csrfmiddlewaretoken: csrfmiddlewaretoken,
        },
    })
    .done(function(data) {
        tr.remove();
        // alert(data.message);
    }).fail(function(data) {
        alert(data.message);
    })
}

function addProduct() {
    if(!validateProductAddInput()) {
        return;
    } else {
        $.post('./product/', $('#product-form').serialize(), function(data) {
            var product = data.product;
            var tr = '<tr>' + 
                ['-', product.category.name, product.name, product.price].map(function(data){
                    return '<td class="text-center">' + data + '</td>'
                }) + '</td>';
            $('#product-list tbody').prepend(tr);
        })
        .fail(function(err) {
            err.responseJSON.message && alert(err.responseJSON.message);
        }).done(function() {
            $('#product-form-row input').val('');
        });
    }
}