"""
Rotation Constraints - Allowed rotations per part
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class RotationConstraints:
    """
    Rotation constraints for nesting
    
    Defines which rotation angles are allowed globally
    and per-part overrides
    """
    allowed_angles: List[float] = field(default_factory=lambda: [0, 90, 180, 270])
    grain_sensitive: bool = False
    per_part_overrides: Dict[str, List[float]] = field(default_factory=dict)
    
    def get_allowed_rotations(self, part_id: str) -> List[float]:
        """
        Get allowed rotations for a specific part
        
        Args:
            part_id: Part identifier
        
        Returns:
            List of allowed rotation angles in degrees
        """
        # Check for part-specific override
        if part_id in self.per_part_overrides:
            return self.per_part_overrides[part_id]
        
        # Return global allowed angles
        return self.allowed_angles
    
    def is_rotation_allowed(self, part_id: str, angle: float) -> bool:
        """Check if a specific rotation is allowed"""
        allowed = self.get_allowed_rotations(part_id)
        
        # Check with small tolerance for floating point comparison
        tolerance = 0.1
        return any(abs(angle - allowed_angle) < tolerance for allowed_angle in allowed)
    
    def set_part_rotations(self, part_id: str, angles: List[float]):
        """Set allowed rotations for a specific part"""
        self.per_part_overrides[part_id] = angles
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RotationConstraints':
        """Create from config dictionary"""
        return cls(
            allowed_angles=data.get('allowed_angles', [0, 90, 180, 270]),
            grain_sensitive=data.get('grain_sensitive', False),
            per_part_overrides=data.get('per_part_override', {})
        )
    
    @classmethod
    def no_rotation(cls) -> 'RotationConstraints':
        """Preset: No rotation allowed"""
        return cls(allowed_angles=[0], grain_sensitive=True)
    
    @classmethod
    def cardinal_only(cls) -> 'RotationConstraints':
        """Preset: 4 cardinal directions"""
        return cls(allowed_angles=[0, 90, 180, 270])
    
    @classmethod
    def eight_way(cls) -> 'RotationConstraints':
        """Preset: 8 directions (45° steps)"""
        return cls(allowed_angles=[0, 45, 90, 135, 180, 225, 270, 315])
    
    @classmethod
    def fine_grain(cls) -> 'RotationConstraints':
        """Preset: 36 directions (10° steps)"""
        return cls(allowed_angles=list(range(0, 360, 10)))
    
    def __str__(self) -> str:
        return f"Rotations: {len(self.allowed_angles)} angles allowed {self.allowed_angles}"

