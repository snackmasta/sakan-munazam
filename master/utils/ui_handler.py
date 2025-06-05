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
            headers = ["Device ID", "State", "Lux", "PWM", "Updated"]
            output.append(tabulate(lights, headers=headers, tablefmt="fancy_grid", floatfmt=".1f"))
        else:
            output.append("Lights: (none)")
        if locks:
            output.append("\nLocks:")
            headers = ["Device ID", "State", "Updated"]
            output.append(tabulate(locks, headers=headers, tablefmt="fancy_grid"))
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
