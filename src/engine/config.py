"""
Configuration Manager - Unified constraint management

Loads configurations from JSON and creates constraint objects
"""

import json
from typing import Optional
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from constraints.sheet import SheetConstraints
from constraints.spacing import SpacingConstraints
from constraints.rotation import RotationConstraints
from constraints.material import MaterialLibrary, Material


@dataclass
class NestingConfig:
    """
    Complete nesting configuration
    
    Combines all constraint types into one object
    """
    sheet: SheetConstraints
    spacing: SpacingConstraints
    rotation: RotationConstraints
    material: Optional[Material] = None
    
    # Optimization settings
    max_runtime_seconds: float = 60.0
    num_multi_starts: int = 10
    enable_local_search: bool = True
    enable_simulated_annealing: bool = False
    target_utilization: float = 80.0
    
    @classmethod
    def from_json_file(cls, filepath: str) -> 'NestingConfig':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NestingConfig':
        """Create from dictionary"""
        # Parse constraints
        sheet_data = data.get('sheet', {})
        constraints_data = data.get('constraints', {})
        rotation_data = data.get('rotation', {})
        optimization_data = data.get('optimization', {})
        
        # Create constraint objects
        sheet = SheetConstraints.from_dict(sheet_data)
        
        spacing = SpacingConstraints.from_dict(constraints_data)
        
        rotation = RotationConstraints.from_dict(rotation_data)
        
        # Load material if specified
        material = None
        if 'material' in sheet_data:
            material_lib = MaterialLibrary()
            material = material_lib.get(sheet_data['material'])
            
            # If material found, override spacing with material values
            if material:
                spacing.kerf_width = material.kerf_width
                spacing.min_web = material.min_web
        
        # Create config
        config = cls(
            sheet=sheet,
            spacing=spacing,
            rotation=rotation,
            material=material
        )
        
        # Set optimization parameters
        if optimization_data:
            config.max_runtime_seconds = optimization_data.get('max_runtime_seconds', 60.0)
            config.num_multi_starts = optimization_data.get('num_multi_starts', 10)
            config.enable_local_search = optimization_data.get('enable_local_search', True)
            config.enable_simulated_annealing = optimization_data.get('enable_simulated_annealing', False)
            config.target_utilization = optimization_data.get('target_utilization', 80.0)
        
        return config
    
    # Convenience properties for easier access
    @property
    def sheet_width(self) -> float:
        return self.sheet.width
    
    @property
    def sheet_height(self) -> float:
        return self.sheet.height
    
    @property
    def margin_left(self) -> float:
        return self.sheet.margin_left
    
    @property
    def margin_right(self) -> float:
        return self.sheet.margin_right
    
    @property
    def margin_top(self) -> float:
        return self.sheet.margin_top
    
    @property
    def margin_bottom(self) -> float:
        return self.sheet.margin_bottom
    
    @property
    def kerf_width(self) -> float:
        return self.spacing.kerf_width
    
    @property
    def min_web(self) -> float:
        return self.spacing.min_web
    
    @property
    def pierce_cost_seconds(self) -> float:
        if self.material:
            return self.material.pierce_time
        return 2.0  # Default
    
    def get_allowed_rotations(self, part=None) -> list:
        """Get allowed rotations for a part"""
        part_id = getattr(part, 'id', 'default')
        return self.rotation.get_allowed_rotations(part_id)
    
    def __str__(self) -> str:
        lines = [
            "Nesting Configuration:",
            f"  {self.sheet}",
            f"  {self.spacing}",
            f"  {self.rotation}",
        ]
        if self.material:
            lines.append(f"  Material: {self.material}")
        lines.extend([
            f"  Max runtime: {self.max_runtime_seconds}s",
            f"  Multi-starts: {self.num_multi_starts}",
            f"  Target utilization: {self.target_utilization}%"
        ])
        return "\n".join(lines)


# Convenience function
def load_config(filepath: str) -> NestingConfig:
    """Load nesting configuration from JSON file"""
    return NestingConfig.from_json_file(filepath)

