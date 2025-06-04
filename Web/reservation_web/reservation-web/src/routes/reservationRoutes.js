const express = require('express');
const ReservationController = require('../controllers/reservationController');
const router = express.Router();
const reservationController = new ReservationController();

router.post('/', reservationController.createReservation);
router.get('/', reservationController.getReservations);
router.put('/:id', reservationController.updateReservation);
router.delete('/:id', reservationController.deleteReservation);

module.exports = () => router;