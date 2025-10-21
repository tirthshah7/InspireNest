"""
Constraint System - Manufacturing Constraints for Nesting

This module defines and enforces all manufacturing constraints:
- Sheet dimensions and margins
- Material properties (kerf, min web)
- Rotation constraints
- Part-specific overrides
"""

from .sheet import SheetConstraints
from .spacing import SpacingConstraints
from .rotation import RotationConstraints
from .material import MaterialLibrary, Material

__all__ = [
    'SheetConstraints',
    'SpacingConstraints',
    'RotationConstraints',
    'MaterialLibrary',
    'Material',
]

