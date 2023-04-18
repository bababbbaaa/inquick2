
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
		language: {
			paginate: {
			  next: '<i class="fa fa-angle-double-right mt-2" aria-hidden="true"></i>',
			  previous: '<i class="fa fa-angle-double-left mt-2" aria-hidden="true"></i>'
			}
		  }
	});
	$('#planner-table tbody').on('click', 'tr', function () {
		var data = table.row( this ).data();
		console.log(data);
	});

	
	
})(jQuery);
