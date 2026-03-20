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

function openModal(productId) {
    var overlay = document.getElementById('product-modal');
    if (!overlay) return;

    fetch('/api/products/' + productId)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var p = data.product;
            document.getElementById('modal-title').textContent = p.title;
            document.getElementById('modal-price').textContent = p.price.toLocaleString('uk-UA') + ' грн';
            document.getElementById('modal-description').textContent = p.description;

            var sellerEl = document.getElementById('modal-seller');
            if (sellerEl && p.seller_name) {
                sellerEl.textContent = p.seller_name;
            }

            var reviewsEl = document.getElementById('modal-reviews');
            if (reviewsEl && p.reviews) {
                reviewsEl.innerHTML = '';
                p.reviews.forEach(function (r) {
                    var stars = '';
                    for (var i = 0; i < r.rating; i++) stars += '\u2B50';
                    reviewsEl.innerHTML +=
                        '<div class="review-item">' +
                        '<div class="review-header">' +
                        '<span class="review-author">' + r.author + '</span>' +
                        '<span class="card-rating">' + stars + '</span>' +
                        '</div>' +
                        '<p class="review-text">' + r.text + '</p>' +
                        '</div>';
                });
            }

            overlay.classList.add('active');
        });
}

function closeModal() {
    var overlay = document.getElementById('product-modal');
    if (overlay) overlay.classList.remove('active');
}

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeModal();
});
