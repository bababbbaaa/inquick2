
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
	            {
               render: function (data, type) {
                    return '<a href=' + $productsEndpoint +'>Продукты (' + data + ')</a>';
                },
               targets: 2 },

               { 'orderable': false,
               render: function (data, type, row) {
                    return '<button  id="edit-expert" class="btn btn-success light sharp control-buttons" data-uid=' + row[7] + '><i class="fa fa-search"></i></button>';
                },
               targets: -2 },
               { 'orderable': false,
               render: function (data, type, row) {
                    return '<button id="archive-expert" class="btn btn-danger light sharp control-buttons" data-uid=' + row[7] + '><i class="fa fa-remove"></i></button>';
                },
               targets: -1 },
               {render: function (data, type, row)
                    {if (row[1] != 'https://' && row[1] != '') {
                    return '<a target="_blank" href="'+row[1]+'">' + data +' <i class="fa fa-sign-in"></i></a>';
                    }
                    if (row[1] == 'https://') {
                    return data;
                    }
                },
               targets: 0 },
               { visible: false, targets: [1] },
               {render: function (data, type) {
                     if (data == '') {
                    return '-';
                    }
                     if (data !='') {
                    return data + '%';
                    }

                },
               targets: 3 },
                              {render: function (data, type) {
                     if (data == '') {
                    return '-';
                    }
                     if (data !='') {
                    return data + '%';
                    }

                },
               targets: 4 },

            ],

		language: {
			paginate: {
			  next: '<i class="fa fa-angle-double-right" aria-hidden="true"></i>',
			  previous: '<i class="fa fa-angle-double-left" aria-hidden="true"></i>'
			}
		  }
	});

		var table = $('#products-table').DataTable({
	    ajax: $productTableEndpoint,
	    columnDefs: [
	         {render: function (data, type, row)
                    {if (row[1] != 'https://' && row[1] != '') {
                    return '<a target="_blank" href="'+row[1]+'">' + data +' <i class="fa fa-sign-in"></i></a>';
                    }
                    if (row[1] == 'https://') {
                    return data;
                    }
                },
               targets: 0 },
               { visible: false, targets: [1] },

               { 'orderable': false,
               render: function (data, type, row) {
                    return '<button  id="edit-product" class="btn btn-success light sharp control-buttons" data-uid=' + row[6] + '><i class="fa fa-search"></i></button>';
                },
               targets: -2 },
               { 'orderable': false,
               render: function (data, type, row) {
                    return '<button id="archive-product" class="btn btn-danger light sharp control-buttons" data-uid=' + row[6] + '><i class="fa fa-remove"></i></button>';
                },
               targets: -1 },
               {render: function (data, type, row) {
                    return '<a target="_blank" href="'+row[1]+'">' + data +' <i class="fa fa-sign-in"></i></a>';
                },
               targets: 0 },
                              {render: function (data, type) {
                     if (data == '') {
                    return '-';
                    }
                     if (data !='') {
                    return data + '%';
                    }

                },
               targets: 4 },
                              {render: function (data, type) {
                     if (data == '') {
                    return '-';
                    }
                     if (data !='') {
                    return data + '%';
                    }

                },
               targets: 5 }

            ],

		language: {
			paginate: {
			  next: '<i class="fa fa-angle-double-right mt-2" aria-hidden="true"></i>',
			  previous: '<i class="fa fa-angle-double-left mt-2" aria-hidden="true"></i>'
			}
		  }
	});


	
	
})(jQuery);
