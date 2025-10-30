# Literature Review: Perceived Livability Assessment Using Computing with Words and Fuzzy Logic

**Authors**: Hao Wang, CAZZATO Emmanuel  
**Date**: October 2025  
**Course**: Urban Computing Seminar

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Computing with Words Framework](#2-computing-with-words-framework)
3. [Fuzzy Logic and Fuzzy Inference Systems](#3-fuzzy-logic-and-fuzzy-inference-systems)
4. [Environmental Quality Assessment](#4-environmental-quality-assessment)
5. [Standards and Guidelines](#5-standards-and-guidelines)
6. [Urban Livability Assessment](#6-urban-livability-assessment)
7. [Research Gap and Contribution](#7-research-gap-and-contribution)
8. [References](#8-references)

---

## 1. Introduction

The assessment of residential livability represents a critical challenge in urban planning and environmental psychology. Traditional approaches rely on quantitative metrics that, while precise, often fail to capture the nuanced, perceptual nature of human experience. This literature review examines the theoretical foundations and practical applications of **Computing with Words (CWW)** and **Fuzzy Inference Systems (FIS)** for assessing perceived livability in residential environments.

The core premise of this research is that livability is fundamentally a **linguistic concept** rather than a purely numerical one. When individuals describe their living environment, they use words like "quiet," "bright," or "pleasant" rather than precise decibel levels or lux measurements. The CWW paradigm, introduced by Zadeh (1996, 1999), provides a formal framework for bridging this gap between quantitative environmental simulations and qualitative human perception.

---

## 2. Computing with Words Framework

### 2.1 Theoretical Foundations

**Computing with Words (CWW)** is a methodology in which words are used in place of numbers for computing and reasoning (Zadeh, 1996). As Zadeh (1999) articulates in his seminal work "From computing with numbers to computing with words," the fundamental premise is that:

> "In dealing with complex systems, especially humanistic systems, the use of words rather than numbers is not only more natural but also more effective."

The CWW paradigm rests on several key principles:

1. **Linguistic Variables**: Variables whose values are words or sentences in natural or artificial language (Zadeh, 1975)
2. **Granular Computing**: Information is represented as granules of varying size and specificity
3. **Fuzzy Constraints**: Constraints are expressed as fuzzy relations rather than crisp boundaries
4. **Perception-Based Reasoning**: Reasoning processes mirror human perceptual judgments

### 2.2 The Perceptual Computer Architecture

Mendel (2002) proposed an architecture for making judgments using CWW, known as the **Perceptual Computer (Per-C)**. The Per-C framework consists of three main components:

1. **Encoder**: Transforms words into type-2 fuzzy sets that capture both intra-personal and inter-personal uncertainties
2. **Fuzzy Inference Engine**: Processes fuzzy sets using IF-THEN rules
3. **Decoder**: Converts fuzzy outputs back into linguistic recommendations

This architecture is particularly relevant for livability assessment because it explicitly accounts for the **uncertainty** inherent in linguistic terms. Different individuals may have slightly different interpretations of what constitutes "quiet" or "bright," and type-2 fuzzy sets can model this variability (Mendel & Wu, 2010).

### 2.3 Applications in Environmental Assessment

The CWW paradigm has been successfully applied to various environmental quality assessment domains:

- **Air Quality**: Dionova et al. (2020) developed a fuzzy logic controller for indoor air quality assessment, combining parameters such as PM2.5, PM10, CO, and NO2 into a comprehensive comfort index
- **Water Quality**: Peche & Rodríguez (2012) demonstrated a rigorous methodology based on fuzzy logic for designing environmental quality indexes
- **Agricultural Sustainability**: dos Reis et al. (2023) proposed a novel indicator-based fuzzy logic model for assessing farming system sustainability

These applications demonstrate the versatility of CWW in transforming multiple quantitative indicators into holistic, interpretable assessments.

---

## 3. Fuzzy Logic and Fuzzy Inference Systems

### 3.1 Fuzzy Set Theory

Fuzzy set theory, introduced by Zadeh (1965), extends classical set theory by allowing partial membership. An element can belong to a set with a degree of membership ranging from 0 to 1, rather than the binary {0, 1} of classical sets.

**Definition**: A fuzzy set A in a universe of discourse X is characterized by a membership function μ_A(x): X → [0,1], where μ_A(x) represents the degree of membership of element x in set A.

This mathematical framework provides the foundation for representing linguistic terms such as "quiet," "moderate," and "noisy" as overlapping fuzzy sets with smooth transitions between categories.

### 3.2 Mamdani Fuzzy Inference System

The **Mamdani FIS**, developed by Ebrahim Mamdani in 1975, is one of the most widely used fuzzy inference methods. It is particularly well-suited for expert system applications where rules are created from human knowledge (Mamdani & Assilian, 1975).

**The Mamdani inference process consists of four steps**:

1. **Fuzzification**: Convert crisp input values into fuzzy membership degrees
2. **Rule Evaluation**: Apply fuzzy IF-THEN rules using minimum (AND) and maximum (OR) operators
3. **Aggregation**: Combine the outputs of all rules
4. **Defuzzification**: Convert the aggregated fuzzy output into a crisp value using methods such as centroid, bisector, or maximum

**Advantages of Mamdani FIS**:
- Intuitive rule structure that mirrors human reasoning
- Transparent decision-making process
- Ability to incorporate expert knowledge
- Robustness to imprecise or incomplete data

**Applications**: Mamdani FIS has been successfully applied to green supply chain management evaluation (Govindan et al., 2018), ecological security assessment (Sun et al., 2018), and urban livability index development (Karasan et al., 2019).

### 3.3 Type-2 Fuzzy Sets

While type-1 fuzzy sets have crisp membership functions, **type-2 fuzzy sets** allow the membership function itself to be fuzzy (Mendel & John, 2002). This additional layer of uncertainty is particularly valuable for modeling the inherent vagueness in linguistic terms.

**Interval Type-2 Fuzzy Sets (IT2FS)** are a simplified form of type-2 fuzzy sets where the secondary membership function is uniformly 1. IT2FS have been shown to effectively model both intra-personal uncertainty (how one person's interpretation varies over time) and inter-personal uncertainty (how different people interpret the same term) (Liu et al., 2025).

For livability assessment, type-2 fuzzy sets could capture the fact that different residents may have different thresholds for what constitutes "acceptable" noise or "sufficient" daylight.

---

## 4. Environmental Quality Assessment

### 4.1 Fuzzy Logic in Environmental Indices

The development of environmental quality indices using fuzzy logic has gained significant traction in recent years. Javid et al. (2016) demonstrated that fuzzy logic-based indices can overcome the limitations of traditional methods by:

1. Handling non-linear relationships between indicators
2. Incorporating expert judgment and local knowledge
3. Providing interpretable results for policymakers
4. Accommodating incomplete or uncertain data

Alieldin et al. (2020) applied fuzzy logic to assess environmental quality in urban development projects, demonstrating the method's capacity to integrate multiple criteria into a coherent assessment framework.

### 4.2 Multi-Criteria Decision Making

Fuzzy inference systems are particularly well-suited for **multi-criteria decision making (MCDM)** in environmental contexts. Kutty et al. (2023) developed a novel fuzzy expert-based MCDM model for assessing smart city performance, integrating sustainability, resilience, and livability dimensions.

The key advantage of fuzzy MCDM is its ability to handle:
- **Conflicting criteria**: Trade-offs between noise reduction and urban density
- **Incommensurable units**: Combining decibels, lux, and POI counts
- **Subjective preferences**: Different stakeholder priorities
- **Linguistic assessments**: Expert opinions expressed in words

---

## 5. Standards and Guidelines

### 5.1 WHO 2018 Environmental Noise Guidelines

The **World Health Organization (WHO)** published comprehensive Environmental Noise Guidelines for the European Region in 2018, providing evidence-based recommendations for protecting human health from exposure to environmental noise.

**Key Recommendations** (Strong evidence):

| **Noise Source** | **Lden (dB)** | **Lnight (dB)** | **Recommendation Strength** |
|------------------|---------------|-----------------|------------------------------|
| Road traffic     | < 53          | < 45            | Strong                       |
| Railway          | < 54          | < 44            | Strong                       |
| Aircraft         | < 45          | < 40            | Strong                       |
| Wind turbine     | < 45          | No recommendation | Conditional                |

**Notes**:
- **Lden**: Day-evening-night average sound level over a 24-hour period, with 5 dB penalty for evening (7pm-11pm) and 10 dB penalty for night (11pm-7am)
- **Lnight**: Average sound level during the night period (11pm-7am)

These guidelines are based on a comprehensive systematic review of 400 health effect studies conducted between 1999-2015. The 2018 guidelines supersede the outdoor noise recommendations from "Guidelines for Community Noise" (1999), although the 1999 guidelines for internal noise remain valid.

**Health Effects Considered**:
- Cardiovascular disease (ischemic heart disease, hypertension)
- Cognitive impairment in children
- Sleep disturbance
- Hearing impairment and tinnitus
- Adverse birth outcomes
- Quality of life and mental health

### 5.2 EN 17037:2018 Daylight in Buildings

The European Standard **EN 17037:2018** provides a comprehensive framework for assessing daylight provision in buildings. Unlike previous standards that focused solely on minimum illuminance levels, EN 17037 adopts a holistic approach considering multiple aspects of daylight quality.

**Daylight Provision Levels**:

| **Target Level** | **Target Illuminance** | **Floor Coverage** | **Minimum Illuminance** | **Floor Coverage** |
|------------------|------------------------|--------------------|--------------------------|--------------------|
| Minimum          | 300 lux                | ≥ 50%              | 100 lux                  | ≥ 95%              |
| Medium           | 500 lux                | ≥ 50%              | 300 lux                  | ≥ 95%              |
| High             | 750 lux                | ≥ 50%              | 500 lux                  | ≥ 95%              |

**Four Key Aspects**:

1. **Daylight Provision**: Minimum illuminance levels for task performance
2. **View Out**: Connection to the external environment (sky, landscape, ground)
3. **Exposure to Sunlight**: Access to direct sunlight for psychological well-being
4. **Glare Protection**: Prevention of visual discomfort and disability

**Measurement Methodology**:
- Illuminance values are calculated for March 21st (equinox) at 10:00 AM
- Overcast sky conditions (CIE Standard Overcast Sky)
- Horizontal plane at 0.85m above floor level (typical work surface height)

The standard recognizes that daylight requirements vary by building use, with residential buildings typically requiring "minimum" to "medium" levels, while schools and offices may require "medium" to "high" levels.

### 5.3 Integration into Fuzzy Membership Functions

These standards provide **objective thresholds** for defining fuzzy membership functions:

**Acoustic Comfort** (based on WHO 2018):
- **Quiet**: Lden < 53 dB, Lnight < 45 dB (full membership = 1.0)
- **Moderate**: 53 ≤ Lden < 65 dB, 45 ≤ Lnight < 55 dB (partial membership)
- **Noisy**: Lden ≥ 65 dB, Lnight ≥ 55 dB (full membership = 1.0)

**Daylight Quality** (based on EN 17037):
- **Low**: < 100 lux (insufficient for most tasks)
- **Medium**: 100-300 lux (minimum acceptable)
- **High**: > 300 lux (optimal for residential use)

By grounding fuzzy membership functions in internationally recognized standards, the assessment framework gains both scientific credibility and practical relevance for policy implementation.

---

## 6. Urban Livability Assessment

### 6.1 Defining Livability

**Livability** is a multidimensional concept encompassing the physical, social, and environmental qualities that make a place suitable for human habitation. Kutty (2022) defines livability as:

> "The sum of factors that add up to a community's quality of life—including the built and natural environments, economic prosperity, social stability and equity, educational opportunity, and cultural, entertainment, and recreation possibilities."

Key dimensions consistently identified in livability research include:

1. **Environmental Quality**: Air quality, noise levels, green spaces
2. **Accessibility**: Proximity to amenities, public transportation
3. **Safety**: Crime rates, traffic safety
4. **Social Infrastructure**: Healthcare, education, cultural facilities
5. **Housing Quality**: Dwelling conditions, affordability
6. **Economic Opportunity**: Employment, income levels

### 6.2 Fuzzy Inference for Livability

Karasan et al. (2019) developed an integrated methodology using neutrosophic CODAS and fuzzy inference systems for assessing the livability index of urban districts. Their approach demonstrates that:

- Fuzzy inference systems allow expert judgments to be incorporated into decision-making processes
- The process is based on more information than traditional crisp methods
- Results are more intuitive and interpretable for stakeholders

Pászto et al. (2015) used a Mamdani Fuzzy Inference System to delimit rural and urban areas based on livability indicators, showing that fuzzy approaches can capture the gradual transition between urban and rural characteristics rather than imposing artificial boundaries.

### 6.3 Perceived vs. Objective Livability

An important distinction exists between **objective livability** (measured through quantitative indicators) and **perceived livability** (residents' subjective assessments). Chen et al. (2021) applied probabilistic hesitation fuzzy linguistic sets to urban livability assessment, recognizing that:

- Residents' perceptions may not perfectly align with objective measurements
- Linguistic assessments capture nuances that numerical scores miss
- Uncertainty and hesitation are inherent in human judgment

The CWW framework is particularly well-suited for bridging this gap, as it transforms objective simulations into linguistic assessments that mirror human perception.

---

## 7. Research Gap and Contribution

### 7.1 Identified Gaps

Despite extensive research on both fuzzy logic applications and livability assessment, several gaps remain:

1. **Limited Integration of International Standards**: Few studies explicitly incorporate WHO and EN standards into fuzzy membership function design
2. **Lack of Validation**: Many fuzzy livability models are not validated against external benchmarks or resident surveys
3. **Simplified Environmental Modeling**: Most studies use aggregated or simplified environmental data rather than detailed building-level simulations
4. **Static Assessment**: Limited consideration of temporal variations (seasonal, diurnal) in environmental quality

### 7.2 Research Contribution

This research addresses these gaps by:

1. **Grounding fuzzy membership functions in WHO 2018 and EN 17037 standards**, ensuring scientific credibility and policy relevance
2. **Utilizing high-resolution building-level simulations** from the Swiss Dwellings v3.0.0 dataset (45,176 dwellings with detailed noise, daylight, and view data)
3. **Implementing a transparent Mamdani FIS** with explicit rule bases that can be validated and refined
4. **Providing a framework for validation** against external ratings and resident surveys
5. **Demonstrating the CWW paradigm** in a real-world urban computing application

### 7.3 Research Questions

**RQ1**: How to deconstruct "perceived livability" into measurable dimensions and map them to available dataset columns?

- **Approach**: Literature review identifies core dimensions (acoustic comfort, daylight quality, view quality, location convenience)
- **Mapping**: Swiss Dwellings dataset provides window_noise_lden, window_noise_lnight, seasonal daylight measurements, view_sky, view_greenery, and POI accessibility

**RQ2**: How to design a Fuzzy Inference System to transform quantitative simulations into linguistic levels?

- **Approach**: Mamdani FIS with membership functions based on WHO 2018 and EN 17037
- **Implementation**: 15 fuzzy rules combining acoustic, visual, and locational factors
- **Output**: Fuzzy Livability Index (FLI) on 0-100 scale with linguistic labels (poor, fair, good, excellent)

**RQ3**: How to validate the "Fuzzy Livability Index" using external benchmarks?

- **Approach**: Correlation analysis with location_ratings.csv from Swiss Dwellings dataset
- **Metrics**: Pearson and Spearman correlation, RMSE, MAE
- **Sensitivity Analysis**: Examine how FLI responds to variations in individual input parameters

---

## 8. References

### Core Theoretical Works

**Zadeh, L. A.** (1965). Fuzzy sets. *Information and Control*, 8(3), 338-353.

**Zadeh, L. A.** (1975). The concept of a linguistic variable and its application to approximate reasoning. *Information Sciences*, 8(3), 199-249.

**Zadeh, L. A.** (1996). Fuzzy logic = computing with words. *IEEE Transactions on Fuzzy Systems*, 4(2), 103-111.

**Zadeh, L. A.** (1999). From computing with numbers to computing with words—from manipulation of measurements to manipulation of perceptions. *IEEE Transactions on Circuits and Systems I: Fundamental Theory and Applications*, 45(1), 105-119.

### Computing with Words

**Mendel, J. M.** (2002). An architecture for making judgments using computing with words. *International Journal of Applied Mathematics and Computer Science*, 12(3), 325-335.

**Mendel, J. M., & Wu, D.** (2010). *Perceptual Computing: Aiding People in Making Subjective Judgments*. IEEE Press/Wiley.

**Mendel, J. M., & John, R. I.** (2002). Type-2 fuzzy sets made simple. *IEEE Transactions on Fuzzy Systems*, 10(2), 117-127.

### Fuzzy Inference Systems

**Mamdani, E. H., & Assilian, S.** (1975). An experiment in linguistic synthesis with a fuzzy logic controller. *International Journal of Man-Machine Studies*, 7(1), 1-13.

**Sun, J., Li, Y. P., Gao, P. P., & Xia, B. C.** (2018). A Mamdani fuzzy inference approach for assessing ecological security in the Pearl River Delta urban agglomeration, China. *Ecological Indicators*, 94, 386-396.

### Environmental Quality Assessment

**Dionova, B. W., Saputro, D. R. S., & Widodo, W.** (2020). Environment indoor air quality assessment using fuzzy inference system. *Journal of Physics: Conference Series*, 1511(1), 012105.

**Peche, R., & Rodríguez, E.** (2012). Development of environmental quality indexes based on fuzzy logic. A case study. *Ecological Indicators*, 23, 555-565.

**Javid, A., Ahmadi, M., Ghasemi, A., & Mahvi, A. H.** (2016). Towards the application of fuzzy logic for developing a novel environmental quality index for human health. *International Journal of Environmental Health Engineering*, 5(1), 10.

**Alieldin, A., Elhakeem, A., & Elmasry, M.** (2020). Adoption of fuzzy logic to assess the environmental quality aspects associating the development plan. *Mansoura Engineering Journal*, 45(2), 1-12.

**dos Reis, J. C., Kamoi, M. Y. T., Latorraca, D., Chen, R. F. F., Michels, R. N., Foschiani, F. H., & Wander, A. E.** (2023). Fuzzy logic indicators for the assessment of farming system sustainability. *Agronomy for Sustainable Development*, 43(3), 1-14.

### Urban Livability

**Karasan, A., Bolturk, E., & Kahraman, C.** (2019). An integrated methodology using neutrosophic CODAS & fuzzy inference system: Assessment of livability index of urban districts. *Journal of Intelligent & Fuzzy Systems*, 37(3), 3565-3583.

**Pászto, V., Marek, L., Tucek, P., & Janoska, Z.** (2015). Using a fuzzy inference system to delimit rural and urban municipalities in the Czech Republic. *Journal of Maps*, 11(2), 231-239.

**Chen, X., Wang, C., & Zhang, C.** (2021). The application of probabilistic hesitation fuzzy linguistic in urban livability. *IOP Conference Series: Earth and Environmental Science*, 668(1), 012086.

**Kutty, A. A., Kucukvar, M., Abdella, G. M., Bulak, M. E., & Onat, N.** (2023). A novel fuzzy expert-based multi-criteria decision support model for linking sustainability, resilience, and livability with smart city development. *Cities*, 135, 104154.

**Kutty, A. A.** (2022). *Linking sustainability, resilience, and livability with smart city development: Building a novel hybrid decision support model for composite performance assessment*. Qatar University.

### Standards and Guidelines

**World Health Organization (WHO).** (2018). *Environmental Noise Guidelines for the European Region*. WHO Regional Office for Europe, Copenhagen.

**European Committee for Standardization (CEN).** (2018). *EN 17037:2018 Daylight in Buildings*. Brussels: CEN.

### Datasets

**Swiss Dwellings v3.0.0.** (2023). Comprehensive dataset of 45,176 Swiss residential buildings with environmental simulations including noise exposure, daylight availability, view quality, and location accessibility. [Dataset]

---

## Appendix: Key Definitions

**Computing with Words (CWW)**: A methodology in which words are used in place of numbers for computing and reasoning, particularly suited for dealing with perceptions and human-centric systems.

**Fuzzy Set**: A set with graded membership, where elements can belong to the set with degrees ranging from 0 (no membership) to 1 (full membership).

**Linguistic Variable**: A variable whose values are words or sentences in natural or artificial language (e.g., "noise level" with values {quiet, moderate, noisy}).

**Membership Function**: A function that defines the degree of membership of an element in a fuzzy set, typically represented as μ_A(x): X → [0,1].

**Mamdani Fuzzy Inference System**: A fuzzy inference method that uses fuzzy IF-THEN rules with linguistic antecedents and consequents, followed by defuzzification to produce crisp outputs.

**Type-2 Fuzzy Set**: A fuzzy set where the membership function itself is fuzzy, allowing modeling of uncertainty about membership degrees.

**Defuzzification**: The process of converting a fuzzy output set into a single crisp value, using methods such as centroid, bisector, or maximum.

**Lden**: Day-evening-night average sound level, a noise indicator that applies penalties to evening and night periods to reflect increased sensitivity.

**Lnight**: Average sound level during the night period (11pm-7am), used to assess sleep disturbance risk.

**Illuminance**: The amount of light falling on a surface, measured in lux (lumens per square meter).

**Solid Angle**: A measure of the field of view from a particular point, measured in steradians (sr), used to quantify view quality.

---

*This literature review provides the theoretical foundation for developing a fuzzy inference system to assess perceived livability of Swiss residential dwellings using the Computing with Words paradigm.*

