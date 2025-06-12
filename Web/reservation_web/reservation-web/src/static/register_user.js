document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('userRegistrationForm');
    const messageDiv = document.getElementById('registrationMessage');

    form.addEventListener('submit', e => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if (result.message) {
                messageDiv.textContent = result.message;
                messageDiv.style.color = 'green';
                form.reset();
            } else {
                messageDiv.textContent = 'Registration failed.';
                messageDiv.style.color = 'red';
            }
        })
        .catch(() => {
            messageDiv.textContent = 'Registration failed.';
            messageDiv.style.color = 'red';
        });
    });
});
