document.addEventListener('DOMContentLoaded', () => {
    const header = document.getElementById('main-header');

    // Sticky Header Scroll Effect
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // Add to Cart Logic (Basic feedback)
    const cartBtns = document.querySelectorAll('.add-to-cart');
    const cartBadge = document.querySelector('.badge');
    let cartCount = 0;

    cartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            cartCount++;
            cartBadge.textContent = cartCount;

            // Subtle feedback
            const originalText = btn.textContent;
            btn.textContent = 'Added!';
            btn.style.background = '#4cd964';

            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        });
    });

    // --- Shop Page Specific Logic ---
    const priceSlider = document.getElementById('price-range');
    const priceValue = document.getElementById('price-value');
    const mobileFilterBtn = document.getElementById('mobile-filter-btn');
    const closeFiltersBtn = document.getElementById('close-filters');
    const filtersSidebar = document.getElementById('filters-sidebar');
    const wishlistBtns = document.querySelectorAll('.wishlist-btn');
    const sizeBtns = document.querySelectorAll('.size-btn');
    const clearFiltersBtn = document.getElementById('clear-filters');

    // Price Range Display
    if (priceSlider && priceValue) {
        priceSlider.addEventListener('input', (e) => {
            priceValue.textContent = `$${e.target.value}`;
        });
    }

    // Mobile Filter Drawer Toggle
    if (mobileFilterBtn && filtersSidebar) {
        mobileFilterBtn.addEventListener('click', () => {
            filtersSidebar.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        });
    }

    if (closeFiltersBtn && filtersSidebar) {
        closeFiltersBtn.addEventListener('click', () => {
            filtersSidebar.classList.remove('active');
            document.body.style.overflow = ''; // Restore scrolling
        });
    }

    // Wishlist Toggle
    wishlistBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            btn.classList.toggle('active');

            // Icon feedback (Simple)
            const icon = btn.querySelector('i');
            if (btn.classList.contains('active')) {
                icon.setAttribute('fill', '#ff3b30');
                icon.style.color = '#ff3b30';
            } else {
                icon.removeAttribute('fill');
                icon.style.color = '';
            }
        });
    });

    // Size Selection
    sizeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            sizeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Clear Filters
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            // Uncheck all checkboxes
            document.querySelectorAll('.filters-sidebar input[type="checkbox"]').forEach(cb => {
                cb.checked = false;
            });

            // Reset price slider
            if (priceSlider && priceValue) {
                priceSlider.value = 500;
                priceValue.textContent = '$500';
            }

            // Reset size selection
            sizeBtns.forEach(b => b.classList.remove('active'));
            if (sizeBtns.length > 1) sizeBtns[1].classList.add('active'); // Default to size 8 as in HTML
        });
    }

    // Simple scroll animation for reveal
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('reveal');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.section, .category-card, .product-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.8s ease-out';
        observer.observe(el);
    });

    // Dynamic class injection for reveal effect
    const style = document.createElement('style');
    style.innerHTML = `
        .reveal {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    `;
    document.head.appendChild(style);
});

// Cart Item Removal Confirmation
function confirmRemove(button) {
    if (confirm("Are you sure you want to remove this item from your cart?")) {
        const cartItem = button.closest('.cart-item');
        if (cartItem) {
            cartItem.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            cartItem.style.opacity = '0';
            cartItem.style.transform = 'translateY(20px)';

            setTimeout(() => {
                cartItem.remove();
                // Check if cart is empty
                const remainingItems = document.querySelectorAll('.cart-item');
                if (remainingItems.length === 0) {
                    const cartWrapper = document.querySelector('.cart-items-wrapper');
                    if (cartWrapper) {
                        cartWrapper.innerHTML = '<div class="text-center py-5"><i data-lucide="shopping-bag" class="mb-3" style="width: 48px; height: 48px; color: #ccc;"></i><h4 class="text-muted">Your cart is empty</h4><a href="shop.html" class="btn btn-dark mt-3 rounded-pill px-4">See what\'s new</a></div>';
                        lucide.createIcons();
                    }
                }
            }, 500);
        }
    }
}

// Checkout Form Submission
document.addEventListener('DOMContentLoaded', () => {
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function (e) {
            e.preventDefault();
            if (this.checkValidity()) {
                alert('Thank you! Your order has been placed successfully.');
                window.location.href = 'index.html';
            } else {
                this.classList.add('was-validated');
            }
        });
    }
});
