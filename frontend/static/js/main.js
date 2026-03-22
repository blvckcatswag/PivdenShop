document.addEventListener('DOMContentLoaded', function () {
    // User menu toggle
    var toggle = document.querySelector('.user-menu-toggle');
    var dropdown = document.querySelector('.user-dropdown');

    if (toggle && dropdown) {
        toggle.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdown.classList.toggle('active');
        });

        document.addEventListener('click', function () {
            dropdown.classList.remove('active');
        });
    }

    // Ripple effect
    document.addEventListener('click', function (e) {
        var btn = e.target.closest('.btn, .btn-gradient');
        if (!btn) return;
        var ripple = document.createElement('span');
        ripple.classList.add('ripple');
        var rect = btn.getBoundingClientRect();
        var size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
        ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
        btn.appendChild(ripple);
        setTimeout(function () { ripple.remove(); }, 600);
    });

    // Sticky header — hide top bar on scroll
    var header = document.getElementById('site-header');
    var lastScroll = 0;
    if (header) {
        window.addEventListener('scroll', function () {
            var scrollY = window.pageYOffset || document.documentElement.scrollTop;
            if (scrollY > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
            lastScroll = scrollY;
        }, { passive: true });
    }

    // Theme toggle
    _initTheme();

    // Search autocomplete
    _initSearchAutocomplete();

    // Mini cart
    _initMiniCart();
});

// ===== THEME =====
function _initTheme() {
    var saved = localStorage.getItem('theme');
    if (saved === 'light') {
        document.body.classList.add('light');
    }

    var btn = document.getElementById('theme-toggle');
    if (btn) {
        btn.addEventListener('click', function () {
            document.body.classList.toggle('light');
            var isLight = document.body.classList.contains('light');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
        });
    }
}

// ===== SEARCH AUTOCOMPLETE =====
function _initSearchAutocomplete() {
    var input = document.getElementById('header-search');
    var dd = document.getElementById('search-dropdown');
    if (!input || !dd) return;

    var debounceTimer;
    var resultsEl = document.getElementById('search-results');

    input.addEventListener('focus', function () {
        dd.classList.add('active');
    });

    document.addEventListener('click', function (e) {
        if (!e.target.closest('.search-wrapper')) {
            dd.classList.remove('active');
        }
    });

    input.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        var query = this.value.trim();

        if (query.length < 2) {
            resultsEl.innerHTML = '<div class="search-dropdown-hint">Введіть від 2 символів для пошуку</div>';
            return;
        }

        debounceTimer = setTimeout(function () {
            fetch('/api/products?search=' + encodeURIComponent(query) + '&limit=5')
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    var products = data.products || [];
                    if (products.length === 0) {
                        resultsEl.innerHTML = '<div class="search-dropdown-hint">Нічого не знайдено</div>';
                        return;
                    }

                    var html = '';
                    products.forEach(function (p) {
                        var title = _highlightMatch(p.title, query);
                        var imgHtml = p.image_url
                            ? '<img src="' + p.image_url + '" alt="">'
                            : _getCategoryIcon(p.category);

                        html += '<a href="/products?search=' + encodeURIComponent(query) + '" class="search-result-item" data-id="' + p.id + '">' +
                            '<div class="search-result-img">' + imgHtml + '</div>' +
                            '<div class="search-result-info">' +
                            '<div class="search-result-title">' + title + '</div>' +
                            '<div class="search-result-price">' + Math.round(p.price) + ' грн</div>' +
                            '</div>' +
                            '</a>';
                    });
                    resultsEl.innerHTML = html;

                    resultsEl.querySelectorAll('.search-result-item').forEach(function (item) {
                        item.addEventListener('click', function (e) {
                            e.preventDefault();
                            var pid = this.dataset.id;
                            dd.classList.remove('active');
                            openModal(parseInt(pid));
                        });
                    });
                })
                .catch(function () {
                    resultsEl.innerHTML = '<div class="search-dropdown-hint">Помилка пошуку</div>';
                });
        }, 300);
    });

    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            dd.classList.remove('active');
        }
    });
}

function _highlightMatch(text, query) {
    if (!query) return text;
    var escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    var re = new RegExp('(' + escaped + ')', 'gi');
    return text.replace(re, '<mark>$1</mark>');
}

function _getCategoryIcon(category) {
    var icons = {
        'Електроніка': '&#128187;',
        'Одяг': '&#128085;',
        'Дім': '&#127968;',
        'Спорт': '&#9917;',
        'Краса': '&#128132;'
    };
    return icons[category] || '&#128230;';
}

