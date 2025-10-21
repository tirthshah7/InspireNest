# Quick Reference Guide

## 🚀 Quick Start Commands

```bash
# Analyze all test files
python3 analyze_all_test_files.py

# Run simple test
python3 nest.py --config "Test files/01_simple/config_simple.json" --file "Test files/01_simple/rectangles.dxf"

# Run full benchmark
python3 run_benchmark.py --config "Test files/config_benchmark.json" --output "benchmark_results"

# Generate report
python3 generate_report.py --results "benchmark_results" --format html
```

---

## 📊 Test File Cheat Sheet

| File | Parts | Size (mm) | Complexity | Use Case |
|------|-------|-----------|------------|----------|
| **rectangles.dxf** | ~1 | 121×330 | 1/10 | Basic packing |
| **circles.dxf** | 6 | 148×330 | 2/10 | Circular packing |
| **mixed_simple.dxf** | 2 | 128×330 | 2/10 | Mixed shapes |
| **brackets_L_T_sha[e.dxf** | ~1 | 50×330 | 1/10 | L/T brackets |
| **gears.dxf** | 2 | 82×338 | 3/10 | Spline curves |
| **plates_with_holes.dxf** | 12 | 160×331 | 4/10 | Nested features |
| **irregular_shapes.dxf** | 1 | 130×330 | 2/10 | Freeform |
| **nested_contours.dxf** | 5 | 155×330 | 2/10 | Holes test |

---

## ⚙️ Configuration Presets

### Materials
```json
"mild_steel_3mm"      → kerf: 0.3mm, min_web: 3mm
"stainless_steel_3mm" → kerf: 0.35mm, min_web: 4mm  
"aluminum_3mm"        → kerf: 0.25mm, min_web: 2.5mm
"mild_steel_5mm"      → kerf: 0.4mm, min_web: 5mm
"acrylic_3mm"         → kerf: 0.15mm, min_web: 2mm
```

### Sheet Sizes
```json
"standard_4x8"        → 1220 × 2440 mm
"standard_5x10"       → 1524 × 3048 mm
"metric_1000x2000"    → 1000 × 2000 mm
"metric_1500x3000"    → 1500 × 3000 mm
"small_test"          → 600 × 400 mm
```

### Rotation Presets
```json
"no_rotation"   → [0°]
"cardinal_only" → [0°, 90°, 180°, 270°]
"eight_way"     → [0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°]
"fine_grain"    → [every 10°, 0° to 350°]
```

---

## 🎯 Performance Targets

### Simple (01_simple)
```
Utilization:  75-85%
Runtime:      <30 seconds
Reliability:  100% placement
```

### Moderate (02_moderate)
```
Utilization:  78-82%
Runtime:      60-90 seconds
Reliability:  98%+ placement
```

### Complex (03_complex)
```
Utilization:  75-80%
Runtime:      120-180 seconds
Reliability:  95%+ placement
```

---

## 🔧 Common Parameter Adjustments

### To Increase Utilization (slower):
```json
{
  "rotation": {"allowed_angles": [0, 45, 90, 135, 180, 225, 270, 315]},
  "optimization": {
    "num_multi_starts": 15,
    "enable_simulated_annealing": true,
    "max_runtime_seconds": 180
  }
}
```

### To Decrease Runtime (lower utilization):
```json
{
  "rotation": {"allowed_angles": [0, 90]},
  "optimization": {
    "num_multi_starts": 3,
    "enable_simulated_annealing": false,
    "max_runtime_seconds": 30
  }
}
```

### For Production (balanced):
```json
{
  "rotation": {"allowed_angles": [0, 90, 180, 270]},
  "optimization": {
    "num_multi_starts": 10,
    "enable_simulated_annealing": true,
    "max_runtime_seconds": 60
  }
}
```

---

## 📈 Benchmark Scenarios

| Scenario | Category | Runtime | Seeds | Target | Notes |
|----------|----------|---------|-------|--------|-------|
| **simple_fast** | 01_simple | 30s | 3 | 75% | Quick check |
| **simple_full** | 01_simple | 60s | 5 | 80% | Full baseline |
| **moderate_standard** | 02_moderate | 90s | 5 | 78% | Production |
| **moderate_optimized** | 02_moderate | 180s | 10 | 82% | Best result |
| **complex_standard** | 03_complex | 120s | 5 | 75% | Standard |
| **complex_aggressive** | 03_complex | 300s | 15 | 80% | Maximum |
| **mixed_production** | mixed | 120s | 5 | 77% | Realistic |

---

## 🛠️ Troubleshooting Quick Fixes

### Problem: File won't load
```bash
✓ Check DXF version (use R12/LT2)
✓ Verify entities are in MODEL_SPACE
✓ Run: python3 validate_dxf.py your_file.dxf
```

### Problem: Low utilization (<70%)
```bash
✓ Increase rotations: "eight_way" or "fine_grain"
✓ Enable SA: "enable_simulated_annealing": true
✓ Increase runtime: "max_runtime_seconds": 180
✓ Check part size vs. sheet size
```

### Problem: Too slow
```bash
✓ Reduce rotations: "cardinal_only" or "no_rotation"
✓ Decrease multi-starts: "num_multi_starts": 3
✓ Disable SA: "enable_simulated_annealing": false
✓ Simplify geometry (reduce vertices)
```

### Problem: Parts not placing
```bash
✓ Check constraints (kerf + min_web not too large)
✓ Verify sheet margins allow space
✓ Check part dimensions vs. sheet size
✓ Look for invalid geometry (self-intersections)
```

---

## 📝 Metrics Glossary

| Metric | Description | Good Value |
|--------|-------------|------------|
| **Utilization %** | Used area / sheet area × 100 | >75% |
| **Cut Length** | Total mm of cutting | Minimize |
| **Pierce Count** | Number of laser start points | Minimize |
| **Cut Time** | Estimated cutting duration | - |
| **Machine Time** | Cut + rapid + pierce time | Minimize |
| **Runtime** | Algorithm execution time | <120s |
| **Sheets Used** | Number of sheets needed | Minimize |

---

## 🔬 Algorithm Settings Explained

### Multi-Start
- **What**: Run algorithm N times with different orderings
- **Default**: 10
- **Range**: 3-20
- **Impact**: More starts = better results, longer runtime

### Simulated Annealing (SA)
- **What**: Meta-heuristic that escapes local optima
- **When**: Complex shapes, targeting >80% utilization
- **Cost**: +50-100% runtime
- **Benefit**: +3-7% utilization improvement

### Lift-and-Drop
- **What**: Remove k parts and re-nest them
- **k value**: 3-5 typical
- **When**: Final improvement phase
- **Cost**: Moderate
- **Benefit**: +1-3% utilization

---

## 💾 Output Files

After running tests, expect these outputs:

```
results/
├── scenario_name/
│   ├── solution.json          # Final nested solution
│   ├── solution.dxf           # DXF output for CAM
│   ├── solution.svg           # Visual preview
│   ├── metrics.json           # Performance metrics
│   ├── convergence.png        # Optimization curve
│   └── report.html            # Human-readable report
```

---

## 📧 Getting Help

1. Check `README.md` for detailed documentation
2. Review test file analysis: `test_files_analysis.json`
3. Validate DXF files: `python3 validate_dxf.py file.dxf`
4. Open an issue with:
   - Config file used
   - DXF file (or description)
   - Error message / unexpected behavior
   - Expected vs. actual results

---

## 🎓 Best Practices

1. **Start Simple**: Test with 01_simple first
2. **Iterate**: Adjust configs based on results
3. **Document**: Save configs that work well
4. **Compare**: Run multiple seeds, report statistics
5. **Validate**: Check output in CAM software before cutting

---

## 🚦 Status Indicators

When viewing results:

- 🟢 **>80% utilization**: Excellent
- 🟡 **70-80% utilization**: Good
- 🟠 **60-70% utilization**: Acceptable
- 🔴 **<60% utilization**: Poor (investigate)

---

Last updated: 2025-10-17

