import mysql.connector
from mysql.connector import pooling
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "kucingku",
    "database": "mtu_smart_classroom"
}

# Create a connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **DB_CONFIG
)

def get_connection():
    return connection_pool.get_connection()

def is_user_id_valid(user_id):
    """Quick check if a user ID exists in any reservation."""
    try:
        connection = get_connection()
        cursor = connection.cursor(buffered=True)
        query = "SELECT 1 FROM room_reservations WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return result is not None
    finally:
        cursor.close()
        connection.close()

def get_all_user_ids():
    """Get all unique user IDs from reservations."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        query = "SELECT DISTINCT user_id FROM room_reservations"
        cursor.execute(query)
        user_ids = [row[0] for row in cursor.fetchall()]
        return user_ids
    finally:
        cursor.close()
        connection.close()

def is_access_allowed(user_id, ip_address):
    """Check if a user has access to a room at the current time."""
    try:
        connection = get_connection()
        cursor = connection.cursor(buffered=True)
        
        # 1. Get room_id from slave table using ip_address
        cursor.execute("SELECT room_id FROM slave WHERE ip_address = %s", (ip_address,))
        row = cursor.fetchone()
        if not row:
            return False
        room_id = row[0]
        
        # 2. Check for valid reservation
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M:%S')
        query = (
            "SELECT 1 FROM room_reservations "
            "WHERE user_id = %s AND room_id = %s "
            "AND date = %s AND start_time <= %s AND end_time >= %s"
        )
        cursor.execute(query, (user_id, room_id, today, current_time, current_time))
        result = cursor.fetchone()
        return result is not None
    finally:
        cursor.close()
        connection.close()

def get_all_room_reservations():
    """Retrieve all room reservations."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM room_reservations"
        cursor.execute(query)
        reservations = cursor.fetchall()
        return reservations
    finally:
        cursor.close()
        connection.close()

def get_next_3_reservations():
    """Retrieve the next 3 upcoming room reservations ordered by date and start_time."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        current_time = now.strftime('%H:%M:%S')
        query = (
            "SELECT * FROM room_reservations "
            "WHERE (date > %s) OR (date = %s AND start_time >= %s) "
            "ORDER BY date ASC, start_time ASC "
            "LIMIT 3"
        )
        cursor.execute(query, (today, today, current_time))
        reservations = cursor.fetchall()
        return reservations
    finally:
        cursor.close()
        connection.close()

def ensure_log_tables_exist():
    """Create incoming_log and outgoing_log tables if they do not exist."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incoming_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                log_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                message TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outgoing_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                log_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                message TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def insert_incoming_log(message):
    ensure_log_tables_exist()
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO incoming_log (message) VALUES (%s)",
            (message,)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def insert_outgoing_log(message):
    ensure_log_tables_exist()
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO outgoing_log (message) VALUES (%s)",
            (message,)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("All valid user IDs in the database:")
    for uid in get_all_user_ids():
        print(uid)
    print("\nAll room reservations:")
    for reservation in get_all_room_reservations():
        print(reservation)
    print("\nNext 3 upcoming room reservations:")
    for reservation in get_next_3_reservations():
        print(reservation)
    test_user_id = input("Enter user_id to test: ").strip()
    if is_user_id_valid(test_user_id):
        print("User ID is valid (found in database).")
    else:
        print("User ID is NOT valid (not found in database).")
