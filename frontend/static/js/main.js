document.addEventListener('DOMContentLoaded', function () {
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
});

var _currentProductId = null;
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

            if (p.seller) {
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
            alert('Увійдіть щоб залишити відгук');
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

    if (e.target && e.target.id === 'modal-add-cart') {
        alert('Додано в кошик!');
    }
});

function closeModal() {
    var overlay = document.getElementById('product-modal');
    if (overlay) overlay.classList.remove('active');
}

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
});
