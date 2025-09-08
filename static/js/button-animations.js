/* Button Animation Enhancements */

(function() {
    'use strict';

    // Add loading state to buttons when forms are submitted
    function initButtonLoadingStates() {
        // Find all forms with buttons
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            
            if (submitButton) {
                form.addEventListener('submit', function() {
                    // Add loading class
                    submitButton.classList.add('loading');
                    submitButton.disabled = true;
                    
                    // Change text if possible
                    if (submitButton.tagName === 'BUTTON') {
                        const originalText = submitButton.textContent;
                        submitButton.setAttribute('data-original-text', originalText);
                        submitButton.textContent = 'Отправка...';
                    }
                });
            }
        });
    }

    // Add ripple effect to buttons
    function initRippleEffect() {
        const buttons = document.querySelectorAll('.btn, button, .button, .btn-hero');
        
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                // Create ripple element
                const ripple = document.createElement('span');
                const rect = button.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: ripple 0.6s linear;
                    pointer-events: none;
                `;
                
                // Add ripple to button
                button.style.position = 'relative';
                button.style.overflow = 'hidden';
                button.appendChild(ripple);
                
                // Remove ripple after animation
                setTimeout(() => {
                    if (ripple.parentNode) {
                        ripple.parentNode.removeChild(ripple);
                    }
                }, 600);
            });
        });
    }

    // Add CSS for ripple animation
    function addRippleCSS() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Initialize all button enhancements
    function init() {
        addRippleCSS();
        initButtonLoadingStates();
        initRippleEffect();
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();







