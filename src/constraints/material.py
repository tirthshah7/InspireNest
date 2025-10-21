"""
Material Library - Predefined Material Properties

Based on config_materials.json from test suite
"""

from typing import Dict, Optional
from dataclasses import dataclass
import json


@dataclass
class Material:
    """Material properties for laser cutting"""
    name: str
    thickness: float  # mm
    kerf_width: float  # mm
    min_web: float  # mm (minimum gap between parts)
    cutting_speed: float  # mm/min
    rapid_speed: float  # mm/min
    pierce_time: float  # seconds
    cost_per_sqm: float  # $ per square meter
    
    @property
    def total_offset(self) -> float:
        """Total offset needed (kerf/2 + min_web)"""
        return (self.kerf_width / 2) + self.min_web
    
    def __str__(self) -> str:
        return f"{self.name} ({self.thickness}mm): kerf={self.kerf_width}mm, web={self.min_web}mm"


class MaterialLibrary:
    """
    Library of predefined materials
    
    Matches config_materials.json for consistency
    """
    
    def __init__(self):
        self._materials: Dict[str, Material] = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default material presets"""
        
        # Mild Steel 3mm (most common)
        self.add_material(Material(
            name="mild_steel_3mm",
            thickness=3.0,
            kerf_width=0.3,
            min_web=3.0,
            cutting_speed=3000,
            rapid_speed=15000,
            pierce_time=0.5,
            cost_per_sqm=25.0
        ))
        
        # Stainless Steel 3mm
        self.add_material(Material(
            name="stainless_steel_3mm",
            thickness=3.0,
            kerf_width=0.35,
            min_web=4.0,
            cutting_speed=2500,
            rapid_speed=15000,
            pierce_time=0.7,
            cost_per_sqm=45.0
        ))
        
        # Aluminum 3mm
        self.add_material(Material(
            name="aluminum_3mm",
            thickness=3.0,
            kerf_width=0.25,
            min_web=2.5,
            cutting_speed=3500,
            rapid_speed=15000,
            pierce_time=0.4,
            cost_per_sqm=35.0
        ))
        
        # Mild Steel 5mm (thicker)
        self.add_material(Material(
            name="mild_steel_5mm",
            thickness=5.0,
            kerf_width=0.4,
            min_web=5.0,
            cutting_speed=2000,
            rapid_speed=15000,
            pierce_time=0.8,
            cost_per_sqm=40.0
        ))
        
        # Acrylic 3mm (fast cutting)
        self.add_material(Material(
            name="acrylic_3mm",
            thickness=3.0,
            kerf_width=0.15,
            min_web=2.0,
            cutting_speed=4000,
            rapid_speed=20000,
            pierce_time=0.2,
            cost_per_sqm=15.0
        ))
    
    def add_material(self, material: Material):
        """Add material to library"""
        self._materials[material.name] = material
    
    def get(self, name: str) -> Optional[Material]:
        """Get material by name"""
        return self._materials.get(name)
    
    def list_materials(self) -> list:
        """List all available materials"""
        return list(self._materials.keys())
    
    def __contains__(self, name: str) -> bool:
        return name in self._materials
    
    def __getitem__(self, name: str) -> Material:
        return self._materials[name]


# Singleton instance
_material_library = MaterialLibrary()

def get_material(name: str) -> Optional[Material]:
    """Get material from global library"""
    return _material_library.get(name)

def list_materials() -> list:
    """List all available materials"""
    return _material_library.list_materials()

