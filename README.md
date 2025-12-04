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
│   ├── feature_alignment.py # Feature alignment layer (raw → FIS)
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
│   ├── prepare_full_features.py  # Data preparation (two-stage)
│   ├── validate_alignment.py    # Alignment validation
│   └── explore_dataset.py   # Dataset exploration
│
├── data/
│   ├── raw/                 # Original dataset
│   │   └── swiss-dwellings-v3.0.0/
│   └── processed/           # Processed data
│       ├── dwellings_full.csv      # Aligned features
│       └── feature_alignment.json  # Alignment config
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

Prepare full features from raw data (two-stage processing):
```bash
uv run python scripts/prepare_full_features.py
```

This script performs:
1. **Stage 1**: Extract raw features from Swiss Dwellings dataset (original units)
2. **Stage 2**: Fit and apply feature alignment to match FIS input universes

Validate the feature alignment:
```bash
uv run python scripts/validate_alignment.py
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

Raw features (from simulations.csv and locations.csv):
- **Noise**: window_noise_traffic/train_day/night (dBA)
- **Daylight**: sun_*_mean at noon for 3 seasons (klx)
- **Views**: view_sky_p80, view_greenery_p80 (steradians)
- **Location**: walkshed_* POI counts (202 categories)

## Feature Alignment

The Feature Alignment layer transforms raw dataset values to match the FIS input universes, ensuring all dimensions properly contribute to the fuzzy inference.

### Problem Addressed

The raw Swiss Dwellings data has different scales than the FIS membership function universes:
- **view_sky**: Raw data 0-0.13 sr, but MF expects 0-4 sr
- **view_greenery**: Raw data 0-0.06 sr, but MF expects 0-2 sr
- **daylight**: Raw data in klx, but MF expects lux (0-1000)
- **location_poi**: Raw counts 3-2662, but MF expects 0-100

### Transformations

| Variable | Transformation | Purpose |
|----------|---------------|---------|
| **Daylight** | klx × 1000, cap at 1000 lux | Unit conversion to match EN 17037 |
| **View sky** | sr / ref_95pctl × 4.0 | Data-driven scaling to universe |
| **View greenery** | sr / ref_95pctl × 2.0 | Data-driven scaling to universe |
| **Location POI** | log1p + robust min-max → 0-100 | Handle long-tail distribution |
| **Noise** | Pass-through, ≤0 → missing | Already in dBA |

### Configuration

Alignment parameters are fitted on the full dataset and saved to `data/processed/feature_alignment.json`:
```json
{
  "view_sky_ref": 0.0507,
  "view_greenery_ref": 0.0258,
  "poi_log_p01": 0.0,
  "poi_log_p99": 7.44
}
```

This ensures consistency between batch processing and the web API.

## FLI Results

After feature alignment, the Fuzzy Livability Index shows a well-distributed output:

| Statistic | Value |
|-----------|-------|
| Mean | 50.43 |
| Std Dev | 22.20 |
| Min | 13.17 |
| Max | 85.91 |

**Linguistic Label Distribution:**
| Label | Count | Percentage |
|-------|-------|------------|
| Excellent | 614 | 20.5% |
| Good | 1,410 | 47.2% |
| Fair | 397 | 13.3% |
| Poor | 567 | 19.0% |

**Feature Correlations with FLI:**
- noise_lden: -0.75 (strong negative - more noise = lower livability)
- noise_lnight: -0.73 (strong negative)
- view_greenery: +0.23 (moderate positive)
- view_sky: +0.16 (moderate positive)
- daylight: +0.14 (moderate positive)

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
