const { DataTypes } = require('sequelize');
const db = require('../db/index');

const Reservation = db.define('room_reservations', {
    reservation_id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true,
    },
    room_id: {
        type: DataTypes.STRING(10),
        allowNull: true,
    },
    user_id: {
        type: DataTypes.STRING(50),
        allowNull: true,
    },
    date: {
        type: DataTypes.DATEONLY,
        allowNull: true,
    },
    start_time: {
        type: DataTypes.TIME,
        allowNull: true,
    },
    end_time: {
        type: DataTypes.TIME,
        allowNull: true,
    },
}, {
    tableName: 'room_reservations',
    timestamps: false,
});

module.exports = Reservation;