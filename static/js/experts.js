  var $uid = null;
  $(document).on('click','#archive-expert',function() {
    $uid = $(this).data('uid');
  });
    $(document).on('click','#edit-expert',function() {
    $uid = $(this).data('uid');
    $('#expertModal').modal('show');
  });
    $(document).on('click','#products-expert',function() {
    $uid = $(this).data('uid');

  });

  $('#add-expert').click( function(event) {
    $uid = null;
    $('#expertModal').modal('show');
  });

  $('#save-expert').click( function(event) {
              event.preventDefault();
              $('#uid').val($uid);
              params = $("#expert-form").serializeArray();
              if (validationForm()) {
              $.post( $editExpertEndpoint, params )
                              .done(function( data ) {
                              if (data[0] == 0) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                                        } else {
                                        SuccessMessageSend(data[1], 'Сохранено')
                                        $('#expertModal').modal('hide');
                                        }
                                        });

                //$('#callback-modal').modal('hide');
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
$('#expertModal').on('hide.bs.modal', function (e) {
    $('#experts-table').DataTable().ajax.reload();
});

$('#expertModal').on('show.bs.modal', function (e) {
    if ($uid == null) {
    $('#expert-form')[0].reset();
    $('#save-expert-text').text('Добавить')
    $('.expert-save-icon').addClass('fa-plus')
    $('.expert-save-icon').removeClass('fa-save')
    } else {
    $('#save-expert-text').text('Сохранить')
    $('.expert-save-icon').removeClass('fa-plus')
    $('.expert-save-icon').addClass('fa-save')
   $.post( $getExpertEndpoint, {'uid': $uid} )
                              .fail(function( data ) {

                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                            })
                              .done(function( data ) {
                                        $('#expert-name').val(data['name']);
                                        $('#expert-commission').val(data['commission']);
                                        $('#expert-link').val(data['link']);
                                        $('#expert-commission2').val(data['commission_2']);
                                        $('#expert-comment').val(data['comment']);
                                        });
                                        }

});


