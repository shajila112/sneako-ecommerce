document.addEventListener('DOMContentLoaded', () => {
    const header = document.getElementById('main-header');

    // --- Seed Data for Reviews ---
    if (!localStorage.getItem('sneako_reviews')) {
        const seedReviews = [
            {
                id: 1001,
                productName: "Nike Air Max 270",
                productImg: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=100",
                userName: "Alex Johnson",
                rating: 5,
                title: "Ultimate Comfort",
                text: "These are by far the most comfortable sneakers I've ever owned. The air unit provides amazing cushioning for all-day wear.",
                date: "Nov 12, 2025",
                verified: true,
                hidden: false
            },
            {
                id: 1002,
                productName: "Adidas Ultraboost",
                productImg: "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&q=80&w=100",
                userName: "Sarah Miller",
                rating: 4,
                title: "Stylish but Pricey",
                text: "Love the look and the boost foam is incredible. However, the price point is a bit high compared to other models.",
                date: "Dec 05, 2025",
                verified: true,
                hidden: false
            },
            {
                id: 1003,
                productName: "Puma RS-X3",
                productImg: "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&q=80&w=100",
                userName: "Chris Evans",
                rating: 5,
                title: "Great Design",
                text: "The chunkiness and colorway of these Pumas are spot on. Very happy with the purchase!",
                date: "Jan 10, 2026",
                verified: true,
                hidden: false
            }
        ];
        localStorage.setItem('sneako_reviews', JSON.stringify(seedReviews));
    }

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

// Checkout Wallet Logic
document.addEventListener('DOMContentLoaded', () => {
    const useWalletCheckbox = document.getElementById('useWallet');
    const walletBalance = 125.50; // Mock balance

    if (useWalletCheckbox) {
        const totalElement = document.getElementById('checkout-total');
        const deductionElement = document.getElementById('wallet-deduction-amount');
        const remainingElement = document.getElementById('remaining-payable');
        const balanceDisplay = document.getElementById('wallet-balance-display');
        const walletMessage = document.getElementById('wallet-message');

        const updateWalletPayable = () => {
            if (!totalElement) return;

            const orderTotalText = totalElement.textContent.replace('$', '').replace(',', '');
            const orderTotal = parseFloat(orderTotalText);
            let deduction = 0;
            let remaining = orderTotal;

            if (useWalletCheckbox.checked) {
                deduction = Math.min(orderTotal, walletBalance);
                remaining = orderTotal - deduction;
            }

            if (deductionElement) deductionElement.textContent = `-$${deduction.toFixed(2)}`;
            if (remainingElement) remainingElement.textContent = `$${remaining.toFixed(2)}`;

            if (walletMessage) {
                if (deduction >= orderTotal) {
                    walletMessage.textContent = `Wallet covers the full amount. No additional payment needed.`;
                } else if (useWalletCheckbox.checked) {
                    walletMessage.textContent = `Value updated based on your $${walletBalance.toFixed(2)} balance.`;
                } else {
                    walletMessage.textContent = `Use your wallet balance for this purchase.`;
                }
            }
        };

        useWalletCheckbox.addEventListener('change', updateWalletPayable);

        // Initial set
        if (balanceDisplay) balanceDisplay.textContent = `Bal: $${walletBalance.toFixed(2)}`;
        updateWalletPayable();
    }
});

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

// Profile Edit Form Handling
document.addEventListener('DOMContentLoaded', () => {
    const editProfileForm = document.getElementById('edit-profile-form');
    if (editProfileForm) {
        editProfileForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // Simulate profile update
            const newName = document.getElementById('edit-name').value;
            const newEmail = document.getElementById('edit-email').value;
            const newPhone = document.getElementById('edit-phone').value;

            // Update profile view (UI only)
            const profileNameElements = document.querySelectorAll('.profile-sidebar h5, .profile-card p.fw-medium:nth-of-type(1)');
            const profileEmailElements = document.querySelectorAll('.profile-sidebar p.small, .profile-card p.fw-medium:nth-of-type(2)');
            const profilePhoneElements = document.querySelectorAll('.profile-card p.fw-medium:nth-of-type(3)');

            // We need to be specific about which indices to update
            // Side bar
            const sidebarName = document.querySelector('.profile-sidebar h5');
            const sidebarEmail = document.querySelector('.profile-sidebar p.small');

            // Profile Info Section
            const profileInfoName = document.querySelector('#profile-info .row .col-md-6:nth-child(1) p');
            const profileInfoEmail = document.querySelector('#profile-info .row .col-md-6:nth-child(2) p');
            const profileInfoPhone = document.querySelector('#profile-info .row .col-md-6:nth-child(3) p');

            if (sidebarName) sidebarName.textContent = newName;
            if (sidebarEmail) sidebarEmail.textContent = newEmail;
            if (profileInfoName) profileInfoName.textContent = newName;
            if (profileInfoEmail) profileInfoEmail.textContent = newEmail;
            if (profileInfoPhone) profileInfoPhone.textContent = newPhone;

            // Success feedback
            alert('Profile updated successfully!');

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
            if (modal) modal.hide();
        });
    }
});

