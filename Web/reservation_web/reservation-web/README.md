# Reservation Web

This project is a web application for managing room reservations. It allows users to create, read, update, and delete reservations for various rooms.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [License](#license)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/reservation-web.git
   ```

2. Navigate to the project directory:
   ```
   cd reservation-web
   ```

3. Install the dependencies:
   ```
   npm install
   ```

4. Create a `.env` file in the root directory and add your database connection details:
   ```
   DB_HOST=your_database_host
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_NAME=your_database_name
   ```

## Usage

To start the application, run the following command:
```
npm start
```

The application will be running on `http://localhost:3000`.

## API Endpoints

- **GET /reservations**: Retrieve all reservations.
- **POST /reservations**: Create a new reservation.
- **PUT /reservations/:id**: Update an existing reservation.
- **DELETE /reservations/:id**: Delete a reservation.

## License

This project is licensed under the MIT License.