"""UI handler for displaying device status and handling user input."""

class UIHandler:
    @staticmethod
    def print_status_table(lights, locks):
        """Display device status in a clean table format using tabulate, without cursor movement or line clearing."""
        from tabulate import tabulate
        # Compose the table as a string
        output = ["=== Device Status ===\n"]
        if lights:
            output.append("Lights:")
            headers = ["Device ID", "State", "Lux", "PWM", "Raw LDR", "Updated"]
            output.append(tabulate(lights, headers=headers, tablefmt="fancy_grid", floatfmt=".1f"))
        else:
            output.append("Lights: (none)")
        if locks:
            output.append("\nLocks:")
            headers = ["Device ID", "State", "Updated", "Latest UID"]
            # Add 'Latest UID' to each lock row if not present
            lock_rows = []
            for lock in locks:
                # If lock is a dict, extract values by key; if tuple/list, assume order
                if isinstance(lock, dict):
                    row = [lock.get("Device ID", lock.get("device_id", "?")),
                           lock.get("State", lock.get("state", "?")),
                           lock.get("Updated", lock.get("updated", "?")),
                           lock.get("Latest UID", lock.get("latest_uid", "?"))]
                else:
                    # If lock is a tuple/list, append ? if missing latest_uid
                    row = list(lock)
                    if len(row) < 4:
                        row.append("?")
                lock_rows.append(row)
            output.append(tabulate(lock_rows, headers=headers, tablefmt="fancy_grid"))
        else:
            output.append("Locks: (none)")
        table_str = "\n".join(output)
        print(table_str)
        return

    @staticmethod
    def print_help():
        """Display available commands."""
        print("\nCommands:")
        print("- 'status': Show all device statuses")
        print("- 'light <device_id> <ON/OFF>': Control light")
        print("- 'E': Exit server")

def get_latest_lock_uids_from_log(log_path):
    """Parse the log file and return a dict of lock_id -> latest UID."""
    import re
    latest_uid = {}
    # Regex to match lock messages: lock_<id>:<UID>
    lock_re = re.compile(r"lock_(\d+):([0-9A-Fa-f:]+)")
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            match = lock_re.search(line)
            if match:
                lock_id = f"lock_{match.group(1)}"
                uid = match.group(2)
                latest_uid[lock_id] = uid
    return latest_uid
