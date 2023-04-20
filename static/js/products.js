
  var $uid = null;


  $('#expert-select').select2({
  ajax: {
    url: $getAuthorsEndpoint,
    dataType: 'json'
  }
});


  $(document).on('click','#archive-product',function() {
    $uid = $(this).data('uid');
  });
    $(document).on('click','#edit-product',function() {
    $uid = $(this).data('uid');
    $('#productModal').modal('show');
  });


  $('#add-product').click( function(event) {
    $uid = null;
    $('#productModal').modal('show');
  });

  $('#save-product').click( function(event) {
              $(this).addClass('btn-loading')
              event.preventDefault();
              $('#uid').val($uid);
              params = $("#product-form").serializeArray();
              if (validationForm()) {
              $.post( $editProductEndpoint, params )
                              .done(function( data ) {
                              if (data[0] == 0) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                                        $(this).removeClass('btn-loading')
                                        } else {
                                        SuccessMessageSend(data[1], 'Сохранено')
                                        $('#productModal').modal('hide');
                                        }
                                        });

                //$('#callback-modal').modal('hide');
              } else {
              $('html,body').animate({scrollTop: $('.is-invalid').first().offset().top - 100});
              }
     });

function validationForm(form) {
    var validated = true;
        $('.form-control').each(function() {
                var empty = ($(this).val() == "" || $(this).val() == null)
                if (empty && $(this).hasClass('form-validate')) {
                    $(this).addClass("is-invalid");
                    $(this).prev().addClass("is-invalid");
                    $(this).next().show();
                    validated = false;
                    }

        });
    return validated;
}
$('#productModal').on('hide.bs.modal', function (e) {
    $('#products-table').DataTable().ajax.reload();
});

$('#productModal').on('show.bs.modal', function (e) {
console.log($uid);
    if ($uid == null) {
    $('#product-form')[0].reset();
    $('#expert-select').val(null).trigger("change");
    $('#save-product-text').text('Добавить')
    $('.product-save-icon').addClass('fa-plus')
    $('.product-save-icon').removeClass('fa-save')
    } else {
    $('#save-product-text').text('Сохранить')
    $('.product-save-icon').removeClass('fa-plus')
    $('.product-save-icon').addClass('fa-save')
   $.post( $getProductEndpoint, {'uid': $uid} )
                              .fail(function( data ) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                            })
                              .done(function( data ) {
                                        if ($('#expert-select').find("option[value='" + data['author']+ "']").length) {
                                              $('#expert-select').val(data['author']).trigger('change');
                                          } else {
                                              // Create a DOM Option and pre-select by default
                                              var newOption = new Option(data['author_name'], data['author'], true, true);
                                              // Append it to the select
                                              $('#expert-select').append(newOption).trigger('change').select2();
                                          }

                                        $('#product-name').val(data['name']);
                                        $('#product-promo-price').val(data['promo_price']);
                                        $('#product-price').val(data['price']);
                                        $('#product-link').val(data['link']);
                                        $('#product-comment').val(data['comment']);
                                        });
                                        }

});


	    $('#products-table').on('click', 'tr', function () {
	    console.log('test');
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        } else {
            $('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    });