"""UI handler for displaying device status and handling user input."""

class UIHandler:
    @staticmethod
    def print_status_table(lights, locks):
        """Display device status in a clean table format using tabulate, redrawing in-place with minimal flicker using cursor movement only."""
        import sys
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
        lines = table_str.count('\n') + 1
        # Always print table at the top, but only clear if not first call
        if not hasattr(UIHandler.print_status_table, "_lines"):
            print(table_str)
            UIHandler.print_status_table._lines = lines
        else:
            # Move cursor up to the start of the table, clear only those lines, then print
            sys.stdout.write(f"\033[{UIHandler.print_status_table._lines}F")  # Move up
            for _ in range(UIHandler.print_status_table._lines):
                sys.stdout.write("\033[2K\r")  # Clear line
                sys.stdout.write("\n")
            sys.stdout.write(f"\033[{UIHandler.print_status_table._lines}F")  # Move up again
            print(table_str, end="\n")
            sys.stdout.flush()
            UIHandler.print_status_table._lines = lines
        # Prevent crash if called before terminal is ready
        return

    @staticmethod
    def print_help():
        """Display available commands."""
        print("\nCommands:")
        print("- 'status': Show all device statuses")
        print("- 'light <device_id> <ON/OFF>': Control light")
        print("- 'E': Exit server")