// Order Details Modal Population
document.addEventListener('DOMContentLoaded', () => {
    const viewOrderLinks = document.querySelectorAll('.view-order-details');
    const modalOrderId = document.getElementById('modal-order-id');
    const modalStatus = document.getElementById('modal-status');
    const modalSubtotal = document.getElementById('modal-subtotal');
    const modalTotal = document.getElementById('modal-total');

    viewOrderLinks.forEach(link => {
        link.addEventListener('click', function () {
            const data = this.dataset;
            if (modalOrderId) modalOrderId.textContent = data.orderId;
            if (modalTotal) modalTotal.textContent = data.orderTotal;
            if (modalSubtotal) modalSubtotal.textContent = data.orderTotal;


            if (modalStatus) {
                modalStatus.textContent = data.orderStatus;
                modalStatus.className = `badge rounded-pill border bg-${data.orderStatus.toLowerCase()}-subtle text-${data.orderStatus.toLowerCase()}`;
                if (data.orderStatus === 'Shipped') modalStatus.classList.replace('text-shipped', 'text-info');
            }
        });
    });

});
// Add New Address Handling
document.addEventListener('DOMContentLoaded', () => {
    const addAddressForm = document.getElementById('add-address-form');
    const addressGrid = document.getElementById('address-grid');

    if (addAddressForm && addressGrid) {
        addAddressForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // Get form values
            const type = document.getElementById('address-type').value;
            const street = document.getElementById('address-street').value;
            const city = document.getElementById('address-city').value;
            const state = document.getElementById('address-state').value;
            const zip = document.getElementById('address-zip').value;
            const country = document.getElementById('address-country').value;
            const isDefault = document.getElementById('set-default-address').checked;

            // Create new address card HTML
            const col = document.createElement('div');
            col.className = 'col-md-6';

            let defaultBadge = '';
            let activeClass = '';

            if (isDefault) {
                // Remove default from others
                document.querySelectorAll('#address-grid .address-card').forEach(card => {
                    card.classList.remove('active-address');
                    const badge = card.querySelector('.badge.bg-dark');
                    if (badge) badge.remove();
                });
                defaultBadge = '<span class="badge bg-dark rounded-pill mb-3">Default</span>';
                activeClass = 'active-address';
            }

            col.innerHTML = `
                <div class="address-card p-4 rounded-4 border position-relative ${activeClass}"
                    data-type="${type}" data-street="${street}" 
                    data-city="${city}" data-state="${state}" 
                    data-zip="${zip}" data-country="${country}">
                    <div class="position-absolute top-0 end-0 m-3 d-flex gap-2">
                        <button class="btn btn-link text-muted p-0 edit-address-btn" title="Edit"
                            data-bs-toggle="modal" data-bs-target="#editAddressModal"><i data-lucide="edit-2" style="width: 16px;"></i></button>
                        <button class="btn btn-link text-danger p-0 delete-address-btn" title="Delete"><i data-lucide="trash-2" style="width: 16px;"></i></button>
                    </div>
                    ${defaultBadge}
                    <h6 class="fw-bold mb-2">${type}</h6>
                    <p class="text-muted small mb-0">
                        ${street},<br>
                        ${city}, ${state} ${zip},<br>
                        ${country}
                    </p>
                </div>
            `;

            // Append to grid
            addressGrid.appendChild(col);

            // Re-initialize icons for the new card
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }

            // Success feedback
            alert('Address added successfully!');

            // Reset form and close modal
            addAddressForm.reset();
            const modal = bootstrap.Modal.getInstance(document.getElementById('addAddressModal'));
            if (modal) modal.hide();
        });
    }
});

