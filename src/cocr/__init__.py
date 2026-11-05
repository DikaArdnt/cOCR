# cOCR Workbench
#
# Copyright (C) 2026 Dika Ardianta
# Copyright (C) 2026 Hisoka Labs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# See LICENSE for details.

"""
cOCR Workbench
Local-first studio for visual document extraction, cleaning, and restructuring.
"""

__version__ = "1.2.0"
__all__ = ["OCREngine", "Exporters", "start_gui_server", "run_cli"]

from cocr.engine import OCREngine
from cocr.exporters import Exporters
from cocr.server import start_gui_server
from cocr.cli import run_cli
