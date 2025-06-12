from utils.sql import get_connection


def get_nim_for_reservations(reservations):
    """Given a list of reservation dicts (with user_id as RFID UID), fetches the NIM for each reservation from the users table."""
    if not reservations:
        return []
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        # Build a map from user_id (rfid_UID) to NIM
        user_ids = tuple(set(r['user_id'] for r in reservations if r.get('user_id')))
        if not user_ids:
            return [None for _ in reservations]
        # Prepare query for multiple user_ids
        format_strings = ','.join(['%s'] * len(user_ids))
        query = f"SELECT nim, rfid_UID FROM users WHERE rfid_UID IN ({format_strings})"
        cursor.execute(query, user_ids)
        nim_map = {row['rfid_UID']: row['nim'] for row in cursor.fetchall()}
        # Attach NIM to each reservation
        for r in reservations:
            r['nim'] = nim_map.get(r['user_id'])
        return reservations
    finally:
        cursor.close()
        connection.close()
