# Test Files & Benchmark Suite

## Overview

This directory contains a comprehensive test suite for evaluating laser cutting nesting algorithms. The test files are organized by complexity and include configuration files for various optimization scenarios.

---

## Directory Structure

```
Test files/
├── 01_simple/              # Basic shapes for baseline testing
│   ├── rectangles.dxf      # ~25 entities, simple rectangles
│   ├── circles.dxf         # 6 circles, circular packing test
│   ├── mixed_simple.dxf    # Mix of circles, lines, arcs
│   ├── Rectangles_circles.dxf
│   └── config_simple.json  # Configuration for simple tests
│
├── 02_moderate/            # Moderate complexity parts
│   ├── brackets_L_T_sha[e.dxf  # L and T shaped brackets
│   ├── gears.dxf           # 228 SPLINE entities (curve test)
│   ├── plates_with_holes.dxf   # Plates with circular holes
│   └── config_moderate.json
│
├── 03_complex/             # Complex irregular shapes
│   ├── irregular_shapes.dxf    # Freeform irregular geometry
│   ├── nested_contours.dxf     # Shapes with holes
│   └── config_complex.json
│
├── config_template.json    # Master configuration template
├── config_materials.json   # Material & sheet size presets
├── config_benchmark.json   # Benchmark suite configuration
└── README.md              # This file
```

---

## Test File Analysis Summary

| Category | Files | Est. Parts | Avg Complexity | Key Features |
|----------|-------|------------|----------------|--------------|
| **01_simple** | 4 | ~10 | 1.6/10 | Rectangles, circles, basic shapes |
| **02_moderate** | 3 | ~15 | 2.7/10 | Brackets, gears (splines), holes |
| **03_complex** | 2 | ~6 | 1.9/10 | Irregular shapes, nested contours |
| **Total** | 9 | ~32 | 2.1/10 | Full spectrum of part types |

---

## Configuration Files

### 1. `config_template.json`
Master template with all available parameters:
- Sheet dimensions & material properties
- Constraint definitions (kerf, min web, margins)
- Rotation settings
- Optimization parameters
- Manufacturing settings
- Output formats

### 2. Category-Specific Configs
- **`01_simple/config_simple.json`**: Fast testing, 75%+ utilization target
- **`02_moderate/config_moderate.json`**: Standard production settings, 78%+ target
- **`03_complex/config_complex.json`**: Aggressive optimization, 75%+ target

### 3. `config_materials.json`
Predefined material profiles:
- **Mild Steel 3mm**: Standard (kerf 0.3mm, min web 3mm)
- **Stainless Steel 3mm**: Tighter tolerances (kerf 0.35mm, min web 4mm)
- **Aluminum 3mm**: Faster cutting (kerf 0.25mm, min web 2.5mm)
- **Mild Steel 5mm**: Thicker material (kerf 0.4mm, min web 5mm)
- **Acrylic 3mm**: Very fast (kerf 0.15mm, min web 2mm)

Sheet size presets:
- 1220×2440mm (4'×8' standard)
- 1524×3048mm (5'×10' large format)
- 1000×2000mm, 1500×3000mm (metric)
- 600×400mm (small test)

### 4. `config_benchmark.json`
Complete benchmark suite with 7 scenarios:
1. **simple_fast**: Quick 30s sanity check
2. **simple_full**: Full simple suite (60s)
3. **moderate_standard**: Standard settings (90s)
4. **moderate_optimized**: Enhanced with SA (180s)
5. **complex_standard**: Complex parts, 4 rotations (120s)
6. **complex_aggressive**: Maximum optimization (300s)
7. **mixed_production**: Realistic production mix (120s)

---

## Quick Start

### Running a Single Test

```python
from nesting import NestingEngine

# Load configuration
config = load_config("Test files/01_simple/config_simple.json")

# Run nesting
engine = NestingEngine(config)
result = engine.nest("Test files/01_simple/rectangles.dxf")

# Check results
print(f"Utilization: {result.utilization_percent:.1f}%")
print(f"Runtime: {result.runtime_seconds:.2f}s")
```

### Running Full Benchmark

```bash
python run_benchmark.py --config "Test files/config_benchmark.json"
```

---

## Expected Performance Targets

### 01_simple (Baseline)
- **Utilization**: 75-85%
- **Runtime**: <30s per file
- **Reliability**: 100% placement
- **Notes**: Basic shapes should pack efficiently

