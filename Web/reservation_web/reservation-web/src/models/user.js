const { DataTypes } = require('sequelize');
const db = require('../db/index');

const User = db.define('users', {
    nim: {
        type: DataTypes.STRING(50),
        primaryKey: true,
    },
    name: {
        type: DataTypes.STRING(100),
        allowNull: false,
    },
    rfid_UID: {
        type: DataTypes.STRING(50),
        allowNull: true,
    },
}, {
    tableName: 'users',
    timestamps: false,
});

module.exports = User;
