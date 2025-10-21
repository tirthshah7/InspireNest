# Test Suite Summary & Configuration Overview

## 📋 Executive Summary

**Complete test suite for laser cutting nesting algorithm validation**

- **9 DXF test files** organized into 3 complexity categories
- **~32 estimated parts** covering full spectrum of manufacturing scenarios
- **7 benchmark configurations** with comprehensive configuration files
- **5+ material presets** with realistic cutting parameters
- **4 rotation strategies** from fixed to fine-grain

---

## 📊 Test Files Breakdown

### Category 01: Simple (Baseline Testing)
**Purpose**: Establish baseline performance and validate basic functionality

| File | Entities | Est. Parts | Key Test |
|------|----------|------------|----------|
| rectangles.dxf | 25 (1 LWPOLYLINE, 24 LINE) | 1 | Basic rectangular packing |
| circles.dxf | 7 (1 LWPOLYLINE, 6 CIRCLE) | 6 | Circular packing optimization |
| mixed_simple.dxf | 16 (LWPOLYLINE, CIRCLE, LINE, ARC) | 2 | Mixed geometry handling |
| Rectangles_circles.dxf | 1 LWPOLYLINE | 1 | Simple test case |

**Expected Performance**: 75-85% utilization, <30s runtime, 100% placement

---

### Category 02: Moderate (Production Scenarios)
**Purpose**: Simulate realistic manufacturing workloads

