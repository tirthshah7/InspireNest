"""
Spacing Constraints - Kerf and minimum web
"""

from dataclasses import dataclass


@dataclass
class SpacingConstraints:
    """
    Spacing constraints between parts
    
    - kerf_width: Material removed by laser
    - min_web: Minimum gap between parts for structural integrity
    """
    kerf_width: float  # mm
    min_web: float  # mm
    
    @property
    def total_spacing(self) -> float:
        """Total spacing needed between parts"""
        return self.kerf_width + self.min_web
    
    @property
    def offset_per_part(self) -> float:
        """Offset to apply to each part"""
        return (self.kerf_width / 2) + self.min_web
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SpacingConstraints':
        """Create from config dictionary"""
        return cls(
            kerf_width=data.get('kerf_width', 0.3),
            min_web=data.get('min_web', 3.0)
        )
    
    def __str__(self) -> str:
        return f"Spacing: kerf={self.kerf_width}mm, min_web={self.min_web}mm, total={self.total_spacing}mm"

