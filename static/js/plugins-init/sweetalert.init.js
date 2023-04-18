(function ($) {
    "use strict"
document.querySelector(".sweet-confirm").onclick = function () {
        swal({
            title: "Are you sure to delete ?",
            text: "You will not be able to recover this imaginary file !!",
            type: "warning",
            showCancelButton: !0,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Yes, delete it !!",
            closeOnConfirm: !1
        }, function () {
            swal("Deleted !!", "Hey, your imaginary file has been deleted !!", "success")
        }
        )}

 })(jQuery);