// Edit Address Handling
document.addEventListener('DOMContentLoaded', () => {
    const editAddressForm = document.getElementById('edit-address-form');
    let currentEditingCard = null;

    // Handle Edit Button Clicks (Delegation for dynamic cards)
    document.addEventListener('click', function (e) {
        if (e.target.closest('.edit-address-btn')) {
            const btn = e.target.closest('.edit-address-btn');
            currentEditingCard = btn.closest('.address-card');

            // Populate Modal
            document.getElementById('edit-address-type').value = currentEditingCard.getAttribute('data-type');
            document.getElementById('edit-address-street').value = currentEditingCard.getAttribute('data-street');
            document.getElementById('edit-address-city').value = currentEditingCard.getAttribute('data-city');
            document.getElementById('edit-address-state').value = currentEditingCard.getAttribute('data-state');
            document.getElementById('edit-address-zip').value = currentEditingCard.getAttribute('data-zip');
            document.getElementById('edit-address-country').value = currentEditingCard.getAttribute('data-country');
            document.getElementById('edit-set-default-address').checked = currentEditingCard.classList.contains('active-address');
        }
    });

    // Handle Delete Button Clicks (Delegation for dynamic cards)
    document.addEventListener('click', function (e) {
        if (e.target.closest('.delete-address-btn')) {
            const btn = e.target.closest('.delete-address-btn');
            const card = btn.closest('.col-md-6'); // The container column

            if (confirm('Are you sure you want to delete this address?')) {
                card.remove();
                alert('Address deleted successfully!');
            }
        }
    });

    if (editAddressForm) {
        editAddressForm.addEventListener('submit', function (e) {
            e.preventDefault();

            if (!currentEditingCard) return;

            // Get form values
            const type = document.getElementById('edit-address-type').value;
            const street = document.getElementById('edit-address-street').value;
            const city = document.getElementById('edit-address-city').value;
            const state = document.getElementById('edit-address-state').value;
            const zip = document.getElementById('edit-address-zip').value;
            const country = document.getElementById('edit-address-country').value;
            const isDefault = document.getElementById('edit-set-default-address').checked;

            // Update data attributes
            currentEditingCard.setAttribute('data-type', type);
            currentEditingCard.setAttribute('data-street', street);
            currentEditingCard.setAttribute('data-city', city);
            currentEditingCard.setAttribute('data-state', state);
            currentEditingCard.setAttribute('data-zip', zip);
            currentEditingCard.setAttribute('data-country', country);

            // Update UI
            currentEditingCard.querySelector('h6').textContent = type;
            currentEditingCard.querySelector('p').innerHTML = `
                ${street},<br>
                ${city}, ${state} ${zip},<br>
                ${country}
            `;

            if (isDefault) {
                // Remove default from others
                document.querySelectorAll('#address-grid .address-card').forEach(card => {
                    card.classList.remove('active-address');
                    const badge = card.querySelector('.badge.bg-dark');
                    if (badge) badge.remove();
                });

                // Set as default
                currentEditingCard.classList.add('active-address');
                if (!currentEditingCard.querySelector('.badge.bg-dark')) {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-dark rounded-pill mb-3';
                    badge.textContent = 'Default';
                    currentEditingCard.insertBefore(badge, currentEditingCard.querySelector('h6'));
                }
            } else {
                currentEditingCard.classList.remove('active-address');
                const badge = currentEditingCard.querySelector('.badge.bg-dark');
                if (badge) badge.remove();
            }

            // Success feedback
            alert('Address updated successfully!');

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editAddressModal'));
            if (modal) modal.hide();
        });
    }


    // --- Write Review Logic ---
    const stars = document.querySelectorAll('.star-icon');
    const ratingInput = document.getElementById('review-rating');

    // Pre-populate if editing
    const urlParamsSearch = new URLSearchParams(window.location.search);
    const editId = urlParamsSearch.get('edit');

    if (editId) {
        const storedReviews = JSON.parse(localStorage.getItem('sneako_reviews') || '[]');
        const reviewToEdit = storedReviews.find(r => r.id == editId);

        if (reviewToEdit) {
            document.querySelector('.review-form-card h3').textContent = 'Edit Your Review';
            document.getElementById('review-title').value = reviewToEdit.title;
            document.getElementById('review-text').value = reviewToEdit.text;
            ratingInput.value = reviewToEdit.rating;
            highlightStars(reviewToEdit.rating);

            // Update product info if possible
            if (document.getElementById('product-name')) document.getElementById('product-name').textContent = reviewToEdit.productName;
            if (document.getElementById('product-img')) document.getElementById('product-img').src = reviewToEdit.productImg;
        }
    }

    stars.forEach(star => {
        star.addEventListener('mouseover', function () {
            const value = this.getAttribute('data-value');
            highlightStars(value);
        });

        star.addEventListener('mouseout', function () {
            const currentRating = ratingInput.value;
            highlightStars(currentRating);
        });

        star.addEventListener('click', function () {
            const value = this.getAttribute('data-value');
            ratingInput.value = value;
            highlightStars(value);
            document.querySelector('.rating-error').style.setProperty('display', 'none', 'important');
        });
    });

    function highlightStars(value) {
        stars.forEach(star => {
            const starValue = star.getAttribute('data-value');
            if (starValue <= value) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    const writeReviewForm = document.getElementById('write-review-form');
    if (writeReviewForm) {
        writeReviewForm.addEventListener('submit', function (e) {
            e.preventDefault();

            if (ratingInput.value === "0") {
                document.querySelector('.rating-error').style.setProperty('display', 'block', 'important');
                return;
            }

            const urlParams = new URLSearchParams(window.location.search);
            const productName = document.getElementById('product-name') ? document.getElementById('product-name').textContent : (urlParams.get('product') || "Air Jordan 1 Retro High");
            const productImg = document.getElementById('product-img') ? document.getElementById('product-img').src : (urlParams.get('img') || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&q=80&w=200");

            const existingReviews = JSON.parse(localStorage.getItem('sneako_reviews') || '[]');

            if (editId) {
                // Update existing review
                const index = existingReviews.findIndex(r => r.id == editId);
                if (index !== -1) {
                    existingReviews[index].rating = parseInt(ratingInput.value);
                    existingReviews[index].title = document.getElementById('review-title').value;
                    existingReviews[index].text = document.getElementById('review-text').value;
                    existingReviews[index].date = "Edited on " + new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
                }
            } else {
                // Prepend new review
                const newReview = {
                    id: Date.now(),
                    productName: productName,
                    productImg: productImg,
                    rating: parseInt(ratingInput.value),
                    title: document.getElementById('review-title').value,
                    text: document.getElementById('review-text').value,
                    date: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })
                };
                existingReviews.unshift(newReview);
            }

            localStorage.setItem('sneako_reviews', JSON.stringify(existingReviews));

            alert(editId ? 'Your review has been updated successfully!' : 'Thank you! Your review has been submitted successfully.');
            window.location.href = 'profile.html?tab=reviews';
        });
    }

    const productReviewForm = document.getElementById('product-review-form');
    if (productReviewForm) {
        productReviewForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const ratingInputSelected = this.querySelector('input[name="rating"]:checked');
            if (!ratingInputSelected) {
                alert('Please select a rating.');
                return;
            }

            const productName = document.querySelector('h1').textContent;
            const productImg = document.getElementById('main-product-img').src;
            const comment = document.getElementById('reviewComment').value;

            const existingReviews = JSON.parse(localStorage.getItem('sneako_reviews') || '[]');

            const userName = localStorage.getItem('sneako_user_name') || 'Verified Customer';

            const newReview = {
                id: Date.now(),
                productName: productName,
                productImg: productImg,
                userName: userName,
                rating: parseInt(ratingInputSelected.value),
                title: "Reviewed from Product Page",
                text: comment,
                date: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
                verified: true,
                hidden: false
            };

            existingReviews.unshift(newReview);
            localStorage.setItem('sneako_reviews', JSON.stringify(existingReviews));

            alert('Thank you! Your review has been submitted successfully.');
            window.location.href = 'profile.html?tab=reviews';
        });
    }

    // --- Dynamic Review Loading on Profile Page ---
    const reviewListContainer = document.getElementById('dynamic-review-list');
    const reviewCountBadge = document.getElementById('review-count');

    function renderReviews() {
        if (!reviewListContainer) return;

        const storedReviews = JSON.parse(localStorage.getItem('sneako_reviews') || '[]');
        const visibleReviews = storedReviews.filter(r => !r.hidden);

        // Update Counter
        if (reviewCountBadge) {
            reviewCountBadge.textContent = `${visibleReviews.length} ${visibleReviews.length === 1 ? 'Review' : 'Reviews'}`;
        }

        reviewListContainer.innerHTML = '';

        if (visibleReviews.length === 0) {
            reviewListContainer.innerHTML = `
                <div class="text-center py-5">
                    <i data-lucide="message-square" class="text-muted mb-3" style="width: 48px; height: 48px;"></i>
                    <h6 class="fw-bold">No reviews yet</h6>
                    <p class="text-muted small">Share your thoughts on products you've purchased.</p>
                    <a href="shop.html" class="btn btn-outline-dark btn-sm rounded-pill mt-2">Go to Shop</a>
                </div>
            `;
        } else {
            visibleReviews.forEach(review => {
                const reviewItem = document.createElement('div');
                reviewItem.className = 'review-item-card p-4 rounded-4 border mb-3 bg-white shadow-sm';

                let starsHtml = '';
                for (let i = 1; i <= 5; i++) {
                    const isFilled = i <= review.rating;
                    starsHtml += `<i data-lucide="star" style="width: 14px; ${isFilled ? 'fill: currentColor;' : ''}"></i>`;
                }

                reviewItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div class="d-flex align-items-center">
                            <img src="${review.productImg}" alt="${review.productName}" class="rounded-3 me-3"
                                style="width: 60px; height: 60px; object-fit: cover;">
                            <div>
                                <h6 class="fw-bold mb-1">${review.productName} ${review.verified ? `<span class="verified-badge ms-2"><i data-lucide="check-circle" style="width: 10px;"></i> Verified</span>` : ''}</h6>
                                <p class="text-muted small mb-0">${review.title}</p>
                            </div>
                        </div>
                        <div class="text-end">
                            <div class="text-warning mb-1">
                                ${starsHtml}
                            </div>
                            <span class="text-muted extra-small">${review.date}</span>
                        </div>
                    </div>
                    <p class="text-muted small mb-0" style="font-style: italic;">
                        "${review.text}"
                    </p>
                    <div class="mt-3 text-end d-flex justify-content-end gap-2">
                        <button class="btn btn-outline-dark btn-sm rounded-pill px-3 edit-review-btn" data-id="${review.id}">Edit</button>
                        <button class="btn btn-outline-danger btn-sm rounded-pill px-3 delete-review-btn" data-id="${review.id}">Delete</button>
                    </div>
                `;
                reviewListContainer.appendChild(reviewItem);
            });
        }

        if (typeof lucide !== 'undefined') lucide.createIcons();
    }

    // Initial render
    renderReviews();

    // Edit Review Modal Logic
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('edit-review-btn')) {
            const reviewId = e.target.getAttribute('data-id');
            const storedReviews = JSON.parse(localStorage.getItem('sneako_reviews') || '[]');
            const review = storedReviews.find(r => r.id == reviewId);

            if (review) {
                document.getElementById('edit-review-id').value = review.id;
                document.getElementById('edit-review-title').value = review.title;
                document.getElementById('edit-review-text').value = review.text;

                // Set radio star
                const radio = document.querySelector(`input[name="edit-rating"][value="${review.rating}"]`);
                if (radio) radio.checked = true;

                const modal = new bootstrap.Modal(document.getElementById('editReviewModal'));
                modal.show();
            }
        }

        if (e.target.classList.contains('delete-review-btn')) {
            const reviewId = e.target.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this review?')) {
                let storedReviews = JSON.parse(localStorage.getItem('sneako_reviews') || '[]');
                storedReviews = storedReviews.filter(r => r.id != reviewId);
                localStorage.setItem('sneako_reviews', JSON.stringify(storedReviews));
                renderReviews();
            }
        }
    });

    const editReviewForm = document.getElementById('edit-review-form');
    if (editReviewForm) {
        editReviewForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const reviewId = document.getElementById('edit-review-id').value;
            const title = document.getElementById('edit-review-title').value;
            const text = document.getElementById('edit-review-text').value;
            const ratingInput = this.querySelector('input[name="edit-rating"]:checked');

            if (!ratingInput) {
                alert('Please select a rating');
                return;
            }

            let storedReviews = JSON.parse(localStorage.getItem('sneako_reviews') || '[]');
            const index = storedReviews.findIndex(r => r.id == reviewId);

            if (index !== -1) {
                storedReviews[index].title = title;
                storedReviews[index].text = text;
                storedReviews[index].rating = parseInt(ratingInput.value);
                storedReviews[index].date = "Edited on " + new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });

                localStorage.setItem('sneako_reviews', JSON.stringify(storedReviews));

                const modal = bootstrap.Modal.getInstance(document.getElementById('editReviewModal'));
                if (modal) modal.hide();

                renderReviews();
                alert('Review updated successfully!');
            }
        });
    }

    // Handle Tab Activation via URL
    const urlParamsFinal = new URLSearchParams(window.location.search);
    const activeTab = urlParamsFinal.get('tab');
    if (activeTab) {
        const tabTrigger = document.querySelector(`.nav-link[href="#${activeTab}"]`);
        if (tabTrigger) {
            const tab = new bootstrap.Tab(tabTrigger);
            tab.show();
        }
    }

    // --- Dynamic Product Detail Reviews ---
    const productReviewContainer = document.getElementById('dynamic-product-reviews');
    if (productReviewContainer) {
        function renderProductPageReviews() {
            const currentProductName = document.querySelector('h1')?.textContent.trim();
            if (!currentProductName) return;

            const storedReviews = JSON.parse(localStorage.getItem('sneako_reviews') || '[]');
            const productReviews = storedReviews.filter(r => r.productName === currentProductName && !r.hidden);

            if (productReviews.length > 0) {
                productReviewContainer.innerHTML = ''; // Clear default static reviews
                productReviews.forEach(review => {
                    let starsHtml = '';
                    for (let i = 1; i <= 5; i++) {
                        starsHtml += `<i data-lucide="star" class="${i <= review.rating ? 'text-warning fill-warning' : 'text-muted'}" style="width: 16px; height: 16px;"></i>`;
                    }

                    const reviewHtml = `
                        <div class="review-item-card mb-4 pb-4 border-bottom">
                            <div class="d-flex justify-content-between align-items-start mb-3">
                                <div>
                                    <h6 class="fw-bold mb-1">${review.userName || 'Verified Customer'}</h6>
                                    <div class="d-flex gap-1 mb-2">${starsHtml}</div>
                                </div>
                                <span class="text-muted small">${review.date}</span>
                            </div>
                            <p class="text-muted small mb-0">${review.text}</p>
                            ${review.verified ? '<span class="badge bg-success-subtle text-success border border-success-subtle rounded-pill mt-2" style="font-size: 0.65rem;"><i data-lucide="check-circle" style="width: 10px; height: 10px;" class="me-1"></i> Verified Purchase</span>' : ''}
                        </div>
                    `;
                    productReviewContainer.insertAdjacentHTML('beforeend', reviewHtml);
                });
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
        }
        renderProductPageReviews();
    }

    // --- Order Cancellation Logic ---
    const cancelOrderConfirmedBtn = document.querySelector('#cancelOrderModal .btn-danger');
    if (cancelOrderConfirmedBtn) {
        cancelOrderConfirmedBtn.addEventListener('click', function () {
            // In a real app, you would send an API request here
            alert('Order #ORD-2026-105 has been cancelled successfully.');
            
            // Redirect to orders page or refresh to show updated status
            if (window.location.pathname.includes('order-details.html')) {
                window.location.href = 'orders.html';
            } else {
                location.reload();
            }
        });
    }

    // Initialize Lucide icons for any dynamically added content
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});
