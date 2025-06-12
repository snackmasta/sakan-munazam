const express = require('express');
const User = require('../models/user');
const router = express.Router();

router.post('/', async (req, res) => {
    try {
        const { nim, name, rfid_UID } = req.body;
        if (!nim && !name && !rfid_UID) {
            return res.status(400).json({ message: 'At least one field (NIM, Name, or RFID UID) is required' });
        }
        // Try to find user by NIM if provided, else by RFID UID if provided
        let user = null;
        if (nim) {
            user = await User.findOne({ where: { nim } });
        } else if (rfid_UID) {
            user = await User.findOne({ where: { rfid_UID } });
        }
        if (user) {
            // Update only provided fields
            if (name) user.name = name;
            if (rfid_UID) user.rfid_UID = rfid_UID;
            await user.save();
            return res.status(200).json({ message: 'User updated successfully' });
        } else {
            // Create new user with provided fields (missing fields will be NULL)
            const newUser = await User.create({ nim, name, rfid_UID });
            return res.status(201).json({ message: 'User registered successfully', user: newUser });
        }
    } catch (error) {
        res.status(500).json({ message: 'Error registering/updating user', error: error.message });
    }
});

module.exports = () => router;
