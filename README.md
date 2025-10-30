# Swiss Residential Perceived Livability Assessment

## Overview

This project implements a **Fuzzy Inference System (FIS)** to assess the perceived livability of Swiss residential dwellings using the **Computing with Words (CWW)** framework. The system transforms quantitative environmental simulations into linguistic assessments that align with human perception.

## Research Questions

1. **RQ1**: How to deconstruct "perceived livability" into measurable dimensions and map them to available dataset columns?
2. **RQ2**: How to design a Fuzzy Inference System to transform quantitative simulations into linguistic levels?
3. **RQ3**: How to validate the "Fuzzy Livability Index" using external benchmarks?

## Methodology

The project follows a structured approach based on the Computing with Words paradigm:

1. **Deconstruction**: Identify core dimensions of perceived livability from literature
2. **Mapping**: Correspond dimensions to Swiss Dwellings dataset features
3. **Fuzzification**: Define membership functions based on WHO 2018 and EN 17037 standards
4. **Rule-base Definition**: Apply Mamdani inference with IF-THEN rules
5. **Defuzzification**: Generate Fuzzy Livability Index (FLI) using centroid method
6. **Validation**: Correlate FLI with external expert ratings

## Dataset

**Swiss Dwellings v3.0.0** (45,176 dwellings)

Key features:
- **Noise**: window_noise_lden, window_noise_lnight (dBA)
- **Daylight**: Seasonal measurements (klx)
- **Views**: view_sky, view_greenery (solid angle in sr)
- **Location**: POI counts and distances

## Standards Applied

### WHO 2018 Environmental Noise Guidelines
- Road traffic: Lden < 53 dB, Lnight < 45 dB (Strong recommendation)
- Railway: Lden < 54 dB, Lnight < 44 dB
- Aircraft: Lden < 45 dB, Lnight < 40 dB

### EN 17037 Daylight Provision
- **Minimum**: 300 lux over 50% of area, 100 lux over 95% of area
- **Medium**: 500 lux over 50% of area, 300 lux over 95% of area
- **High**: 750 lux over 50% of area, 500 lux over 95% of area

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. Data Processing
```python
from src.data_processing import load_swiss_dwellings, preprocess_features

# Load dataset
df = load_swiss_dwellings('data/raw/swiss_dwellings.csv')

# Preprocess features
df_processed = preprocess_features(df)
```

### 2. Fuzzy System Execution
```python
from src.fuzzy_system import compute_fuzzy_livability_index

# Compute FLI for all dwellings
fli_scores = compute_fuzzy_livability_index(df_processed)
```

### 3. Validation
```python
from src.validation import validate_against_ratings

# Validate against external ratings
correlation, p_value = validate_against_ratings(fli_scores, 'data/external/location_ratings.csv')
```

## Project Structure

```
swiss_livability/
├── data/               # Dataset files
├── src/                # Source code
├── notebooks/          # Jupyter notebooks for analysis
├── results/            # Output files and visualizations
├── docs/               # Documentation and literature review
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Key References

1. Mendel, J. M. (2002). An architecture for making judgments using computing with words. *International Journal of Applied Mathematics and Computer Science*, 12(3), 325-335.
2. WHO (2018). Environmental Noise Guidelines for the European Region.
3. EN 17037:2018. Daylight in buildings.
4. Zadeh, L. A. (1999). From computing with numbers to computing with words. *IEEE Transactions on Circuits and Systems*, 45(1), 105-119.

## Authors

- Hao Wang
- Emmanuel Cazzato
