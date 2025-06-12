const express = require('express');
const bodyParser = require('body-parser');
const reservationRoutes = require('./routes/reservationRoutes');
const userRoutes = require('./routes/userRoutes');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use('/api/reservations', reservationRoutes());
app.use('/api/users', userRoutes());

// Serve static files
app.use('/static', express.static(path.join(__dirname, 'static')));

// Serve the GUI
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Serve the user registration page
app.get('/register.html', (req, res) => {
    res.sendFile(path.join(__dirname, 'register.html'));
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});