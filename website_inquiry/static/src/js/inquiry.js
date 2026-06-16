document.addEventListener('DOMContentLoaded', function () {

    const form = document.getElementById('inquiry_form');

    const name = document.getElementById('name');
    const email = document.getElementById('email');
    const country = document.getElementById('country_select');
    const phone = document.getElementById('phone');

    function showError(el, msg) {
        let error = el.parentNode.querySelector('.error-msg');

        if (!error) {
            error = document.createElement('div');
            error.className = 'error-msg';
            error.style.color = 'red';
            error.style.fontSize = '12px';
            el.parentNode.appendChild(error);
        }

        error.innerText = msg;
    }

    function clearError(el) {
        const error = el.parentNode.querySelector('.error-msg');
        if (error) error.remove();
    }

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        let valid = true;

        // clear old errors
        [name, email, country, phone].forEach(clearError);

        // NAME
        if (!name.value.trim()) {
            showError(name, "Full Name is required");
            valid = false;
        }

        // EMAIL
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email.value.trim()) {
            showError(email, "Email is required");
            valid = false;
        } else if (!emailRegex.test(email.value)) {
            showError(email, "Enter valid email address");
            valid = false;
        }

        // COUNTRY
        if (!country.value) {
            showError(country, "Please select country");
            valid = false;
        }

        // PHONE
        if (!phone.value.trim()) {
            showError(phone, "Phone number is required");
            valid = false;
        } else if (!/^[0-9]{6,15}$/.test(phone.value)) {
            showError(phone, "Enter valid phone number");
            valid = false;
        }

        if (valid) {
            form.submit();
        }
    });

    // UX improvement: clear phone error when country changes
    country.addEventListener('change', function () {
        clearError(phone);
    });
});