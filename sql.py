import mysql.connector

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

if __name__ == "__main__":
    print("All valid user IDs in the database:")
    for uid in get_all_user_ids():
        print(uid)
    test_user_id = input("Enter user_id to test: ").strip()
    if is_user_id_valid(test_user_id):
        print("User ID is valid (found in database).")
    else:
        print("User ID is NOT valid (not found in database).")