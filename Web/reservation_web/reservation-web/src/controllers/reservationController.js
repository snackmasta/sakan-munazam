const Reservation = require('../models/reservation');
const User = require('../models/user');

class ReservationController {
    constructor(reservationModel = Reservation) {
        this.reservationModel = reservationModel;
        this.createReservation = this.createReservation.bind(this);
        this.getReservations = this.getReservations.bind(this);
        this.updateReservation = this.updateReservation.bind(this);
        this.deleteReservation = this.deleteReservation.bind(this);
    }

    async createReservation(req, res) {
        try {
            const { room_id, user_id: nim, date, start_time, end_time } = req.body;
            // Find UID by NIM
            const user = await User.findOne({ where: { nim } });
            if (!user || !user.rfid_UID) {
                return res.status(400).json({ message: 'NIM not found or user has no UID in users table' });
            }
            const newReservation = await this.reservationModel.create({
                room_id,
                user_id: user.rfid_UID, // Insert UID from users table
                date,
                start_time,
                end_time
            });
            res.status(201).json(newReservation);
        } catch (error) {
            console.error('Error creating reservation:', error); // Log full error to console
            res.status(500).json({ message: 'Error creating reservation', error: error.message, stack: error.stack });
        }
    }

    async getReservations(req, res) {
        try {
            const reservations = await this.reservationModel.findAll();
            res.status(200).json(reservations);
        } catch (error) {
            res.status(500).json({ message: 'Error fetching reservations', error });
        }
    }

    async updateReservation(req, res) {
        try {
            const { id } = req.params;
            const { room_id, user_id, date, start_time, end_time } = req.body;
            const updatedReservation = await this.reservationModel.update(
                { room_id, user_id, date, start_time, end_time },
                { where: { reservation_id: id } }
            );
            if (updatedReservation[0] === 0) {
                return res.status(404).json({ message: 'Reservation not found' });
            }
            res.status(200).json({ message: 'Reservation updated successfully' });
        } catch (error) {
            res.status(500).json({ message: 'Error updating reservation', error });
        }
    }

    async deleteReservation(req, res) {
        try {
            const { id } = req.params;
            const deleted = await this.reservationModel.destroy({ where: { reservation_id: id } });
            if (deleted === 0) {
                return res.status(404).json({ message: 'Reservation not found' });
            }
            res.status(204).send();
        } catch (error) {
            res.status(500).json({ message: 'Error deleting reservation', error });
        }
    }
}

module.exports = ReservationController;