
(function($) {
    "use strict"
    //example 1



	// orderTable
		var table = $('#orderTable').DataTable({

			searching: false,
			paging:true,
			select: false,
			info: false,         
			lengthChange:false ,
			language: {
				paginate: {
				  next: '<i class="fa fa-angle-double-right" aria-hidden="true"></i>',
				  previous: '<i class="fa fa-angle-double-left" aria-hidden="true"></i>' 
				}
			  }
			
		});
		
		
	
	// table row
	var table = $('#planner-table').DataTable({
	    columnDefs: [
               { orderable: false, targets: -1 }
            ],
		language: {
			paginate: {
			  next: '<i class="fa fa-angle-double-right mt-2" aria-hidden="true"></i>',
			  previous: '<i class="fa fa-angle-double-left mt-2" aria-hidden="true"></i>'
			}
		  }
	});
	var table = $('#experts-table').DataTable({
	    ajax: $expertTableEndpoint,
	    columnDefs: [
               { orderable: false,
               render: function (data, type) {
                    return '<div class="dropdown ms-auto text-start"><div class="btn-link pointer-link" data-bs-toggle="dropdown" aria-expanded="false"><svg width="24px" height="24px" viewBox="0 0 24 24" version="1.1"><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd"><rect x="0" y="0" width="24" height="24"></rect><circle fill="#000000" cx="5" cy="12" r="2"></circle><circle fill="#000000" cx="12" cy="12" r="2"></circle><circle fill="#000000" cx="19" cy="12" r="2"></circle></g></svg></div><div class="dropdown-menu dropdown-menu-start" style="margin: 0px;"><button  id="products-expert" class="dropdown-item control-buttons" data-uid=' + data + '><i class="flaticon-381-reading me-2"></i>Продукты</button><button  id="edit-expert" class="dropdown-item control-buttons" data-uid=' + data + '><i class="fa fa-edit me-2"></i>Редактировать</button><button id="archive-expert" class="dropdown-item control-buttons" data-uid=' + data + '><i class="fa fa-archive me-2"></i>Убрать в архив</button></div></div>';
                },
               targets: -1 },
               {render: function (data, type, row) {
                    return '<a target="_blank" href="'+row[1]+'">' + data +' <i class="fa fa-sign-in"></i></a>';
                },
               targets: 0 },
               { visible: false, targets: [1] },
               {render: function (data, type) {
                    return data + '%';
                },
               targets: 2 },
            ],

		language: {
			paginate: {
			  next: '<i class="fa fa-angle-double-right mt-2" aria-hidden="true"></i>',
			  previous: '<i class="fa fa-angle-double-left mt-2" aria-hidden="true"></i>'
			}
		  }
	});

		var table = $('#products-table').DataTable({
	    ajax: $productTableEndpoint,
	    columnDefs: [
               { orderable: false,
               render: function (data, type) {
                    return '<div class="dropdown ms-auto text-start"><div class="btn-link pointer-link" data-bs-toggle="dropdown" aria-expanded="false"><svg width="24px" height="24px" viewBox="0 0 24 24" version="1.1"><g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd"><rect x="0" y="0" width="24" height="24"></rect><circle fill="#000000" cx="5" cy="12" r="2"></circle><circle fill="#000000" cx="12" cy="12" r="2"></circle><circle fill="#000000" cx="19" cy="12" r="2"></circle></g></svg></div><div class="dropdown-menu dropdown-menu-start" style="margin: 0px;"><button  id="products-expert" class="dropdown-item control-buttons" data-uid=' + data + '><i class="flaticon-381-reading me-2"></i>Продукты</button><button  id="edit-expert" class="dropdown-item control-buttons" data-uid=' + data + '><i class="fa fa-edit me-2"></i>Редактировать</button><button id="archive-expert" class="dropdown-item control-buttons" data-uid=' + data + '><i class="fa fa-archive me-2"></i>Убрать в архив</button></div></div>';
                },
               targets: -1 },
               {render: function (data, type, row) {
                    return '<a target="_blank" href="'+row[1]+'">' + data +' <i class="fa fa-sign-in"></i></a>';
                },
               targets: 0 },

            ],

		language: {
			paginate: {
			  next: '<i class="fa fa-angle-double-right mt-2" aria-hidden="true"></i>',
			  previous: '<i class="fa fa-angle-double-left mt-2" aria-hidden="true"></i>'
			}
		  }
	});
	
	
})(jQuery);
