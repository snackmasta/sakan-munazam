import logging

command_logger = logging.getLogger("command_logger")
command_handler = logging.FileHandler("server_commands.log")
command_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
command_logger.addHandler(command_handler)
command_logger.setLevel(logging.INFO)

def log_command(device_id, command, addr=None):
    if addr:
        command_logger.info(f"[SEND] To {device_id} at {addr}: {command}")
    else:
        command_logger.info(f"[SEND] To {device_id}: {command}")
