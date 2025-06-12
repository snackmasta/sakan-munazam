# ReservationManager: Handles reservation-based light and access logic
from utils import sql
from datetime import datetime

class ReservationManager:
    def __init__(self, lock_to_light, devices):
        self.lock_to_light = lock_to_light
        self.devices = devices
        self.reserved_lights_on = {}
        self.one_time_access = {}
        self.one_time_access_used = {}

    def is_room_reserved_for_device(self, lock_device):
        try:
            ip_address = self.devices[lock_device]['ip']
            connection = sql.get_connection()
            cursor = connection.cursor(buffered=True)
            cursor.execute("SELECT room_id FROM slave WHERE ip_address = %s", (ip_address,))
            row = cursor.fetchone()
            if not row:
                return False, None
            room_id = row[0]
            now = sql.datetime.now()
            today = now.strftime('%Y-%m-%d')
            current_time = now.strftime('%H:%M:%S')
            query = (
                "SELECT end_time FROM room_reservations "
                "WHERE room_id = %s "
                "AND date = %s AND start_time <= %s AND end_time >= %s"
            )
            cursor.execute(query, (room_id, today, current_time, current_time))
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            if result:
                return True, result[0]  # end_time as string
            else:
                return False, None
        except Exception as e:
            print(f"Reservation check error: {e}")
            return False, None

    def check_reservation_expiry(self, send_command):
        try:
            for lock_dev, light_dev in self.lock_to_light.items():
                if self.reserved_lights_on.get(light_dev):
                    reserved, end_time = self.is_room_reserved_for_device(lock_dev)
                    if not reserved:
                        ip_address = self.devices[lock_dev]['ip']
                        connection = sql.get_connection()
                        cursor = connection.cursor(buffered=True)
                        cursor.execute("SELECT room_id FROM slave WHERE ip_address = %s", (ip_address,))
                        row = cursor.fetchone()
                        if row:
                            room_id = row[0]
                            now = sql.datetime.now()
                            today = now.strftime('%Y-%m-%d')
                            cursor.execute(
                                "SELECT user_id, end_time FROM room_reservations WHERE room_id = %s AND date = %s AND end_time < %s ORDER BY end_time DESC LIMIT 1",
                                (room_id, today, now.strftime('%H:%M:%S'))
                            )
                            last_res = cursor.fetchone()
                            cursor.close()
                            connection.close()
                            if last_res:
                                end_dt = datetime.strptime(f"{today} {last_res[1]}", "%Y-%m-%d %H:%M:%S")
                                seconds_since_end = (now - end_dt).total_seconds()
                                if seconds_since_end < 3:  # Grant one-time access if reservation ended recently
                                    if lock_dev not in self.one_time_access:
                                        self.one_time_access[lock_dev] = last_res[0]
                                        self.one_time_access_used = getattr(self, 'one_time_access_used', {})
                                        self.one_time_access_used[lock_dev] = False
                                        print(f"[DEBUG] One-time access GRANTED for lock_dev: {lock_dev} to user_id: {last_res[0]}") # DEBUG
                                    continue
                        if self.reserved_lights_on.get(light_dev):
                            send_command(light_dev, 'OFF')
                            self.reserved_lights_on[light_dev] = False
                            print(f"[DEBUG] Light {light_dev} turned OFF due to reservation expiry for {lock_dev}.") # DEBUG
        except Exception as e:
            print(f"Reservation expiry check error: {e}")

    def check_user_access(self, user_id, ip_address, send_command=None):
        allowed = sql.is_access_allowed(user_id, ip_address)
        print(f"[DEBUG] check_user_access called for user_id: {user_id}, ip_address: {ip_address}")
        print(f"[DEBUG] Initial 'allowed' status from sql.is_access_allowed: {allowed}")
        print(f"[DEBUG] Current one_time_access: {self.one_time_access}")
        print(f"[DEBUG] Current one_time_access_used: {self.one_time_access_used}")

        for lock_dev, last_uid in list(self.one_time_access.items()):
            print(f"[DEBUG] Checking one-time for lock: {lock_dev}, granted_uid: {last_uid}. Comparing with received UID: {user_id} from IP: {ip_address}")
            # Condition 1: UID match
            uid_match = (user_id == last_uid)
            # Condition 2: IP match (device sending UID is the lock device in question)
            # Ensure self.devices[lock_dev]['ip'] exists and is correct
            device_ip_match = False
            if lock_dev in self.devices and 'ip' in self.devices[lock_dev]:
                device_ip_match = (self.devices[lock_dev]['ip'] == ip_address)
            else:
                print(f"[DEBUG] Warning: Device IP not found for lock_dev: {lock_dev} in self.devices")

            print(f"[DEBUG] UID match for {lock_dev}: {uid_match} (Expected: {last_uid}, Got: {user_id})")
            print(f"[DEBUG] Device IP match for {lock_dev}: {device_ip_match} (Expected: {self.devices.get(lock_dev, {}).get('ip')}, Got: {ip_address})")

            if uid_match and device_ip_match:
                print(f"[DEBUG] Matched one-time access rule for user_id: {user_id} at lock_dev: {lock_dev}")
                # Condition 3: Access not used yet
                access_not_used = not self.one_time_access_used.get(lock_dev, True) # Default to True (meaning used or invalid)
                print(f"[DEBUG] Access not used for {lock_dev} (raw value: {self.one_time_access_used.get(lock_dev, 'Not Set, defaults to True for check')}, check result: {access_not_used})")

                if access_not_used:
                    allowed = True # Override initial 'allowed'
                    print(f"[DEBUG] One-time access ALLOWED for user_id: {user_id} at lock_dev: {lock_dev}")
                    if send_command:
                        send_command(lock_dev, 'UNLOCK')
                        print(f"[DEBUG] UNLOCK command attempted for {lock_dev} via send_command.")
                        # Schedule LOCK after 3 seconds
                        import threading
                        def delayed_lock():
                            send_command(lock_dev, 'LOCK')
                            print(f"[DEBUG] LOCK command sent to {lock_dev} after 3s delay following one-time UNLOCK.")
                        threading.Timer(3, delayed_lock).start()
                    else:
                        print(f"[DEBUG] send_command is None. Cannot send UNLOCK to {lock_dev}.")

                    # Revoke one-time access immediately after use
                    del self.one_time_access[lock_dev]
                    if lock_dev in self.one_time_access_used:
                        del self.one_time_access_used[lock_dev]
                    print(f"[DEBUG] One-time access REVOKED for lock_dev: {lock_dev} after use.")
                    break  # Access determined and handled for this attempt
                else:
                    print(f"[DEBUG] One-time access for lock_dev: {lock_dev} was ALREADY USED or not properly granted (used flag: {self.one_time_access_used.get(lock_dev)}). UID: {user_id}")
            # else: # Optional: log if no match for this iteration
                # print(f"[DEBUG] No rule match for lock_dev {lock_dev} with UID {user_id} and IP {ip_address}. UID match: {uid_match}, IP match: {device_ip_match}")
        print(f"[DEBUG] Final 'allowed' status for {user_id} at {ip_address} after one-time check: {allowed}")
        return allowed