// ===== MINI CART =====
function _initMiniCart() {
    var wrapper = document.getElementById('mini-cart-wrapper');
    var dd = document.getElementById('mini-cart-dropdown');
    if (!wrapper || !dd) return;

    var showTimer, hideTimer;

    wrapper.addEventListener('mouseenter', function () {
        clearTimeout(hideTimer);
        showTimer = setTimeout(function () {
            _loadMiniCart();
            dd.classList.add('active');
        }, 150);
    });

    wrapper.addEventListener('mouseleave', function () {
        clearTimeout(showTimer);
        hideTimer = setTimeout(function () {
            dd.classList.remove('active');
        }, 200);
    });
}

function _loadMiniCart() {
    var token = localStorage.getItem('token');
    if (!token) return;

    var itemsEl = document.getElementById('mini-cart-items');
    var footerEl = document.getElementById('mini-cart-footer');
    var totalEl = document.getElementById('mini-cart-total-price');

    fetch('/api/cart', {
        headers: { 'Authorization': 'Bearer ' + token }
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        var items = data.items || [];
        if (items.length === 0) {
            itemsEl.innerHTML = '<div class="mini-cart-empty">Кошик порожній</div>';
            footerEl.style.display = 'none';
            return;
        }

        var html = '';
        var total = 0;
        items.forEach(function (item) {
            var price = item.price * item.quantity;
            total += price;
            var imgHtml = item.image_url
                ? '<img src="' + item.image_url + '" alt="">'
                : '&#128230;';
            html += '<div class="mini-cart-item">' +
                '<div class="mini-cart-item-img">' + imgHtml + '</div>' +
                '<div class="mini-cart-item-info">' +
                '<div class="mini-cart-item-title">' + item.title + '</div>' +
                '<div class="mini-cart-item-price">' + item.quantity + ' × ' + Math.round(item.price) + ' грн</div>' +
                '</div></div>';
        });
        itemsEl.innerHTML = html;
        totalEl.textContent = Math.round(total) + ' грн';
        footerEl.style.display = '';
    })
    .catch(function () {});
}

// ===== PRODUCT MODAL =====
var _currentProductId = null;
var _currentSellerId = null;
var _selectedRating = 5;

function openModal(productId) {
    var overlay = document.getElementById('product-modal');
    if (!overlay) return;

    _currentProductId = productId;
    _selectedRating = 5;

    fetch('/api/products/' + productId)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var p = data.product;
            document.getElementById('modal-title').textContent = p.title;
            document.getElementById('modal-price').textContent = p.price.toLocaleString('uk-UA') + ' грн';
            document.getElementById('modal-description').textContent = p.description || '';
            document.getElementById('modal-category').textContent = p.category || '';

            var imgContainer = document.querySelector('.modal-image');
            if (imgContainer) {
                if (p.image_url) {
                    imgContainer.innerHTML = '<img src="' + p.image_url + '" alt="' + (p.title || '') + '" style="width:100%;height:100%;object-fit:cover">';
                } else {
                    imgContainer.innerHTML = '<div class="modal-image-placeholder"></div>';
                }
            }

            if (p.seller) {
                _currentSellerId = p.seller.id;
                document.getElementById('modal-seller-avatar').textContent = p.seller.name ? p.seller.name[0] : 'S';
                document.getElementById('modal-seller-name').textContent = p.seller.name;
                document.getElementById('modal-seller-rating').innerHTML = '&#11088; ' + p.seller.rating;
                document.getElementById('modal-seller-sales').textContent = p.seller.sales_count + ' продажів';
                document.getElementById('modal-seller-since').textContent = 'На платформі з ' + p.seller.member_since;
            }

            var reviewsEl = document.getElementById('modal-reviews');
            var reviewsTitle = document.getElementById('modal-reviews-title');
            if (reviewsEl) {
                reviewsEl.innerHTML = '';
                if (p.reviews && p.reviews.length > 0) {
                    reviewsTitle.textContent = 'Відгуки (' + p.reviews.length + ')';
                    p.reviews.forEach(function (r) {
                        var stars = '';
                        for (var i = 0; i < r.rating; i++) stars += '\u2B50';
                        for (var j = r.rating; j < 5; j++) stars += '\u2606';
                        reviewsEl.innerHTML +=
                            '<div class="review-item">' +
                            '<div class="review-header">' +
                            '<span class="review-author">' + r.author + '</span>' +
                            '<span class="card-rating">' + stars + '</span>' +
                            '</div>' +
                            '<p class="review-text">' + r.text + '</p>' +
                            '</div>';
                    });
                } else {
                    reviewsTitle.textContent = 'Відгуки';
                    reviewsEl.innerHTML = '<p class="no-reviews">Ще немає відгуків</p>';
                }
            }

            _initStarRating();

            overlay.classList.add('active');
        });
}