### 02_moderate (Production)
- **Utilization**: 78-82%
- **Runtime**: 60-90s per file
- **Reliability**: 98%+
- **Notes**: Real-world manufacturing scenarios

### 03_complex (Challenging)
- **Utilization**: 75-80%
- **Runtime**: 120-180s per file
- **Reliability**: 95%+
- **Notes**: Irregular shapes are inherently harder

---

## Key Constraint Parameters Explained

### Kerf Width
- **Definition**: Width of material removed by laser cutting
- **Typical Values**: 0.15mm (acrylic) to 0.4mm (thick steel)
- **Impact**: Parts must be offset by kerf/2 to maintain dimensions

### Min Web (Bridge)
- **Definition**: Minimum gap between adjacent parts
- **Typical Values**: 2mm (thin) to 5mm (thick materials)
- **Purpose**: Structural integrity, heat management, part stability

### Sheet Margins
- **Definition**: Safe border around sheet edge
- **Typical Values**: 5-10mm
- **Purpose**: Clamping area, edge quality issues

### Allowed Rotations
- **4-way (cardinal)**: Fast, 0°/90°/180°/270° only
- **8-way**: Better packing, 45° increments
- **36-way**: Optimal but slow, 10° increments
- **No rotation**: Grain-sensitive materials

---

## Benchmark Metrics

Each test run collects:

1. **Utilization Metrics**
   - Area utilization % (used area / sheet area)
   - Material waste %
   - Number of sheets used

2. **Manufacturing Metrics**
   - Total cut length (mm)
   - Number of pierces
   - Estimated cut time
   - Estimated rapid travel time
   - Total machine time

3. **Algorithm Performance**
   - Runtime (wall clock seconds)
   - Number of iterations
   - Convergence curve
   - Parts placed vs. failed

4. **Cost Estimates**
   - Material cost (based on utilization)
   - Time cost (machine rate × time)
   - Total job cost

---

## Comparison with Commercial Tools

Expected performance ranges (based on literature):

| Tool | Simple | Moderate | Complex | Runtime |
|------|--------|----------|---------|---------|
| **Deepnest (OSS)** | 75-80% | 72-78% | 68-75% | Medium |
| **TruNest** | 80-88% | 78-85% | 75-82% | Fast |
| **SigmaNEST** | 82-90% | 80-87% | 78-85% | Fast |
| **Our Target** | 75-85% | 78-82% | 75-80% | Fast |

*Note: These are typical ranges; actual results vary by part mix*

---

## Testing Best Practices

### 1. Reproducibility
- Use fixed random seeds (42, 123, 456, 789, 1000)
- Log all parameters and versions
- Save intermediate solutions

### 2. Multiple Runs
- Run each test with 5+ different seeds
- Report mean, std dev, min, max
- Plot convergence curves

### 3. Fair Comparisons
- Same sheet size and material
- Same constraint values
- Same rotation options
- Record exact versions and hardware

### 4. Document Edge Cases
- Failed placements
- Unexpected behaviors
- Performance bottlenecks

---

## Adding New Test Files

To add your own test files:

1. Place DXF file in appropriate category folder
2. Update category config JSON:
   ```json
   "test_files": [
     "existing_file.dxf",
     "your_new_file.dxf"
   ]
   ```
3. Run analysis: `python analyze_all_test_files.py`
4. Verify results and adjust expected metrics

---

## Troubleshooting

### File Won't Load
- Check DXF version (R12/LT2 or AC1014 recommended)
- Verify entities are in MODEL_SPACE (not PAPER_SPACE)
- Check for invalid geometry (self-intersections, zero-length segments)

### Low Utilization
- Try more rotations (8-way or 36-way)
- Increase optimization runtime
- Enable simulated annealing
- Check if parts are too large for sheet

### Slow Performance
- Reduce rotation options
- Decrease multi-start count
- Disable SA for simple parts
- Check for geometry with many vertices

---

## Contributing

When contributing test files:
1. Use descriptive filenames
2. Include source/origin information
3. Specify expected difficulty level
4. Provide reference images if possible
5. Document any special requirements

---

## License

Test files and configurations are provided for benchmarking and development purposes.

---

## Contact

For questions or issues with test files, please open an issue on the project repository.

