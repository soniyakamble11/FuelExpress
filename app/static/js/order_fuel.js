document.addEventListener("DOMContentLoaded", function () {
    const fuelRadios = document.querySelectorAll('input[name="fuel_id"]');
    const quantityInput = document.querySelector('input[name="quantity"]');
    const selectedFuelName = document.getElementById('selectedFuelName');
    const displayQuantity = document.getElementById('displayQuantity');
    const pricePerLiter = document.getElementById('pricePerLiter');
    const totalAmount = document.getElementById('totalAmount');

    function updateTotal() {
        const selectedFuel = document.querySelector('input[name="fuel_id"]:checked');
        if (!selectedFuel) return;
        const price = parseFloat(selectedFuel.dataset.price);
        const qty = parseFloat(quantityInput.value);

        selectedFuelName.textContent = selectedFuel.dataset.name;
        displayQuantity.textContent = qty;
        pricePerLiter.textContent = '₹' + price.toFixed(2);
        totalAmount.textContent = '₹' + (price * qty).toFixed(2);
    }

    fuelRadios.forEach(radio => radio.addEventListener('change', updateTotal));
    quantityInput.addEventListener('input', updateTotal);

    window.decreaseQuantity = function () {
        let val = parseInt(quantityInput.value);
        if (val > 1) quantityInput.value = val - 1;
        updateTotal();
    };

    window.increaseQuantity = function () {
        let val = parseInt(quantityInput.value);
        quantityInput.value = val + 1;
        updateTotal();
    };

    updateTotal(); // initial call
});
