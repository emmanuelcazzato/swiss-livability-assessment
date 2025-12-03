# Swiss Residential Perceived Livability Assessment

## Overview

This project implements a **Fuzzy Inference System** to assess the perceived livability of Swiss residential dwellings using the **Computing with Words** framework. The system transforms quantitative environmental simulations into linguistic assessments that align with human perception.

## Research Questions

1. **RQ1**: How to deconstruct "perceived livability" into measurable dimensions and map them to available dataset columns?
2. **RQ2**: How to design a Fuzzy Inference System to transform quantitative simulations into linguistic levels?
3. **RQ3**: How to validate the "Fuzzy Livability Index" using external benchmarks?

## Project Structure

```
swiss-livability-assessment/
├── README.md                # This file
├── pyproject.toml           # Project configuration
├── .python-version          # Python version
│
├── src/                     # Core fuzzy inference modules
│   ├── __init__.py
│   ├── data_processing.py   # Data loading and preprocessing
│   ├── membership_functions.py  # Fuzzy membership functions
│   ├── rule_base.py         # Fuzzy inference rules
│   ├── fuzzy_system.py      # Mamdani FIS implementation
│   └── validation.py        # Validation utilities
│
├── app/                     # Web application
│   ├── __init__.py
│   ├── web_app.py           # Flask web server
│   └── templates/           # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── explore.html
│       └── assess.html
│
├── scripts/                 # Utility scripts
│   ├── run_prototype.py     # Main prototype execution
│   ├── create_visualizations.py  # Generate plots
│   ├── prepare_full_features.py  # Data preparation
│   └── explore_dataset.py   # Dataset exploration
│
├── data/
│   ├── raw/                 # Original dataset
│   │   └── swiss-dwellings-v3.0.0/
│   └── processed/           # Processed data
│       └── dwellings_full.csv
│
├── results/                 # Output results
│   ├── figures/             # Visualizations
│   └── outputs/             # CSV and reports
│
└── docs/                    # Documentation
    ├── literature_review.md
    └── web_app_guide.md
```

## Installation

### Prerequisites
Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended Python package manager):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install dependencies
```bash
uv sync
```

## Usage

### Data Preprocessing

Explore the raw dataset:
```bash
uv run python scripts/explore_dataset.py
```

Prepare full features from raw data:
```bash
uv run python scripts/prepare_full_features.py
```

### Run Web Application
```bash
uv run python -m app.web_app
```
Then open http://localhost:5001 in your browser.

### Run Prototype Analysis
```bash
uv run python scripts/run_prototype.py
```

### Generate Visualizations
```bash
uv run python scripts/create_visualizations.py
```

## Dataset

**Swiss Dwellings v3.0.0** (3,171 processed dwellings)

Key features:
- **Noise**: noise_lden, noise_lnight (dBA)
- **Daylight**: daylight_avg_klx (klx)
- **Views**: view_sky, view_greenery (solid angle in sr)
- **Location**: location_poi_count

## Standards Applied

### WHO 2018 Environmental Noise Guidelines
- Road traffic: Lden < 53 dB, Lnight < 45 dB
- Railway: Lden < 54 dB, Lnight < 44 dB
- Aircraft: Lden < 45 dB, Lnight < 40 dB

### EN 17037 Daylight Provision
- **Minimum**: 300 lux over 50% of area, 100 lux over 95% of area
- **Medium**: 500 lux over 50% of area, 300 lux over 95% of area
- **High**: 750 lux over 50% of area, 500 lux over 95% of area

## Key References

1. Mendel, J. M. (2002). An architecture for making judgments using computing with words. *International Journal of Applied Mathematics and Computer Science*, 12(3), 325-335.
2. WHO (2018). Environmental Noise Guidelines for the European Region.
3. EN 17037:2018. Daylight in buildings.
4. Zadeh, L. A. (1999). From computing with numbers to computing with words. *IEEE Transactions on Circuits and Systems*, 45(1), 105-119.

## Authors

- Hao Wang
- Emmanuel Cazzato