function _initStarRating() {
    var stars = document.querySelectorAll('#star-rating span');
    stars.forEach(function (star) {
        star.classList.remove('active');
        if (parseInt(star.dataset.rating) <= _selectedRating) {
            star.classList.add('active');
        }
        star.onclick = function () {
            _selectedRating = parseInt(this.dataset.rating);
            stars.forEach(function (s) {
                s.classList.remove('active');
                if (parseInt(s.dataset.rating) <= _selectedRating) {
                    s.classList.add('active');
                }
            });
        };
    });
}

document.addEventListener('click', function (e) {
    if (e.target && e.target.id === 'submit-review') {
        var text = document.getElementById('review-text').value.trim();
        if (!text) return;

        var token = localStorage.getItem('token');
        if (!token) {
            _showToast('Увійдіть щоб залишити відгук', 'error');
            return;
        }

        fetch('/api/products/' + _currentProductId + '/reviews', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({ text: text, rating: _selectedRating })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.ok) {
                document.getElementById('review-text').value = '';
                openModal(_currentProductId);
            }
        });
    }

    if (e.target && e.target.id === 'modal-contact-seller') {
        var chatToken = localStorage.getItem('token');
        if (!chatToken) {
            window.location.href = '/login';
            return;
        }
        if (!_currentSellerId) return;

        fetch('/api/chats/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + chatToken
            },
            body: JSON.stringify({ seller_id: _currentSellerId })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.chat_id) {
                window.location.href = '/chats/' + data.chat_id;
            }
        });
    }

    if (e.target && e.target.id === 'modal-add-cart') {
        var cartToken = localStorage.getItem('token');
        if (!cartToken) {
            window.location.href = '/login';
            return;
        }

        fetch('/api/cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + cartToken
            },
            body: JSON.stringify({ product_id: _currentProductId, quantity: 1 })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.ok) {
                closeModal();
                _showToast('Товар додано в кошик');
                if (window._updateCartCount) window._updateCartCount();
            } else {
                _showToast(data.error || 'Помилка', 'error');
            }
        });
    }
});

function closeModal() {
    var overlay = document.getElementById('product-modal');
    if (overlay) overlay.classList.remove('active');
}

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
});

function _quickAddToCart(productId) {
    var token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    fetch('/api/cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify({ product_id: productId, quantity: 1 })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (data.ok) {
            _showToast('Товар додано в кошик');
            if (window._updateCartCount) window._updateCartCount();
            var cartBtn = document.getElementById('cart-icon-btn');
            if (cartBtn) {
                cartBtn.classList.add('cart-shake');
                setTimeout(function() { cartBtn.classList.remove('cart-shake'); }, 400);
            }
            var badge = document.getElementById('cart-badge');
            if (badge) {
                badge.style.transform = 'scale(1.4)';
                setTimeout(function() { badge.style.transform = 'scale(1)'; }, 300);
            }
        } else {
            _showToast(data.error || 'Помилка', 'error');
        }
    });
}

function _showSkeletons(container, count) {
    container.innerHTML = '';
    for (var i = 0; i < count; i++) {
        container.innerHTML +=
            '<div class="skeleton-card">' +
            '<div class="skeleton skeleton-image"></div>' +
            '<div class="skeleton-body">' +
            '<div class="skeleton skeleton-title"></div>' +
            '<div class="skeleton skeleton-price"></div>' +
            '<div class="skeleton skeleton-meta"></div>' +
            '</div></div>';
    }
}

function _showToast(msg, type) {
    type = type || 'success';
    var icons = { success: '\u2714', error: '\u2718', info: '\u2139' };
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.innerHTML =
        '<span class="toast-icon">' + (icons[type] || '') + '</span>' +
        '<span class="toast-text">' + msg + '</span>' +
        '<div class="toast-progress"></div>';
    document.body.appendChild(toast);
    setTimeout(function () { toast.classList.add('visible'); }, 10);
    setTimeout(function () {
        toast.classList.remove('visible');
        setTimeout(function () { toast.remove(); }, 350);
    }, 3000);
}
