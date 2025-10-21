# Intelligent Nesting System - Project Structure

## 📁 Directory Layout

```
intelligent-nesting/
├── src/
│   ├── geometry/              # Core geometric engine
│   │   ├── __init__.py
│   │   ├── polygon.py         # Robust polygon class
│   │   ├── nfp.py            # No-Fit Polygon computation
│   │   ├── nfp_manufacturing.py  # Manufacturing-aware NFP
│   │   ├── offset.py         # Kerf & margin offsetting
│   │   ├── validation.py     # Geometry validation & fixing
│   │   └── transforms.py     # Rotation, translation, scaling
│   │
│   ├── io/                    # Input/Output handling
│   │   ├── __init__.py
│   │   ├── dxf_importer.py   # Robust DXF import
│   │   ├── svg_importer.py   # SVG import
│   │   ├── exporters.py      # DXF, SVG, JSON export
│   │   └── gcode.py          # G-code generation
│   │
│   ├── constraints/           # Constraint system
│   │   ├── __init__.py
│   │   ├── sheet.py          # Sheet constraints
│   │   ├── spacing.py        # Kerf, min web
│   │   ├── rotation.py       # Rotation constraints
│   │   └── material.py       # Material properties
│   │
│   ├── optimization/          # Core optimization algorithms
│   │   ├── __init__.py
│   │   ├── blf.py           # Bottom-Left-Fill (baseline)
│   │   ├── beam_search.py   # Beam search with lookahead
│   │   ├── mcts.py          # Monte Carlo Tree Search
│   │   ├── simulated_annealing.py
│   │   ├── genetic.py       # Genetic algorithm
│   │   └── multi_objective.py  # Multi-objective optimizer
│   │
│   ├── ai/                    # AI & Learning components (INNOVATION!)
│   │   ├── __init__.py
│   │   ├── placement_policy.py    # Learned placement network
│   │   ├── rotation_optimizer.py  # Adaptive rotation
│   │   ├── strategy_selector.py   # Algorithm selection
│   │   ├── failure_predictor.py   # Predictive failure detection
│   │   ├── job_database.py        # Historical job storage
│   │   └── models/                # Neural network models
│   │       ├── placement_net.py
│   │       ├── rotation_net.py
│   │       └── strategy_net.py
│   │
│   ├── manufacturing/         # Manufacturing-aware features
│   │   ├── __init__.py
│   │   ├── path_planner.py       # Cut sequence optimization
│   │   ├── thermal_model.py      # Thermal distortion modeling
│   │   ├── common_cutting.py     # Common line detection
│   │   ├── lead_inout.py         # Lead-in/out generation
│   │   ├── remnant_analysis.py   # Remnant value prediction
│   │   └── cost_estimator.py     # Real-time cost calculation
│   │
│   ├── scoring/               # Multi-objective scoring
│   │   ├── __init__.py
│   │   ├── objectives.py     # Individual objective functions
│   │   ├── pareto.py         # Pareto optimization
│   │   └── weights.py        # Adaptive weight learning
│   │
│   ├── engine/                # Main nesting engine
│   │   ├── __init__.py
│   │   ├── nesting_engine.py     # Main coordinator
│   │   ├── intelligent_nester.py # AI-enhanced nester
│   │   └── config.py             # Configuration management
│   │
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── geometry_utils.py
│       ├── math_utils.py
│       ├── profiling.py      # Performance monitoring
│       └── logging.py        # Structured logging
│
├── tests/                     # Test suite
│   ├── unit/
│   ├── integration/
│   └── benchmarks/
│
├── examples/                  # Usage examples
│   ├── basic_nesting.py
│   ├── advanced_features.py
│   └── api_demo.py
│
├── scripts/                   # Utility scripts
│   ├── train_models.py       # Train AI models
│   ├── benchmark.py          # Run benchmarks
│   └── analyze_jobs.py       # Analyze job history
│
├── data/                      # Data directory
│   ├── models/               # Trained models
│   ├── job_history/          # Historical jobs
│   └── training_data/        # Training datasets
│
├── docs/                      # Documentation
│   ├── api/
│   ├── algorithms/
│   └── architecture/
│
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup
└── README.md                  # Main documentation
```

## 🎯 Development Phases

### Phase 1: Days 1-2 (Foundation)
- Core geometry engine
- Manufacturing-aware NFP
- Multi-objective scoring
- Basic AI framework

### Phase 2: Days 3-4 (AI Core)
- Learned placement policy
- Adaptive rotation optimizer
- Strategy selector
- Failure predictor

### Phase 3: Days 5-6 (Advanced Search)
- Beam search implementation
- MCTS implementation
- Hybrid optimization

### Phase 4: Days 7-8 (Manufacturing)
- Path planning
- Thermal modeling
- Cost optimization
- Remnant intelligence

### Phase 5: Days 9-10 (Learning & Polish)
- Job history system
- Continuous learning
- Benchmarking
- Documentation

## 🔧 Technology Stack

- **Core**: Python 3.10+
- **Geometry**: Shapely, pyclipper, numpy
- **AI/ML**: PyTorch, scikit-learn
- **Optimization**: scipy, numpy
- **Visualization**: matplotlib, plotly
- **I/O**: ezdxf, svgwrite
- **Testing**: pytest, hypothesis
- **Profiling**: cProfile, line_profiler

