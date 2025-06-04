document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('reservationForm');
    const tableBody = document.querySelector('#reservationsTable tbody');

    function fetchReservations() {
        fetch('/api/reservations')
            .then(res => res.json())
            .then(data => {
                tableBody.innerHTML = '';
                data.forEach(r => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${r.reservation_id}</td>
                        <td>${r.room_id}</td>
                        <td>${r.user_id}</td>
                        <td>${r.date}</td>
                        <td>${r.start_time}</td>
                        <td>${r.end_time}</td>
                        <td><button data-id="${r.reservation_id}" class="delete-btn">Delete</button></td>
                    `;
                    tableBody.appendChild(tr);
                });
            });
    }

    form.addEventListener('submit', e => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        fetch('/api/reservations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => {
            if (!res.ok) throw new Error('Failed to create reservation');
            return res.json();
        })
        .then(() => {
            form.reset();
            fetchReservations();
        })
        .catch(alert);
    });

    tableBody.addEventListener('click', e => {
        if (e.target.classList.contains('delete-btn')) {
            const id = e.target.getAttribute('data-id');
            fetch(`/api/reservations/${id}`, { method: 'DELETE' })
                .then(res => {
                    if (!res.ok) throw new Error('Failed to delete reservation');
                    fetchReservations();
                })
                .catch(alert);
        }
    });

    fetchReservations();
});
