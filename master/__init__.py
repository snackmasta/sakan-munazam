"""Master package initialization."""
from .config import settings
from .handlers.udp_handler import UDPHandler
from .utils.ui_handler import UIHandler

__version__ = "1.0.0"
