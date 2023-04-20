  $('.success-message').hide();
  $('.fail-message').hide();
  $('#pwd-message').hide()
  $('#submit-btn').click(function(event) {
      event.preventDefault();
      params = $("#form").serializeArray();
      if (validationLoginForm()) {
        LoginFormProceed(params);
      }
    });

$(".form-control").on('keydown', function(e) {
if( (event.keyCode == 13) ) {
$('#submit-btn').click()
        }
     });




function LoginFormProceed(params) {
    $('#submit-btn').attr('disabled', true);
    $.post( '', params )
      .fail(function(){
            $('#fail-msg').text('Что-то пошло не так... Попробуйте позднее');
            $('.success-message').hide();
            $('.fail-message').show();
            $('#submit-btn').removeAttr('disabled');
        })
      .done(function( data ) {
      if (data[0] == 0) {
                    $('#fail-msg').text(data[1]);
                    $('.fail-message').show();
                    $('.success-message').hide();
                    $('#submit-btn').removeAttr('disabled');
                    }
      if (data[0]==1) {
                    $('#success-msg').text(data[1]);
                    $('.success-message').show();
                    $('.fail-message').hide();
                    }
      if (data[0]==2) {
                    location.replace(data[2]);
                    }
                });
}


function validationLoginForm(form) {
        var validated = true;
            $('.form-control').each(function() {

                    if ($(this).hasClass('email-validate')) {
                            if (IsEmail($(this).val()) != true) {
                                console.log('mail');
                                $(this).addClass("is-invalid");
                                $(this).prev().addClass("is-invalid");
                                $(this).next().show();
                                validated = false;
                            }
                    }

                    var empty = ($(this).val() == "" || $(this).val() == null)
                    if (empty) {
                        $(this).addClass("is-invalid");
                        $(this).prev().addClass("is-invalid");
                        $(this).next().show();
                        validated = false;
                        }

                    if ($(this).val().length < 8 && $(this).hasClass('password-validate'))  {
                        $(this).addClass("is-invalid");
                        $(this).prev().addClass("is-invalid");
                        $(this).next().show();
                        validated = false;
                    }

            });
        return validated;
}
$("#password").keyup(function() {
    if ($("#password").val().length < 8) {
                        $('#pwd-message').show()
                        } else {
                        $('#pwd-message').hide()

                    }
});

function IsEmail(email) {
  var regex = /^([a-zA-Z0-9_\.\-\+])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
  if(!regex.test(email)) {
    return false;
  }else{
    return true;
  }
}

