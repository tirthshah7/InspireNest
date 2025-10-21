"""
Unit Tests for Constraint System

Tests for sheet, spacing, rotation, and material constraints
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pytest
from constraints.sheet import SheetConstraints, SheetSizes
from constraints.spacing import SpacingConstraints
from constraints.rotation import RotationConstraints
from constraints.material import Material, MaterialLibrary, get_material, list_materials
from geometry.polygon import Polygon, Point


class TestSheetConstraints:
    """Tests for sheet constraints"""
    
    def test_sheet_creation(self):
        sheet = SheetConstraints(width=1220, height=2440)
        assert sheet.width == 1220
        assert sheet.height == 2440
    
    def test_sheet_area(self):
        sheet = SheetConstraints(1000, 2000)
        assert sheet.area == 2_000_000
    
    def test_sheet_with_margins(self):
        sheet = SheetConstraints(
            width=1000, height=2000,
            margin_left=10, margin_right=10,
            margin_top=10, margin_bottom=10
        )
        
        assert sheet.usable_width == 980
        assert sheet.usable_height == 1980
        assert sheet.usable_area == 980 * 1980
    
    def test_usable_bounds(self):
        sheet = SheetConstraints(100, 100, 5, 5, 5, 5)
        bounds = sheet.get_usable_bounds()
        
        assert bounds.min_x == 5
        assert bounds.max_x == 95
        assert bounds.min_y == 5
        assert bounds.max_y == 95
    
    def test_fits_in_sheet_true(self):
        sheet = SheetConstraints(100, 100, 5, 5, 5, 5)
        part = Polygon([(10, 10), (30, 10), (30, 30), (10, 30)])
        
        assert sheet.fits_in_sheet(part) == True
    
    def test_fits_in_sheet_false(self):
        sheet = SheetConstraints(100, 100, 5, 5, 5, 5)
        # Part too large
        part = Polygon([(0, 0), (200, 0), (200, 100), (0, 100)])
        
        assert sheet.fits_in_sheet(part) == False
    
    def test_fits_in_sheet_with_position(self):
        sheet = SheetConstraints(100, 100, 0, 0, 0, 0)
        part = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        
        # Should fit at (0, 0)
        assert sheet.fits_in_sheet(part, Point(0, 0)) == True
        
        # Should NOT fit at (95, 95) - would exceed bounds
        assert sheet.fits_in_sheet(part, Point(95, 95)) == False
    
    def test_preset_sheets(self):
        """Test preset sheet sizes"""
        assert SheetSizes.STANDARD_4X8.width == 1220
        assert SheetSizes.STANDARD_4X8.height == 2440
        assert SheetSizes.SMALL_TEST.width == 600


class TestSpacingConstraints:
    """Tests for spacing constraints"""
    
    def test_spacing_creation(self):
        spacing = SpacingConstraints(kerf_width=0.3, min_web=3.0)
        assert spacing.kerf_width == 0.3
        assert spacing.min_web == 3.0
    
    def test_total_spacing(self):
        spacing = SpacingConstraints(kerf_width=0.4, min_web=5.0)
        assert spacing.total_spacing == 5.4
    
    def test_offset_per_part(self):
        spacing = SpacingConstraints(kerf_width=0.4, min_web=5.0)
        # Offset = kerf/2 + min_web = 0.2 + 5.0 = 5.2
        assert spacing.offset_per_part == pytest.approx(5.2, abs=1e-6)
    
    def test_from_dict(self):
        data = {'kerf_width': 0.35, 'min_web': 4.0}
        spacing = SpacingConstraints.from_dict(data)
        assert spacing.kerf_width == 0.35
        assert spacing.min_web == 4.0
    
    def test_from_dict_defaults(self):
        data = {}
        spacing = SpacingConstraints.from_dict(data)
        assert spacing.kerf_width == 0.3
        assert spacing.min_web == 3.0


class TestRotationConstraints:
    """Tests for rotation constraints"""
    
    def test_rotation_creation_default(self):
        rotation = RotationConstraints()
        assert rotation.allowed_angles == [0, 90, 180, 270]
    
    def test_rotation_custom_angles(self):
        rotation = RotationConstraints(allowed_angles=[0, 45, 90])
        assert rotation.allowed_angles == [0, 45, 90]
    
    def test_get_allowed_rotations_global(self):
        rotation = RotationConstraints(allowed_angles=[0, 90])
        assert rotation.get_allowed_rotations('part_1') == [0, 90]
    
    def test_get_allowed_rotations_per_part_override(self):
        rotation = RotationConstraints(
            allowed_angles=[0, 90, 180, 270],
            per_part_overrides={'special_part': [0]}
        )
        
        assert rotation.get_allowed_rotations('normal_part') == [0, 90, 180, 270]
        assert rotation.get_allowed_rotations('special_part') == [0]
    
    def test_is_rotation_allowed_true(self):
        rotation = RotationConstraints(allowed_angles=[0, 90])
        assert rotation.is_rotation_allowed('part_1', 0) == True
        assert rotation.is_rotation_allowed('part_1', 90) == True
    
    def test_is_rotation_allowed_false(self):
        rotation = RotationConstraints(allowed_angles=[0, 90])
        assert rotation.is_rotation_allowed('part_1', 45) == False
        assert rotation.is_rotation_allowed('part_1', 180) == False
    
    def test_set_part_rotations(self):
        rotation = RotationConstraints()
        rotation.set_part_rotations('gear', [0])
        assert rotation.get_allowed_rotations('gear') == [0]
    
    def test_preset_no_rotation(self):
        rotation = RotationConstraints.no_rotation()
        assert rotation.allowed_angles == [0]
        assert rotation.grain_sensitive == True
    
    def test_preset_cardinal_only(self):
        rotation = RotationConstraints.cardinal_only()
        assert rotation.allowed_angles == [0, 90, 180, 270]
    
    def test_preset_eight_way(self):
        rotation = RotationConstraints.eight_way()
        assert len(rotation.allowed_angles) == 8
        assert 45 in rotation.allowed_angles
    
    def test_preset_fine_grain(self):
        rotation = RotationConstraints.fine_grain()
        assert len(rotation.allowed_angles) == 36
        assert rotation.allowed_angles[1] == 10


class TestMaterial:
    """Tests for Material class"""
    
    def test_material_creation(self):
        material = Material(
            name="steel",
            thickness=3.0,
            kerf_width=0.3,
            min_web=3.0,
            cutting_speed=3000,
            rapid_speed=15000,
            pierce_time=0.5,
            cost_per_sqm=25.0
        )
        
        assert material.name == "steel"
        assert material.thickness == 3.0
        assert material.kerf_width == 0.3
    
    def test_material_total_offset(self):
        material = Material(
            name="test",
            thickness=3.0,
            kerf_width=0.4,
            min_web=5.0,
            cutting_speed=3000,
            rapid_speed=15000,
            pierce_time=0.5,
            cost_per_sqm=25.0
        )
        
        # total = kerf/2 + min_web = 0.2 + 5.0 = 5.2
        assert material.total_offset == pytest.approx(5.2, abs=1e-6)


class TestMaterialLibrary:
    """Tests for material library"""
    
    def test_library_has_defaults(self):
        library = MaterialLibrary()
        materials = library.list_materials()
        
        assert 'mild_steel_3mm' in materials
        assert 'aluminum_3mm' in materials
        assert len(materials) >= 5
    
    def test_library_get_material(self):
        library = MaterialLibrary()
        steel = library.get('mild_steel_3mm')
        
        assert steel is not None
        assert steel.name == 'mild_steel_3mm'
        assert steel.thickness == 3.0
    
    def test_library_add_custom_material(self):
        library = MaterialLibrary()
        
        custom = Material(
            name="custom_brass",
            thickness=2.0,
            kerf_width=0.25,
            min_web=2.5,
            cutting_speed=3500,
            rapid_speed=18000,
            pierce_time=0.3,
            cost_per_sqm=50.0
        )
        
        library.add_material(custom)
        assert 'custom_brass' in library.list_materials()
        assert library.get('custom_brass') == custom
    
    def test_library_contains(self):
        library = MaterialLibrary()
        assert 'mild_steel_3mm' in library
        assert 'nonexistent_material' not in library
    
    def test_library_getitem(self):
        library = MaterialLibrary()
        steel = library['mild_steel_3mm']
        assert steel.name == 'mild_steel_3mm'
    
    def test_global_get_material(self):
        """Test global get_material function"""
        material = get_material('aluminum_3mm')
        assert material is not None
        assert material.name == 'aluminum_3mm'
    
    def test_global_list_materials(self):
        """Test global list_materials function"""
        materials = list_materials()
        assert len(materials) >= 5
        assert 'mild_steel_3mm' in materials


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

