const express = require('express');
const ReservationController = require('../controllers/reservationController');
const User = require('../models/user');
const router = express.Router();
const reservationController = new ReservationController();

router.post('/', reservationController.createReservation);
router.get('/', reservationController.getReservations);
router.put('/:id', reservationController.updateReservation);
router.delete('/:id', reservationController.deleteReservation);
router.post('/users', async (req, res) => {
    try {
        const { nim, name, rfid_UID } = req.body;
        if (!nim || !name) {
            return res.status(400).json({ message: 'NIM and Name are required' });
        }
        const [user, created] = await User.findOrCreate({
            where: { nim },
            defaults: { name, rfid_UID }
        });
        if (!created) {
            return res.status(400).json({ message: 'User with this NIM already exists' });
        }
        res.status(201).json({ message: 'User registered successfully' });
    } catch (error) {
        res.status(500).json({ message: 'Error registering user', error: error.message });
    }
});

module.exports = () => router;