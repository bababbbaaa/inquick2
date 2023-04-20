  $('.success-message').hide();
  $('.fail-message').hide();
  $('#pwd-message').hide()
  $('#send-confirm-btn').click(function(event) {
      event.preventDefault();
                    $.post( $confirmationEndpoint, {'email': $(this).data('email') } )
                              .done(function( data ) {
                              if (data[0] == 0) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                              }
                              if (data[0] == 1) {
                                        SuccessMessageSend(data[1], 'Готово')
                              }
                              if (data[0] == 2) {
                                       SuccessMessageSend(data[1], 'Готово')

                              }
                                        });
    });






