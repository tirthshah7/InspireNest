"""
I/O Module - Robust Input/Output for CAD Files

This module handles importing and exporting various CAD formats:
- DXF (AutoCAD Drawing Exchange Format)
- SVG (Scalable Vector Graphics)
- JSON (Custom format)
- G-code (CNC machine code)
"""

from .dxf_importer import DXFImporter, import_dxf_file
# from .svg_importer import SVGImporter  # Day 3
# from .exporters import export_dxf, export_svg, export_json  # Day 3
# from .gcode import generate_gcode  # Day 8

__all__ = [
    'DXFImporter',
    'import_dxf_file',
]

__version__ = '1.0.0'

