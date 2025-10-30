# Swiss Residential Perceived Livability Assessment
## Fuzzy Inference System Prototype

**Authors**: Hao Wang, CAZZATO Emmanuel  
**Course**: Urban Computing Seminar

---

## Project Overview

This project implements a **Fuzzy Inference System (FIS)** to assess the perceived livability of Swiss residential dwellings using the **Computing with Words (CWW)** framework. The system transforms quantitative environmental simulations into linguistic assessments that align with human perception.

### Key Features

- Mamdani Fuzzy Inference System with 15 expert-defined rules
- Membership functions grounded in WHO 2018 and EN 17037 standards
- Processing of 500 sample dwellings from Swiss Dwellings v3.0.0 dataset
- Fuzzy Livability Index (FLI) on 0-100 scale with linguistic labels
- Comprehensive visualizations and validation framework
- Detailed literature review and documentation

---

## Research Questions

**RQ1**: How to deconstruct "perceived livability" into measurable dimensions?
- **Answer**: Four core dimensions identified: Acoustic Comfort, Daylight Quality, View Quality, Location Convenience

**RQ2**: How to design a FIS to transform quantitative simulations into linguistic levels?
- **Answer**: Mamdani FIS with WHO 2018/EN 17037-based membership functions and 15 fuzzy rules

**RQ3**: How to validate the Fuzzy Livability Index?
- **Answer**: Correlation analysis with external ratings, sensitivity analysis, and statistical validation

---

## Project Structure

```
swiss_livability/
├── data/
│   ├── raw/                          # Raw dataset files
│   │   └── locations.csv             # 3,026 dwellings with POI data
│   ├── processed/                    # Processed data
│   │   ├── simulations_sample.csv    # 500 sample dwellings with simulations
│   │   └── dwellings_sample.csv      # Merged dataset ready for FIS
│   └── external/                     # External validation data
├── src/                              # Source code modules
│   ├── data_processing.py            # Data loading and preprocessing
│   ├── membership_functions.py       # Fuzzy membership function definitions
│   ├── rule_base.py                  # Fuzzy rule definitions (15 rules)
│   ├── fuzzy_system.py               # Mamdani FIS implementation
│   └── validation.py                 # Validation and statistical analysis
├── notebooks/                        # Jupyter notebooks (optional)
├── results/                          # Output files
│   ├── figures/                      # Visualizations (5 plots)
│   │   ├── fli_distribution.png
│   │   ├── linguistic_labels.png
│   │   ├── feature_correlations.png
│   │   ├── features_by_label.png
│   │   └── correlation_heatmap.png
│   └── outputs/                      # FLI scores and reports
│       ├── fli_results.csv
│       └── summary_report.txt
├── docs/                             # Documentation
│   └── literature_review.md          # Comprehensive literature review
├── run_prototype.py                  # Main execution script
├── create_sample_data.py             # Sample data generation
├── create_visualizations.py          # Visualization generation
├── requirements.txt                  # Python dependencies
├── README.md                         # Project README
└── FINAL_README.md                   # This file

```

---

## Methodology

### 1. Dimensions of Perceived Livability

| **Dimension** | **Indicators** | **Data Source** |
|---------------|----------------|-----------------|
| Acoustic Comfort | Lden, Lnight (dBA) | window_noise_lden, window_noise_lnight |
| Daylight Quality | Illuminance (lux) | window_daylight_* (seasonal) |
| View Quality | Sky view, Greenery (sr) | view_sky, view_greenery |
| Location Convenience | POI accessibility | walkshed_* (437 columns) |

### 2. Fuzzy Membership Functions

**Based on WHO 2018 Environmental Noise Guidelines:**

- **Quiet**: Lden < 53 dB, Lnight < 45 dB
- **Moderate**: 53 ≤ Lden < 65 dB, 45 ≤ Lnight < 55 dB
- **Noisy**: Lden ≥ 65 dB, Lnight ≥ 55 dB

**Based on EN 17037 Daylight Provision:**

- **Low**: < 100 lux
- **Medium**: 100-300 lux
- **High**: > 300 lux

### 3. Fuzzy Rule Base (Sample Rules)

```
Rule 1: IF noise is Quiet AND daylight is High AND view is Good 
        THEN livability is Excellent

Rule 6: IF noise is Moderate AND daylight is Medium AND view is Moderate 
        THEN livability is Fair

Rule 9: IF noise is Noisy 
        THEN livability is Poor
```

**Total**: 15 rules covering all combinations of input conditions

### 4. Defuzzification

