/* Modern How It Works Interactive Component */

(function() {
    'use strict';

    class HowItWorks {
        constructor() {
            this.currentStep = 0;
            this.steps = [];
            this.autoPlayInterval = null;
            this.autoPlayDelay = 4000;
            this.isUserInteracting = false;
            
            this.init();
        }

        init() {
            this.setupElements();
            this.setupEventListeners();
            this.startAutoPlay();
            this.observeSteps();
        }

        setupElements() {
            this.container = document.querySelector('.how-it-works');
            if (!this.container) return;

            this.steps = Array.from(document.querySelectorAll('.step-item'));
            this.prevBtn = document.querySelector('.step-nav-btn[data-action="prev"]');
            this.nextBtn = document.querySelector('.step-nav-btn[data-action="next"]');
            this.dots = Array.from(document.querySelectorAll('.step-dot'));
            
            // Add data attributes for navigation
            if (this.prevBtn) this.prevBtn.setAttribute('data-action', 'prev');
            if (this.nextBtn) this.nextBtn.setAttribute('data-action', 'next');
        }

        setupEventListeners() {
            // Navigation buttons
            if (this.prevBtn) {
                this.prevBtn.addEventListener('click', () => this.previousStep());
            }
            if (this.nextBtn) {
                this.nextBtn.addEventListener('click', () => this.nextStep());
            }

            // Dots navigation
            this.dots.forEach((dot, index) => {
                dot.addEventListener('click', () => this.goToStep(index));
            });

            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft') this.previousStep();
                if (e.key === 'ArrowRight') this.nextStep();
            });

            // Touch/swipe support
            this.setupTouchEvents();

            // Pause auto-play on user interaction
            this.container.addEventListener('mouseenter', () => this.pauseAutoPlay());
            this.container.addEventListener('mouseleave', () => this.resumeAutoPlay());
        }

        setupTouchEvents() {
            let startX = 0;
            let startY = 0;

            this.container.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
            });

            this.container.addEventListener('touchend', (e) => {
                if (!startX || !startY) return;

                const endX = e.changedTouches[0].clientX;
                const endY = e.changedTouches[0].clientY;
                const diffX = startX - endX;
                const diffY = startY - endY;

                // Only trigger if horizontal swipe is more significant than vertical
                if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                    if (diffX > 0) {
                        this.nextStep();
                    } else {
                        this.previousStep();
                    }
                }

                startX = 0;
                startY = 0;
            });
        }

        observeSteps() {
            if (!window.IntersectionObserver) return;

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            this.steps.forEach(step => {
                observer.observe(step);
            });
        }

        goToStep(stepIndex) {
            if (stepIndex < 0 || stepIndex >= this.steps.length) return;
            
            this.isUserInteracting = true;
            this.currentStep = stepIndex;
            this.updateDisplay();
            this.resetAutoPlay();
        }

        nextStep() {
            const nextIndex = (this.currentStep + 1) % this.steps.length;
            this.goToStep(nextIndex);
        }

        previousStep() {
            const prevIndex = this.currentStep === 0 ? this.steps.length - 1 : this.currentStep - 1;
            this.goToStep(prevIndex);
        }

        updateDisplay() {
            // Update steps
            this.steps.forEach((step, index) => {
                step.classList.remove('active', 'completed');
                
                if (index < this.currentStep) {
                    step.classList.add('completed');
                } else if (index === this.currentStep) {
                    step.classList.add('active');
                }
            });

            // Update dots
            this.dots.forEach((dot, index) => {
                dot.classList.remove('active', 'completed');
                
                if (index < this.currentStep) {
                    dot.classList.add('completed');
                } else if (index === this.currentStep) {
                    dot.classList.add('active');
                }
            });

            // Update navigation buttons
            if (this.prevBtn) {
                this.prevBtn.disabled = false;
            }
            if (this.nextBtn) {
                this.nextBtn.disabled = false;
            }

            // Add step transition animation
            this.animateStepTransition();
        }

        animateStepTransition() {
            const activeStep = this.steps[this.currentStep];
            if (!activeStep) return;

            // Add pulse animation to active step
            activeStep.style.animation = 'none';
            activeStep.offsetHeight; // Trigger reflow
            activeStep.style.animation = 'stepAppear 0.6s ease-out';

            // Animate step number
            const stepNumber = activeStep.querySelector('.step-number');
            if (stepNumber) {
                stepNumber.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    stepNumber.style.transform = 'scale(1.1)';
                }, 200);
            }

            // Animate step icon
            const stepIcon = activeStep.querySelector('.step-icon');
            if (stepIcon) {
                stepIcon.style.animation = 'none';
                stepIcon.offsetHeight;
                stepIcon.style.animation = 'stepAppear 0.4s ease-out 0.2s both';
            }
        }

        startAutoPlay() {
            this.autoPlayInterval = setInterval(() => {
                if (!this.isUserInteracting) {
                    this.nextStep();
                }
            }, this.autoPlayDelay);
        }

        pauseAutoPlay() {
            if (this.autoPlayInterval) {
                clearInterval(this.autoPlayInterval);
            }
        }

        resumeAutoPlay() {
            if (!this.isUserInteracting) {
                this.startAutoPlay();
            }
        }

        resetAutoPlay() {
            this.pauseAutoPlay();
            setTimeout(() => {
                this.isUserInteracting = false;
                this.resumeAutoPlay();
            }, 10000); // Resume auto-play after 10 seconds
        }

        destroy() {
            this.pauseAutoPlay();
            // Remove event listeners if needed
        }
    }

    // Initialize when DOM is ready
    function initHowItWorks() {
        if (document.querySelector('.how-it-works')) {
            new HowItWorks();
        }
    }

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHowItWorks);
    } else {
        initHowItWorks();
    }

    // Export for potential external use
    window.HowItWorks = HowItWorks;

})();




