    $('.multi-select').select2();
    $(".notify-dialog").hide();
    $(".agree-dialog").hide();
    $(".cancel-dialog").hide();

    var $bloger_id = null;
    var $state_id = null;
    var $target_element = null;
    var $target_class = null;
    var $target_text = null;
    var $content_access = null;
    var $communicationId = null;


  $('.control-buttons').click(function() {

    $target_element = $(this);
    $state_id = $(this).data('state');
    $bloger_id = $(this).data('bloger-id');
    $target_text = $target_element.text();
    console.log($state_id);
  });

  $(".change-state").click(function(event) {
             event.preventDefault();
             $state_id = $(this).data('state');
             $bloger_id = $(this).data('bloger-id');
             let state = $(this).data('state');
             $( ".change-state" ).each(function() {
                  $( this ).addClass( "light" );
             });


             $(this).removeClass('light');
             $target_class = $(this).data('badge-class');
             $target_text = $(this).text();
             if (state == 3) {
             $(".cancel-dialog").show();
             $(".notify-dialog").hide();
             $(".agree-dialog").hide();
             }
             if (state == 2) {
             $(".agree-dialog").show();
             $(".notify-dialog").hide();
             $(".cancel-dialog").hide();
             }
             if (state < 2) {
             $(".notify-dialog").show();
             $(".agree-dialog").hide();
             $(".cancel-dialog").hide();
             }

             });


$('#communicationsModal').on('show.bs.modal', function (e) {
  $("#communicationsModal .datepicker-default").val(currentDate);
});

$('#blogerModal').on('show.bs.modal', function (e) {
     $("#bloger-details").hide();
     $("#bloger-form")[0].reset();
     $("#save-bloger").attr('disabled', true);
     $("#save-bloger").addClass('light btn-dark');
     $("#save-bloger").removeClass('btn-success');
     $('.multi-select').val(null).trigger("change");

});

$('.multi-select').on("change", function(){
      var selectData = $(this).find(':selected');
      $("#bloger-details").show();
      $("#save-bloger").removeAttr('disabled');
      $("#save-bloger").removeClass('light btn-dark');
      $("#save-bloger").addClass('btn-success');
      if (selectData.length == 0) {
      $("#bloger-details").hide();
      $("#save-bloger").attr('disabled', true);
      $("#save-bloger").addClass('light btn-dark');
      $("#save-bloger").removeClass('btn-success');
      $("#bloger-form")[0].reset();
      }
  });

$('#statusModal').on('show.bs.modal', function (e) {
  $(".change-state" ).each(function() {
                  $( this ).addClass( "light" );
  });
     $(".notify-dialog").hide();
     $(".agree-dialog").hide();
     $(".cancel-dialog").hide();
     $("#state-form")[0].reset();

});
$('#questionModal').on('shown.bs.modal', function (e) {
    console.log('state', $state_id);
  if ($state_id == 0) {
  $("#content-yes").addClass('light');
  $("#content-no").removeClass('light');
  } else {
  $("#content-no").addClass('light');
  $("#content-yes").removeClass('light');

  }
});

$('#commentModal').on('show.bs.modal', function (e) {

   $.post( $getCommentEndpoint, {'bloger_id': $bloger_id} )
                              .done(function( data ) {
                              if (data[0] == 0) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                                        $('#comment-text').val('');
                                        } else {
                                        $('#comment-text').val(data[1]);
                                        }
                                        });

});
  $("#save-comment").click(function(event) {
             event.preventDefault();
             $target_text = $("#comment-text").val();
             $.post( $editCommentEndpoint, {'bloger_id': $bloger_id, 'comment': $target_text} )
                              .done(function( data ) {
                              if (data[0] == 0) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                                        } else {
                                        SuccessMessageSend(data[1], 'Сохранено')
                                        $target_text = jQuery.trim($target_text).substring(0, 40).trim(this) + "...";
                                        $target_element.text($target_text);
                                        $('#commentModal').modal('hide');
                                        }
                                        });


    });


    $("#save-communication").click(function(event) {
             event.preventDefault();
             $target_text = $("#communication-date").val();
             $.post( $editCommunicationDateEndpoint, {'bloger_id': $bloger_id, 'communication': $target_text} )
                              .done(function( data ) {
                              if (data[0] == 0) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                                        } else {
                                        SuccessMessageSend(data[1], 'Сохранено')
                                        $("<a href='javascript:void(0)' class='badge badge-rounded badge-outline-light'>" + $target_text + "</a><br>" ).insertBefore($target_element);
                                        $('#communicationsModal').modal('hide');
                                        }
                                        });


    });

  $(".content-access").click(function(event) {
             event.preventDefault();
             $target_text = $(this).text();
             $content_access = $(this).data('state');

             $( ".content-access" ).each(function() {
                  $( this ).addClass( "light" );
             });
             $(this).removeClass('light');
             $.post( $contentAccessEndpoint, {'bloger_id': $bloger_id, 'state': $content_access} )
                              .done(function( data ) {
                              if (data[0] == 0) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                                        } else {
                                        SuccessMessageSend(data[1], 'Сохранено')
                                        }
                                        });
                $target_element.text($target_text);
                $target_element.attr('data-state',$content_access);
    });

    $('#state-save').click( function(event) {
              event.preventDefault();
              $('#state-id').val($state_id);
              params = $("#state-form").serializeArray();
              $.post( $changeStateEndpoint, params )
                              .done(function( data ) {
                              if (data[0] == 0) {
                                        ErrorMessageSend(data[1], 'Произошла ошибка')
                                        } else {
                                        SuccessMessageSend(data[1], 'Сохранено')
                                        }
                                        });

                //$('#callback-modal').modal('hide');
                $target_element.text($target_text);
                $target_element.removeAttr('class');
                $target_element.attr('class', $target_class);
                $target_element.attr('data-state', $state_id);



               });