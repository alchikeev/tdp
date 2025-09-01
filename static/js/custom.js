/* JS Document - Home page specific functionality */

$(document).ready(function()
{
	"use strict";

	// Initialize home page specific functionality
	initHomeSlider();
	initTestimonialsSlider();

	/* 

	Init Home Slider

	*/

	function initHomeSlider()
	{
		if($('.home_slider').length)
		{
			var homeSlider = $('.home_slider');
			homeSlider.owlCarousel(
			{
				items:1,
				autoplay:false,
				loop:true,
				nav:false,
				dots:false,
				smartSpeed:1200
			});
		}
	}

	/* 

	Init Testimonials Slider

	*/

	function initTestimonialsSlider()
	{
		if($('.testimonials_slider').length)
		{
			var testSlider = $('.testimonials_slider');
			testSlider.owlCarousel(
			{
				animateOut: 'fadeOut',
    			animateIn: 'flipInX',
				items:1,
				autoplay:true,
				loop:true,
				smartSpeed:1200,
				dots:false,
				nav:false
			});
		}
	}
});