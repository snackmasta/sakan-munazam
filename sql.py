import mysql.connector
from datetime import datetime

def is_user_id_valid(user_id):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="kucingku",
        database="mtu_smart_classroom"
    )
    cursor = db.cursor(buffered=True)
    query = "SELECT 1 FROM room_reservations WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result is not None

def get_all_user_ids():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="kucingku",
        database="mtu_smart_classroom"
    )
    cursor = db.cursor()
    query = "SELECT user_id FROM room_reservations"
    cursor.execute(query)
    user_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return user_ids

def is_access_allowed(user_id, ip_address):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="kucingku",
        database="mtu_smart_classroom"
    )
    cursor = db.cursor(buffered=True)
    # 1. Get room_id from slave table using ip_address
    cursor.execute("SELECT room_id FROM slave WHERE ip_address = %s", (ip_address,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        db.close()
        return False
    room_id = row[0]
    # 2. Check for valid reservation
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M:%S')
    query = ("SELECT 1 FROM room_reservations WHERE user_id = %s AND room_id = %s "
             "AND date = %s AND start_time <= %s AND end_time >= %s")
    cursor.execute(query, (user_id, room_id, today, current_time, current_time))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result is not None

if __name__ == "__main__":
    print("All valid user IDs in the database:")
    for uid in get_all_user_ids():
        print(uid)
    test_user_id = input("Enter user_id to test: ").strip()
    if is_user_id_valid(test_user_id):
        print("User ID is valid (found in database).")
    else:
        print("User ID is NOT valid (not found in database).")