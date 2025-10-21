#!/usr/bin/env python3
"""
Comprehensive DXF test file analyzer
"""
import os
import json
from pathlib import Path

def analyze_dxf_detailed(filepath):
    """Detailed DXF analysis"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Count entities
        entities = {}
        entity_markers = ['CIRCLE', 'LINE', 'LWPOLYLINE', 'ARC', 'POLYLINE', 
                         'SPLINE', 'ELLIPSE', 'POINT', 'INSERT']
        
        for i, line in enumerate(lines):
            if line.strip() in entity_markers:
                entities[line.strip()] = entities.get(line.strip(), 0) + 1
        
        # Extract coordinates for bounds
        coords_x, coords_y = [], []
        for i, line in enumerate(lines):
            if line.strip() in ['10', '20']:
                if i + 1 < len(lines):
                    try:
                        val = float(lines[i + 1].strip())
                        if line.strip() == '10':
                            coords_x.append(val)
                        else:
                            coords_y.append(val)
                    except:
                        pass
        
        # Calculate bounds and complexity
        result = {
            'filename': os.path.basename(filepath),
            'path': filepath,
            'file_size_kb': len(content) / 1024,
            'entities': entities,
            'total_entities': sum(entities.values()),
            'bounds': None,
            'estimated_parts': 0,
            'complexity_score': 0
        }
        
        if coords_x and coords_y:
            result['bounds'] = {
                'min_x': round(min(coords_x), 2),
                'max_x': round(max(coords_x), 2),
                'min_y': round(min(coords_y), 2),
                'max_y': round(max(coords_y), 2),
                'width': round(max(coords_x) - min(coords_x), 2),
                'height': round(max(coords_y) - min(coords_y), 2)
            }
            
            # Estimate number of parts (rough heuristic)
            if 'CIRCLE' in entities:
                result['estimated_parts'] += entities['CIRCLE']
            if 'LWPOLYLINE' in entities:
                result['estimated_parts'] += entities['LWPOLYLINE']
            if 'POLYLINE' in entities:
                result['estimated_parts'] += entities['POLYLINE']
            
            # Complexity score (0-10)
            complexity = 0
            complexity += min(entities.get('LWPOLYLINE', 0), 5)  # up to 5 points
            complexity += min(entities.get('ARC', 0) * 0.5, 2)   # up to 2 points
            complexity += min(entities.get('CIRCLE', 0) * 0.2, 1) # up to 1 point
            complexity += min(entities.get('SPLINE', 0), 2)      # up to 2 points
            result['complexity_score'] = round(complexity, 1)
        
        return result
        
    except Exception as e:
        return {
            'filename': os.path.basename(filepath),
            'path': filepath,
            'error': str(e)
        }

def scan_test_directory(base_path):
    """Scan all test files"""
    test_dirs = {
        '01_simple': [],
        '02_moderate': [],
        '03_complex': []
    }
    
    for category in test_dirs.keys():
        category_path = os.path.join(base_path, category)
        if os.path.exists(category_path):
            for file in os.listdir(category_path):
                if file.endswith('.dxf'):
                    filepath = os.path.join(category_path, file)
                    analysis = analyze_dxf_detailed(filepath)
                    test_dirs[category].append(analysis)
    
    return test_dirs

def print_analysis(test_dirs):
    """Print formatted analysis"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST FILE ANALYSIS")
    print("="*80 + "\n")
    
    for category, files in test_dirs.items():
        print(f"\n{'='*80}")
        print(f"CATEGORY: {category}")
        print('='*80)
        
        if not files:
            print("  No files found")
            continue
        
        for file_info in files:
            print(f"\n📄 {file_info['filename']}")
            print(f"   Size: {file_info.get('file_size_kb', 0):.2f} KB")
            
            if 'error' in file_info:
                print(f"   ❌ ERROR: {file_info['error']}")
                continue
            
            print(f"   Entities: {file_info['total_entities']} total")
            if file_info['entities']:
                for etype, count in file_info['entities'].items():
                    print(f"      • {etype}: {count}")
            
            if file_info['bounds']:
                b = file_info['bounds']
                print(f"   Bounds: [{b['min_x']}, {b['min_y']}] to [{b['max_x']}, {b['max_y']}]")
                print(f"   Size: {b['width']:.2f} × {b['height']:.2f} mm")
            
            print(f"   Est. Parts: ~{file_info['estimated_parts']}")
            print(f"   Complexity: {file_info['complexity_score']}/10")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print('='*80)
    
    total_files = sum(len(files) for files in test_dirs.values())
    total_parts = sum(f.get('estimated_parts', 0) for files in test_dirs.values() for f in files)
    
    print(f"Total test files: {total_files}")
    print(f"Total estimated parts: {total_parts}")
    
    for category, files in test_dirs.items():
        if files:
            avg_complexity = sum(f.get('complexity_score', 0) for f in files) / len(files)
            print(f"{category}: {len(files)} files, avg complexity: {avg_complexity:.1f}")

if __name__ == "__main__":
    base_path = "Test files"
    test_dirs = scan_test_directory(base_path)
    print_analysis(test_dirs)
    
    # Save to JSON for config generation
    output_file = "test_files_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(test_dirs, f, indent=2)
    print(f"\n✅ Analysis saved to: {output_file}")

