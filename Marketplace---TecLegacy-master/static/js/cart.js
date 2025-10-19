document.addEventListener('DOMContentLoaded', function() {
    // Función para añadir productos al carrito vía AJAX
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();

            const productId = this.dataset.productId;
            const quantity = document.querySelector(`#quantity-${productId}`)
                ? parseInt(document.querySelector(`#quantity-${productId}`).value)
                : 1;

            fetch(`/cart/add/${productId}/?quantity=${quantity}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar contador del carrito
                    document.getElementById('cart-items-count').textContent = data.cart_items_count;

                    // Mostrar notificación
                    Toastify({
                        text: data.message,
                        duration: 3000,
                        gravity: "top",
                        position: "right",
                        backgroundColor: "linear-gradient(to right, #0063e6, #e60048)",
                        stopOnFocus: true,
                    }).showToast();
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });

    // Funcionalidad para actualizar cantidades en el carrito
    const cartItemControls = document.querySelectorAll('.cart-item-control');

    cartItemControls.forEach(control => {
        control.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const action = this.dataset.action;

            fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    item_id: itemId,
                    action: action
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar contador del carrito
                    document.getElementById('cart-items-count').textContent = data.cart_items_count;

                    // Si el elemento fue eliminado
                    if (data.removed) {
                        const cartItem = document.getElementById(`cart-item-${itemId}`);
                        if (cartItem) {
                            cartItem.remove();
                        }
                    } else {
                        // Actualizar cantidad y total del item
                        document.getElementById(`item-quantity-${itemId}`).textContent = data.quantity;
                        document.getElementById(`item-total-${itemId}`).textContent = data.item_total;
                    }

                    // Actualizar el total del carrito
                    document.getElementById('cart-total').textContent = data.cart_total;

                    // Si el carrito está vacío después de eliminar todo
                    if (data.cart_items_count === 0) {
                        document.getElementById('cart-items').innerHTML = '<div class="alert alert-info">Tu carrito está vacío</div>';
                        document.getElementById('checkout-btn').classList.add('disabled');
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});