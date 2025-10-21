"""
Sheet Constraints - Sheet dimensions and usable area
"""

from dataclasses import dataclass
from typing import Optional, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from geometry.polygon import Polygon, Point, BoundingBox


@dataclass
class SheetConstraints:
    """
    Sheet constraints and usable area
    
    Defines the cutting sheet dimensions and safe margins
    """
    width: float  # mm
    height: float  # mm
    margin_left: float = 5.0  # mm
    margin_right: float = 5.0
    margin_top: float = 5.0
    margin_bottom: float = 5.0
    
    @property
    def area(self) -> float:
        """Total sheet area"""
        return self.width * self.height
    
    @property
    def usable_width(self) -> float:
        """Usable width after margins"""
        return self.width - self.margin_left - self.margin_right
    
    @property
    def usable_height(self) -> float:
        """Usable height after margins"""
        return self.height - self.margin_top - self.margin_bottom
    
    @property
    def usable_area(self) -> float:
        """Usable area after margins"""
        return self.usable_width * self.usable_height
    
    def get_usable_bounds(self) -> BoundingBox:
        """Get usable area as bounding box"""
        return BoundingBox(
            min_x=self.margin_left,
            min_y=self.margin_bottom,
            max_x=self.width - self.margin_right,
            max_y=self.height - self.margin_top
        )
    
    def get_usable_polygon(self) -> Polygon:
        """Get usable area as polygon"""
        return Polygon([
            Point(self.margin_left, self.margin_bottom),
            Point(self.width - self.margin_right, self.margin_bottom),
            Point(self.width - self.margin_right, self.height - self.margin_top),
            Point(self.margin_left, self.height - self.margin_top)
        ])
    
    def fits_in_sheet(self, part: Polygon, position: Optional[Point] = None) -> bool:
        """Check if part fits in usable sheet area"""
        if position:
            part = part.translate(position.x, position.y)
        
        bounds = part.bounds
        usable = self.get_usable_bounds()
        
        return (
            bounds.min_x >= usable.min_x and
            bounds.max_x <= usable.max_x and
            bounds.min_y >= usable.min_y and
            bounds.max_y <= usable.max_y
        )
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SheetConstraints':
        """Create from config dictionary"""
        return cls(
            width=data['width'],
            height=data['height'],
            margin_left=data.get('sheet_margin_left', data.get('margin_left', 5.0)),
            margin_right=data.get('sheet_margin_right', data.get('margin_right', 5.0)),
            margin_top=data.get('sheet_margin_top', data.get('margin_top', 5.0)),
            margin_bottom=data.get('sheet_margin_bottom', data.get('margin_bottom', 5.0))
        )
    
    def __str__(self) -> str:
        return f"Sheet {self.width}×{self.height}mm (usable: {self.usable_width:.0f}×{self.usable_height:.0f}mm)"


# Preset sheet sizes
class SheetSizes:
    """Standard sheet size presets"""
    
    STANDARD_4X8 = SheetConstraints(1220, 2440, 10, 10, 10, 10)
    STANDARD_5X10 = SheetConstraints(1524, 3048, 10, 10, 10, 10)
    METRIC_1X2 = SheetConstraints(1000, 2000, 10, 10, 10, 10)
    METRIC_1_5X3 = SheetConstraints(1500, 3000, 10, 10, 10, 10)
    SMALL_TEST = SheetConstraints(600, 400, 5, 5, 5, 5)

