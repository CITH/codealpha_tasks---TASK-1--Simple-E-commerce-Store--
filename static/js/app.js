/* NovaCart Javascript Functionality App */

// Utility: Retrieve CSRF Token from Cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].strip ? cookies[i].strip() : cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Global Toast System Manager
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    // Choose border color based on status
    if (type === 'error') {
        toast.style.borderLeftColor = 'var(--error)';
    } else if (type === 'warning') {
        toast.style.borderLeftColor = 'var(--warning)';
    } else {
        toast.style.borderLeftColor = 'var(--primary)';
    }

    toast.innerHTML = `
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Helper: Show/Hide global loading spinner overlay
function showSpinner(show = true) {
    const overlay = document.getElementById('spinner-overlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------
    // 1. Mobile Menu Toggle
    // ----------------------------------------------------
    const menuToggle = document.getElementById('menu-toggle');
    const navLinks = document.getElementById('nav-links');
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // ----------------------------------------------------
    // 2. Scroll to Top Button Action
    // ----------------------------------------------------
    const scrollTopBtn = document.getElementById('scroll-top-btn');
    if (scrollTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 405) {
                scrollTopBtn.style.display = 'flex';
            } else {
                scrollTopBtn.style.display = 'none';
            }
        });

        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // ----------------------------------------------------
    // 3. Image Gallery Zoom on Hover Effect
    // ----------------------------------------------------
    const zoomImgBox = document.getElementById('detail-img-box');
    const zoomImg = document.getElementById('detail-img-zoom');
    if (zoomImgBox && zoomImg) {
        zoomImgBox.addEventListener('mousemove', (e) => {
            const x = e.clientX - zoomImgBox.getBoundingClientRect().left;
            const y = e.clientY - zoomImgBox.getBoundingClientRect().top;

            const w = zoomImgBox.clientWidth;
            const h = zoomImgBox.clientHeight;

            const xPercent = (x / w) * 100;
            const yPercent = (y / h) * 100;

            zoomImg.style.transformOrigin = `${xPercent}% ${yPercent}%`;
            zoomImg.style.transform = 'scale(1.8)';
        });

        zoomImgBox.addEventListener('mouseleave', () => {
            zoomImg.style.transform = 'scale(1)';
        });
    }

    // ----------------------------------------------------
    // 4. Quantity Adjuster Actions
    // ----------------------------------------------------
    const qtyMin = document.getElementById('qty-minus');
    const qtyPlu = document.getElementById('qty-plus');
    const qtyInp = document.getElementById('qty-input');

    if (qtyMin && qtyPlu && qtyInp) {
        const maxStock = parseInt(qtyInp.getAttribute('max')) || 999;

        qtyMin.addEventListener('click', () => {
            let val = parseInt(qtyInp.value) || 1;
            if (val > 1) {
                qtyInp.value = val - 1;
            }
        });

        qtyPlu.addEventListener('click', () => {
            let val = parseInt(qtyInp.value) || 1;
            if (val < maxStock) {
                qtyInp.value = val + 1;
            } else {
                showToast(`Only ${maxStock} items available in stock.`, 'warning');
            }
        });

        qtyInp.addEventListener('change', () => {
            let val = parseInt(qtyInp.value) || 1;
            if (val < 1) qtyInp.value = 1;
            if (val > maxStock) {
                qtyInp.value = maxStock;
                showToast(`Only ${maxStock} items available in stock.`, 'warning');
            }
        });
    }

    // ----------------------------------------------------
    // 5. AJAX Wishlist Button Toggle Handler
    // ----------------------------------------------------
    const wlButtons = document.querySelectorAll('.wishlist-btn-toggle');
    wlButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const productId = btn.getAttribute('data-product-id');
            const csrftoken = getCookie('csrftoken');

            if (!csrftoken) {
                showToast("You must log in to manage your wishlist.", "error");
                return;
            }

            fetch('/wishlist/toggle-ajax/', {
                method: 'POST',
                headers: {
                    'Content-type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ product_id: productId })
            })
                .then(res => {
                    if (res.status === 403 || res.status === 401) {
                        throw new Error("unauthorized");
                    }
                    return res.json();
                })
                .then(data => {
                    if (data.success) {
                        if (data.added) {
                            btn.classList.add('active');
                            btn.firstElementChild.className = 'fa-solid fa-heart';
                            showToast(data.message, 'success');
                        } else {
                            btn.classList.remove('active');
                            btn.firstElementChild.className = 'fa-regular fa-heart';
                            showToast(data.message, 'success');
                        }

                        // Update Wishlist badge counter if exists
                        const wlBadge = document.getElementById('wishlist-badge');
                        if (wlBadge) {
                            wlBadge.innerText = data.wishlist_count;
                            wlBadge.style.display = data.wishlist_count > 0 ? 'flex' : 'none';
                        }
                    } else {
                        showToast(data.error || "An error occurred.", 'error');
                    }
                })
                .catch(err => {
                    if (err.message === "unauthorized") {
                        showToast("You must log in to use your wishlist.", "error");
                    } else {
                        showToast("Failed to process wishlist request.", "error");
                    }
                });
        });
    });

    // ----------------------------------------------------
    // 6. AJAX Add to Cart Action
    // ----------------------------------------------------
    const addCartBtns = document.querySelectorAll('.btn-add-to-cart');
    addCartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();

            const productId = btn.getAttribute('data-product-id');
            // Check if there is an input field for quantity
            const qtyInput = document.getElementById('qty-input');
            const quantity = qtyInput ? parseInt(qtyInput.value) : 1;

            const csrftoken = getCookie('csrftoken');
            showSpinner(true);

            fetch('/cart/add-ajax/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            })
                .then(res => res.json())
                .then(data => {
                    showSpinner(false);
                    if (data.success) {
                        showToast(data.message, 'success');

                        // Update main Cart Badge counter
                        const cartBadge = document.getElementById('cart-badge');
                        if (cartBadge) {
                            cartBadge.innerText = data.cart_count;
                            cartBadge.style.display = data.cart_count > 0 ? 'flex' : 'none';
                        }
                    } else {
                        showToast(data.error || "Failed to add product to cart.", "error");
                    }
                })
                .catch(err => {
                    showSpinner(false);
                    showToast("Failed to connect to cart service.", "error");
                });
        });
    });
});

// --------------------------------------------------------
// 7. Shopping Cart Quantity Update & Item Removal
// --------------------------------------------------------
function updateCartQty(itemId, quantity) {
    const csrftoken = getCookie('csrftoken');
    showSpinner(true);

    fetch('/cart/update-ajax/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
        .then(res => res.json())
        .then(data => {
            showSpinner(false);
            if (data.success) {
                // Update individual row subtotal
                const subtotalEl = document.getElementById(`subtotal-${itemId}`);
                if (subtotalEl) {
                    subtotalEl.innerText = `$${parseFloat(data.item_subtotal).toFixed(2)}`;
                }

                // Update pricing summary panel
                refreshSummary(data);
                showToast(data.message, 'success');
            } else {
                showToast(data.error || "Failed to update item quantity.", "error");

                // Revert changes on the input
                const qtyBox = document.getElementById(`qty-${itemId}`);
                if (qtyBox) {
                    const prev = qtyBox.getAttribute('data-prev-val');
                    qtyBox.value = prev;
                }
            }
        })
        .catch(err => {
            showSpinner(false);
            showToast("Connection error while updating cart.", "error");
        });
}

function removeCartItem(itemId) {
    if (!confirm("Are you sure you want to remove this item from your cart?")) return;

    const csrftoken = getCookie('csrftoken');
    showSpinner(true);

    fetch('/cart/remove-ajax/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            item_id: itemId
        })
    })
        .then(res => res.json())
        .then(data => {
            showSpinner(false);
            if (data.success) {
                // Fade out and remove element from DOM
                const row = document.getElementById(`cart-row-${itemId}`);
                if (row) {
                    row.remove();
                }

                // If cart is empty, reload page to display empty cart state
                if (data.cart_count === 0) {
                    window.location.reload();
                    return;
                }

                refreshSummary(data);
                showToast(data.message, 'success');
            } else {
                showToast(data.error || "Failed to remove item.", "error");
            }
        })
        .catch(err => {
            showSpinner(false);
            showToast("Connection error while removing item.", "error");
        });
}

function refreshSummary(data) {
    const subtotalValEl = document.getElementById('summary-subtotal');
    const discountValEl = document.getElementById('summary-discount');
    const shippingValEl = document.getElementById('summary-shipping');
    const taxValEl = document.getElementById('summary-tax');
    const grandValEl = document.getElementById('summary-grand-total');

    if (subtotalValEl) subtotalValEl.innerText = `$${parseFloat(data.cart_subtotal).toFixed(2)}`;
    if (discountValEl) discountValEl.innerText = `-$${parseFloat(data.cart_discount).toFixed(2)}`;
    if (shippingValEl) {
        shippingValEl.innerText = parseFloat(data.cart_shipping) === 0 ? 'FREE' : `$${parseFloat(data.cart_shipping).toFixed(2)}`;
    }
    if (taxValEl) taxValEl.innerText = `$${parseFloat(data.cart_tax).toFixed(2)}`;
    if (grandValEl) grandValEl.innerText = `$${parseFloat(data.cart_grand_total).toFixed(2)}`;

    // Update main count badge too
    const cartBadge = document.getElementById('cart-badge');
    if (cartBadge) {
        cartBadge.innerText = data.cart_count;
        cartBadge.style.display = data.cart_count > 0 ? 'flex' : 'none';
    }
}

// ----------------------------------------------------
// 8. Coupon Code Application Action
// ----------------------------------------------------
function applyPromoCode() {
    const promoInput = document.getElementById('promo-input');
    if (!promoInput) return;

    const code = promoInput.value.trim();
    if (!code) {
        showToast('Please enter a coupon code.', 'warning');
        return;
    }

    const csrftoken = getCookie('csrftoken');
    showSpinner(true);

    fetch('/cart/apply-coupon-ajax/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            code: code
        })
    })
        .then(res => {
            if (!res.ok) {
                return res.json().then(d => { throw new Error(d.error || "Invalid coupon"); });
            }
            return res.json();
        })
        .then(data => {
            showSpinner(false);
            if (data.success) {
                showToast(data.message, 'success');

                // Render promo items
                refreshSummary(data);

                // Render details coupon layout
                const promoFeedback = document.getElementById('promo-feedback');
                if (promoFeedback) {
                    promoFeedback.innerHTML = `<span style="color: var(--success); font-weight:600;">Active Coupon: ${code} (-$${data.discount})</span>`;
                }
            }
        })
        .catch(err => {
            showSpinner(false);
            showToast(err.message, 'error');
        });
}