| File | Entities | Est. Parts | Key Test |
|------|----------|------------|----------|
| brackets_L_T_sha[e.dxf | 29 (1 LWPOLYLINE, 28 LINE) | 1 | L/T bracket shapes, common line cutting |
| gears.dxf | 242 (228 SPLINE!) | 2 | **CRITICAL**: Spline curve handling |
| plates_with_holes.dxf | 32 (LWPOLYLINE, LINE, CIRCLE, ARC) | 12 | Nested features, hole detection |

**Expected Performance**: 78-82% utilization, 60-90s runtime, 98% placement

**⚠️ Special Note**: `gears.dxf` contains 228 SPLINE entities - this is a **critical test** for curve approximation and geometry handling!

---

### Category 03: Complex (Edge Cases)
**Purpose**: Stress test with challenging irregular geometries

| File | Entities | Est. Parts | Key Test |
|------|----------|------------|----------|
| irregular_shapes.dxf | 34 (LWPOLYLINE, LINE, ARC) | 1 | Freeform irregular geometry, NFP computation |
| nested_contours.dxf | 43 (LWPOLYLINE, 4 CIRCLE, LINE) | 5 | Multiple holes, inner-before-outer sequencing |

**Expected Performance**: 75-80% utilization, 120-180s runtime, 95% placement

---

## ⚙️ Configuration Files Created

### 1. Master Template (`config_template.json`)
Complete reference with all available parameters:
- Sheet specifications (dimensions, material, cost)
- Constraints (kerf, min web, margins, part limits)
- Rotation rules (angles, grain sensitivity, per-part overrides)
- Optimization settings (runtime, multi-start, SA, local search)
- Manufacturing parameters (speeds, pierce time, lead-ins)
- Output formats (DXF, SVG, JSON, G-code)

**Use**: Copy and customize for new scenarios

---

### 2. Category Configs

#### `01_simple/config_simple.json`
- **Sheet**: 600×400mm (small test sheet)
- **Material**: Mild steel 3mm
- **Rotations**: Cardinal only (4 angles)
- **Runtime**: 30s
- **Target**: 80% utilization
- **Strategy**: Quick validation, prove basic functionality

#### `02_moderate/config_moderate.json`
- **Sheet**: 1220×2440mm (standard 4×8 ft)
- **Material**: Mild steel 3mm
- **Rotations**: Cardinal (4 angles), gears fixed at 0°
- **Runtime**: 60s
- **Target**: 82% utilization
- **Strategy**: Full optimization with SA, common line cutting enabled
- **Special**: Per-part rotation override for gears

#### `03_complex/config_complex.json`
- **Sheet**: 1220×2440mm (standard 4×8 ft)
- **Material**: Stainless steel 3mm (tighter tolerances)
- **Rotations**: 8-way (45° steps)
- **Runtime**: 120s
- **Target**: 85% utilization
- **Strategy**: Aggressive - SA, lift-and-drop, adaptive lead-ins
- **Features**: All advanced features enabled

---

### 3. Material Library (`config_materials.json`)

**5 Material Presets**:

| Material | Thickness | Kerf | Min Web | Speed | Pierce | Cost/m² |
|----------|-----------|------|---------|-------|--------|---------|
| Mild Steel | 3mm | 0.3mm | 3mm | 3000 mm/min | 0.5s | $25 |
| Stainless | 3mm | 0.35mm | 4mm | 2500 mm/min | 0.7s | $45 |
| Aluminum | 3mm | 0.25mm | 2.5mm | 3500 mm/min | 0.4s | $35 |
| Mild Steel | 5mm | 0.4mm | 5mm | 2000 mm/min | 0.8s | $40 |
| Acrylic | 3mm | 0.15mm | 2mm | 4000 mm/min | 0.2s | $15 |

**5 Sheet Size Presets**:
- Standard 4×8: 1220×2440mm (most common)
- Standard 5×10: 1524×3048mm (large format)
- Metric 1m×2m: 1000×2000mm
- Metric 1.5m×3m: 1500×3000mm
- Test sheet: 600×400mm (development)

**4 Rotation Strategies**:
- No rotation: [0°] - grain-sensitive materials
- Cardinal: [0°, 90°, 180°, 270°] - balanced speed/quality
- 8-way: [every 45°] - better packing
- Fine-grain: [every 10°] - optimal but slow

---

### 4. Benchmark Suite (`config_benchmark.json`)

**7 Predefined Scenarios**:

1. **simple_fast** (30s) - Quick sanity check
   - Files: rectangles + circles
   - Seeds: 3
   - Purpose: CI/CD validation

2. **simple_full** (60s) - Full baseline
   - Files: All 01_simple
   - Seeds: 5
   - Purpose: Establish performance floor

3. **moderate_standard** (90s) - Production typical
   - Files: All 02_moderate
   - Seeds: 5
   - Purpose: Real-world manufacturing

4. **moderate_optimized** (180s) - Best effort
   - Files: All 02_moderate
   - Seeds: 10
   - SA: Enabled
   - Purpose: Maximum quality for production

5. **complex_standard** (120s) - Irregular shapes
   - Files: All 03_complex
   - Seeds: 5
   - Rotations: 4-way
   - Purpose: Baseline for difficult parts

6. **complex_aggressive** (300s) - Ultimate optimization
   - Files: All 03_complex
   - Seeds: 15
   - Rotations: 8-way
   - SA + Lift-Drop: Enabled
   - Purpose: Prove algorithm capability

7. **mixed_production** (120s) - Realistic mix
   - Files: One from each category
   - Seeds: 5
   - Purpose: Real job simulation

---

## 📈 Performance Expectations

### Comparison with Commercial Tools

Based on literature and industry benchmarks:

| Tool | Simple | Moderate | Complex | Speed |
|------|--------|----------|---------|-------|
| **Manual Nesting** | 60-70% | 55-65% | 50-60% | Very Slow |
| **Deepnest (OSS)** | 75-80% | 72-78% | 68-75% | Medium |
| **TruNest** | 80-88% | 78-85% | 75-82% | Fast |
| **SigmaNEST** | 82-90% | 80-87% | 78-85% | Fast |
| **Our v1.0 Target** | 75-85% | 78-82% | 75-80% | Fast |

**Our Goal**: Match open-source tools immediately, approach commercial quality within 3 months

---

## 🎯 Success Criteria (10-Day Milestone)

### Day 10 Deliverables Checklist:

#### ✅ Geometry & Constraints (Days 1-3)
- [ ] Load all 9 DXF files without errors
- [ ] Handle SPLINE entities (gears.dxf)
- [ ] Detect nested contours (holes) correctly
- [ ] Apply kerf offset accurately
- [ ] Enforce min web constraints
- [ ] Respect sheet margins

#### ✅ Optimizer (Days 4-6)
- [ ] Multi-start BLF implemented
- [ ] Local search improving results by 5-10%
- [ ] SA optional but functional
- [ ] Simple shapes: >75% utilization
- [ ] Moderate shapes: >70% utilization
- [ ] Complex shapes: >65% utilization

#### ✅ Manufacturability (Days 7-8)
- [ ] Cut sequence: inner-before-outer
- [ ] Lead-in/out generation
- [ ] Cut time estimation
- [ ] DXF/SVG export working
- [ ] G-code generation (basic)

#### ✅ Benchmarks (Days 9-10)
- [ ] All 7 scenarios run successfully
- [ ] Metrics collected and saved
- [ ] Comparison table generated
- [ ] Visual outputs (plots, nested previews)
- [ ] README with results published

---

## 🔍 Critical Test Cases

### Must-Pass Tests:

1. **rectangles.dxf** - If this fails, everything fails
2. **gears.dxf** - 228 SPLINES - curve handling litmus test
3. **plates_with_holes.dxf** - Nested feature detection
4. **nested_contours.dxf** - Inner-before-outer sequencing
5. **mixed_production** - Realistic scenario

---

## 🛠️ Using the Test Suite

### Development Workflow:

```bash
# 1. Validate test files
python3 analyze_all_test_files.py

# 2. Run single quick test
python3 nest.py --config "Test files/01_simple/config_simple.json" \
                --file "Test files/01_simple/rectangles.dxf" \
                --output results/test1

# 3. Run category
python3 nest_batch.py --config "Test files/01_simple/config_simple.json" \
                      --output results/simple_batch

# 4. Run full benchmark
python3 run_benchmark.py --config "Test files/config_benchmark.json" \
                         --output results/benchmark_$(date +%Y%m%d)

# 5. Generate report
python3 generate_report.py --input results/benchmark_* \
                            --format html \
                            --output benchmark_report.html
```

### CI/CD Integration:

```yaml
# .github/workflows/test.yml
test:
  - name: Quick Test
    run: python3 nest.py --config "Test files/01_simple/config_simple.json" \
                          --scenario "simple_fast" \
                          --timeout 60
  
  - name: Assert Minimum Performance
    run: python3 assert_performance.py \
           --results results/ \
           --min-utilization 70 \
           --max-runtime 90
```

---

## 📚 Documentation Files

All documentation included:

1. **README.md** - Comprehensive guide (full details)
2. **QUICK_REFERENCE.md** - Cheat sheet (quick lookup)
3. **TEST_SUITE_SUMMARY.md** - This file (overview)
4. **test_files_analysis.json** - Machine-readable analysis

---

## 🚀 Next Steps

### After Configuration (Immediate):

1. **Validate Setup**
   ```bash
   python3 validate_test_suite.py
   ```

2. **Run First Test**
   ```bash
   python3 nest.py --config "Test files/01_simple/config_simple.json" \
                   --file "Test files/01_simple/rectangles.dxf"
   ```

3. **Verify Output**
   - Check DXF output loads in CAM software
   - Verify SVG preview looks correct
   - Confirm metrics JSON is complete

### During Development (Days 1-10):

- **Daily**: Run simple_fast (30s) to catch regressions
- **Every 2 days**: Run simple_full + moderate_standard
- **Day 10**: Full benchmark suite

### After 10 Days (Continuous):

- Add customer DXF files to test suite
- Tune parameters based on real jobs
- Compare with Deepnest/commercial tools
- Publish benchmark results

---

## 🎓 Learning from Results

### Analyzing Utilization:

- **>85%**: Excellent! (Rare for complex shapes)
- **80-85%**: Very good (commercial quality)
- **75-80%**: Good (acceptable for production)
- **70-75%**: Fair (room for improvement)
- **<70%**: Poor (investigate constraints or algorithm)

### Common Issues:

1. **Low utilization + fast runtime** → Need more optimization (increase runtime, enable SA)
2. **Low utilization + slow runtime** → Algorithm not converging (check geometry validity)
3. **High utilization but parts won't fit** → Constraints too tight (kerf + min web)
4. **Crash on specific file** → Geometry issue (self-intersections, invalid curves)

---

## 📊 Metrics Interpretation

### Primary Metric: Utilization %
```
Utilization = (Sum of part areas) / (Sheet area × sheets used) × 100
```
- Accounts for material waste
- Higher is better
- Industry standard metric

### Secondary Metrics:
- **Cut Length**: Affects machine time and tool wear
- **Pierce Count**: Each pierce adds 0.5-1.0 seconds
- **Machine Time**: Cut time + rapid time + pierce time
- **Cost**: Material cost + (machine rate × time)

---

## ✅ Configuration Validation Checklist

Before running tests, verify:

- [ ] All config files are valid JSON
- [ ] File paths are correct
- [ ] Sheet dimensions > max part dimensions
- [ ] kerf_width + min_web < smallest part feature
- [ ] Rotation angles are valid (0-359)
- [ ] Runtime limits are reasonable
- [ ] Material parameters match actual equipment

---

**Test Suite Version**: 1.0.0  
**Last Updated**: 2025-10-17  
**Status**: ✅ Ready for use  
**Files**: 9 DXF + 7 configs + 3 docs = Complete!