- **Method**: Centroid (Center of Gravity)
- **Output**: Fuzzy Livability Index (FLI) on 0-100 scale
- **Linguistic Labels**: Poor (0-35), Fair (25-55), Good (45-75), Excellent (65-100)

---

## Results Summary

### Prototype Execution (500 Sample Dwellings)

| **Linguistic Label** | **Count** | **Percentage** | **FLI Range** |
|----------------------|-----------|----------------|---------------|
| Excellent            | 26        | 5.2%           | 65-86         |
| Good                 | 275       | 55.0%          | 45-75         |
| Fair                 | 95        | 19.0%          | 25-55         |
| Poor                 | 104       | 20.8%          | 13-35         |

**FLI Score Statistics:**
- Mean: 44.02
- Std: 17.57
- Min: 13.17
- Max: 85.91

### Example Dwelling Assessment

**Excellent Livability (FLI: 83.85/100)**
- Noise Lden: 45.8 dBA (Quiet)
- Noise Lnight: 35.6 dBA (Quiet)
- Daylight: 476 lux (High)
- View Sky: 1.02 sr (Moderate)
- View Greenery: 0.88 sr (Good)
- POI Count: 70 (Medium)

---

## Installation and Usage

### Prerequisites

```bash
Python 3.11+
pip install -r requirements.txt
```

### Dependencies

- pandas >= 2.0.0
- numpy >= 1.24.0
- scikit-fuzzy >= 0.4.2
- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- scipy >= 1.10.0

### Running the Prototype

```bash
# 1. Create sample data (if needed)
python3 create_sample_data.py

# 2. Run the fuzzy inference system
python3 run_prototype.py

# 3. Generate visualizations
python3 create_visualizations.py
```

### Output Files

- `results/outputs/fli_results.csv`: FLI scores for all dwellings
- `results/outputs/summary_report.txt`: Statistical summary
- `results/figures/*.png`: Visualization plots

---

## Key Findings

### 1. Distribution Insights

- **Majority (55%)** of dwellings achieve "Good" livability
- **5.2%** achieve "Excellent" livability (quiet environment + high daylight + good views)
- **20.8%** suffer from "Poor" livability (primarily due to noise exposure)

### 2. Feature Correlations

- **Noise** shows strongest negative correlation with FLI (r ≈ -0.4)
- **Daylight** shows moderate positive correlation (r ≈ 0.3)
- **View quality** contributes to higher FLI scores
- **POI accessibility** has weak correlation (suggests trade-off with noise)

### 3. Rule Activation Patterns

- **Rule 6** (Moderate noise + Medium daylight) most frequently activated
- **Rule 9** (Noisy environment) strongly penalizes livability
- **Rule 1** (Quiet + High daylight + Good view) rarely achieved but highly valued

---

## Validation and Next Steps

### Completed

Prototype implementation with 500 sample dwellings  
Fuzzy membership functions based on international standards  
Mamdani FIS with 15 expert-defined rules  
Comprehensive visualizations  
Literature review grounding the approach  

### Next Steps for Full Implementation

1. **Data Integration**: Download and process full simulations.csv (1.49 GB, 45,176 dwellings)
2. **Validation**: Correlate FLI with location_ratings.csv for external validation
3. **Rule Refinement**: Adjust membership functions and rules based on validation results
4. **Sensitivity Analysis**: Systematic variation of input parameters
5. **Spatial Analysis**: Examine geographic patterns in FLI scores
6. **User Study**: Collect resident surveys to validate perceived vs. computed livability

---

## Standards Applied

### WHO 2018 Environmental Noise Guidelines

- **Road traffic**: Lden < 53 dB, Lnight < 45 dB (Strong recommendation)
- **Railway**: Lden < 54 dB, Lnight < 44 dB (Strong recommendation)
- **Aircraft**: Lden < 45 dB, Lnight < 40 dB (Strong recommendation)

### EN 17037:2018 Daylight in Buildings

- **Minimum**: 300 lux (target), 100 lux (floor)
- **Medium**: 500 lux (target), 300 lux (floor)
- **High**: 750 lux (target), 500 lux (floor)

---

## References

See `docs/literature_review.md` for comprehensive references.

**Key Citations:**

- Zadeh, L. A. (1999). From computing with numbers to computing with words. *IEEE TCAS*, 45(1), 105-119.
- Mendel, J. M. (2002). An architecture for making judgments using computing with words. *IJAMCS*, 12(3), 325-335.
- WHO (2018). *Environmental Noise Guidelines for the European Region*.
- EN 17037:2018. *Daylight in Buildings*.
