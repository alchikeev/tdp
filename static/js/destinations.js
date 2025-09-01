/* JS Document - Destinations page specific functionality */

$(document).ready(function()
{
	"use strict";

	// Initialize destinations page specific functionality
	initDestinationsIsotope();

	/* 

	Init Destinations Isotope (with sorting buttons)

	*/

	function initDestinationsIsotope()
	{
		var sortingButtons = $('.product_sorting_btn');
		
		if($('.item_grid').length)
		{
			var grid = $('.item_grid').isotope({
				itemSelector: '.item',
	            getSortData:
	            {
	            	price: function(itemElement)
	            	{
	            		var priceEle = $(itemElement).find('.destination_price').text().replace( 'From $', '' );
	            		return parseFloat(priceEle);
	            	},
	            	name: '.destination_title a'
	            },
	            animationOptions:
	            {
	                duration: 750,
	                easing: 'linear',
	                queue: false
	            }
	        });

	        // Sort based on the value from the sorting_type dropdown
	        sortingButtons.each(function()
	        {
	        	$(this).on('click', function()
	        	{
	        		var parent = $(this).parent().parent().find('.sorting_text');
		        		parent.text($(this).text());
		        		var option = $(this).attr('data-isotope-option');
		        		option = JSON.parse( option );
	    				grid.isotope( option );
	        	});
	        });
		}
	}
	
});