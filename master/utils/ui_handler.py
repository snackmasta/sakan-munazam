"""UI handler for displaying device status and handling user input."""

class UIHandler:
    @staticmethod
    def print_status_table(lights, locks):
        """Display device status in a clean table format."""
        # Clear previous lines (not scrolling)
        print("\033[H\033[J")  # Clear screen
        
        # Print header
        print("\n=== Device Status ===")
        
        # Print lights table
        if lights:
            print("\nLights:")
            print("┌─────────────┬──────┬─────────┬─────────┬──────────┐")
            print("│ Device ID   │State │ Lux     │ PWM     │ Updated  │")
            print("├─────────────┼──────┼─────────┼─────────┼──────────┤")
            for device in lights:
                print(f"│ {device[0]:<11}│{device[1]:<6}│{device[2]:>8} │{device[3]:>8} │ {device[4]} │")
            print("└─────────────┴──────┴─────────┴─────────┴──────────┘")
        
        # Print locks table
        if locks:
            print("\nLocks:")
            print("┌─────────────┬──────────┬──────────┐")
            print("│ Device ID   │ State    │ Updated  │")
            print("├─────────────┼──────────┼──────────┤")
            for device in locks:
                print(f"│ {device[0]:<11}│{device[1]:<9} │ {device[2]} │")
            print("└─────────────┴──────────┴──────────┘")

    @staticmethod
    def print_help():
        """Display available commands."""
        print("\nCommands:")
        print("- 'status': Show all device statuses")
        print("- 'light <device_id> <ON/OFF>': Control light")
        print("- 'E': Exit server")
