// Mobile Menu JavaScript
(function() {
    'use strict';
    
    var menuActive = false;
    
    function toggleMobileMenu() {
        console.log('toggleMobileMenu called, current state:', menuActive);
        
        if (menuActive) {
            closeMenu();
        } else {
            openMenu();
        }
    }
    
    function openMenu() {
        console.log('Opening menu...');
        $('.menu').addClass('active');
        $('.menu_overlay').addClass('active');
        $('.hamburger').addClass('active');
        $('body').addClass('menu-open');
        menuActive = true;
        console.log('Menu opened');
    }
    
    function closeMenu() {
        console.log('Closing menu...');
        $('.menu').removeClass('active');
        $('.menu_overlay').removeClass('active');
        $('.hamburger').removeClass('active');
        $('body').removeClass('menu-open');
        menuActive = false;
        $(document).trigger('menuClosed'); // Trigger custom event
        console.log('Menu closed');
    }
    
    // Make functions globally available
    window.toggleMobileMenu = toggleMobileMenu;
    window.openMobileMenu = openMenu;
    window.closeMobileMenu = closeMenu;
    
    // Initialize when document is ready
    $(document).ready(function() {
        console.log('Mobile menu script loaded');
        console.log('Menu elements found:', $('.menu').length);
        console.log('Hamburger elements found:', $('.hamburger').length);
        console.log('Overlay elements found:', $('.menu_overlay').length);
        console.log('Accordion toggles found:', $('.accordion-toggle').length);
        console.log('Menu items with accordion found:', $('.menu-item-with-accordion').length);
        
        // Check if elements exist
        if ($('.menu').length === 0) {
            console.error('Menu element not found!');
        }
        if ($('.hamburger').length === 0) {
            console.error('Hamburger element not found!');
        }
        if ($('.menu_overlay').length === 0) {
            console.error('Menu overlay element not found!');
        }
        
        // Handle hamburger click
        $('.hamburger').on('click', function(e) {
            e.preventDefault();
            console.log('Hamburger clicked via jQuery!');
            toggleMobileMenu();
        });
        
        // Close menu when clicking on overlay
        $('.menu_overlay').on('click', function() {
            if (menuActive) {
                closeMenu();
            }
        });
        
        // Close menu when clicking on menu links (except accordion toggles)
        $('.menu_content a').not('.accordion-toggle').on('click', function() {
            if (menuActive) {
                closeMenu();
            }
        });
        
        // Handle accordion toggle clicks
        $('.accordion-toggle').on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            var $toggle = $(this);
            var $accordionItem = $toggle.closest('.menu-item-with-accordion');
            var $content = $accordionItem.find('.accordion-content');
            
            var isExpanded = $toggle.attr('aria-expanded') === 'true';
            
            // Close all other accordions
            $('.accordion-toggle').not($toggle).attr('aria-expanded', 'false');
            $('.accordion-content').not($content).removeClass('open');
            
            // Toggle current accordion
            if (isExpanded) {
                $toggle.attr('aria-expanded', 'false');
                $content.removeClass('open');
            } else {
                $toggle.attr('aria-expanded', 'true');
                $content.addClass('open');
            }
        });
        
        // Handle main link clicks - close menu after navigation
        $('.menu-item-header .main-link').on('click', function() {
            if (menuActive) {
                closeMenu();
            }
        });
        
        // Close accordions when menu closes
        $(document).on('menuClosed', function() {
            $('.accordion-toggle').attr('aria-expanded', 'false');
            $('.accordion-content').removeClass('open');
        });
    });
    
})();
