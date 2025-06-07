"""
Main OPC Server Handler

This module provides the main interface for interacting with the OPC server,
including methods for reading and writing tags, managing connections, and
handling device communication.
"""

import OpenOPC
from ..config.settings import (
    OPC_SERVER_NAME,
    UPDATE_RATE,
    DEFAULT_READ_TIMEOUT,
    DEFAULT_WRITE_TIMEOUT
)

class OPCHandler:
    def __init__(self):
        self.client = None
        self.connected = False
        
    def connect(self):
        """
        Establish connection to the OPC server
        """
        try:
            self.client = OpenOPC.client()
            self.client.connect(OPC_SERVER_NAME)
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to OPC server: {e}")
            return False
            
    def disconnect(self):
        """
        Disconnect from the OPC server
        """
        if self.client:
            try:
                self.client.close()
                self.connected = False
                return True
            except Exception as e:
                print(f"Error disconnecting from OPC server: {e}")
                return False
    
    def read_tag(self, tag_name):
        """
        Read a value from a specified OPC tag
        """
        if not self.connected:
            return None
            
        try:
            value = self.client.read(tag_name, timeout=DEFAULT_READ_TIMEOUT)
            return value
        except Exception as e:
            print(f"Error reading tag {tag_name}: {e}")
            return None
            
    def write_tag(self, tag_name, value):
        """
        Write a value to a specified OPC tag
        """
        if not self.connected:
            return False
            
        try:
            self.client.write((tag_name, value), timeout=DEFAULT_WRITE_TIMEOUT)
            return True
        except Exception as e:
            print(f"Error writing to tag {tag_name}: {e}")
            return False
