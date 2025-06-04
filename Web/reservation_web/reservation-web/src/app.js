const express = require('express');
const bodyParser = require('body-parser');
const reservationRoutes = require('./routes/reservationRoutes');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use('/api/reservations', reservationRoutes());

// Serve static files
app.use('/static', express.static(path.join(__dirname, 'static')));

// Serve the GUI
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});