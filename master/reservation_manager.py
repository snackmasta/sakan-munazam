# ReservationManager: Handles reservation-based light and access logic
from utils import sql
from datetime import datetime

class ReservationManager:
    def __init__(self, lock_to_light, devices):
        self.lock_to_light = lock_to_light
        self.devices = devices
        self.reserved_lights_on = {}
        self.one_time_access = {}
        self.one_time_access_time = {}

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
                                if seconds_since_end < 3:
                                    self.one_time_access[lock_dev] = last_res[0]
                                    self.one_time_access_time[lock_dev] = now
                                    continue
                        send_command(light_dev, 'OFF')
                        self.reserved_lights_on[light_dev] = False
                else:
                    if lock_dev in self.one_time_access:
                        if lock_dev in self.one_time_access_time:
                            now = sql.datetime.now()
                            access_time = self.one_time_access_time[lock_dev]
                            if (now - access_time).total_seconds() > 60:
                                del self.one_time_access[lock_dev]
                                del self.one_time_access_time[lock_dev]
        except Exception as e:
            print(f"Reservation expiry check error: {e}")

    def check_user_access(self, user_id, ip_address):
        allowed = sql.is_access_allowed(user_id, ip_address)
        for lock_dev, last_uid in self.one_time_access.items():
            if user_id == last_uid and self.devices[lock_dev]['ip'] == ip_address:
                del self.one_time_access[lock_dev]
                if lock_dev in self.one_time_access_time:
                    del self.one_time_access_time[lock_dev]
                allowed = True
                break
        return allowed
