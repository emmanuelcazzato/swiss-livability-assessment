"""
Assessment Module for Swiss Livability Assessment

Provides centralized assessment logic and threshold configuration for:
- FLI score to linguistic label conversion
- Feature-specific assessments (noise, daylight, view, POI)

This module serves as a single source of truth for all assessment thresholds,
eliminating duplication across fuzzy_system.py, web_app.py, and scripts.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AssessmentThresholds:
    """
    Configuration class for all assessment thresholds.

    All thresholds are based on scientific standards:
    - Noise: WHO 2018 Environmental Noise Guidelines
    - Daylight: EN 17037 Daylight Provision Standard
    - View/POI: Empirical distribution from Swiss dwellings dataset
    """

    # FLI score thresholds for linguistic labels
    fli_excellent: float = 65.0
    fli_good: float = 45.0
    fli_fair: float = 25.0

    # Noise Lden thresholds (dBA) - based on WHO 2018
    noise_quiet: float = 53.0            # Below WHO Lden threshold (alias for noise_lden_quiet)
    noise_moderate: float = 65.0         # Moderate Lden level (alias for noise_lden_moderate)

    # Noise Lnight thresholds (dBA) - based on WHO 2018
    noise_lnight_quiet: float = 45.0     # Below WHO Lnight threshold
    noise_lnight_moderate: float = 56.0  # Moderate Lnight level

    # Daylight thresholds (klx) - based on EN 17037
    daylight_high: float = 2.0      # High daylight provision
    daylight_medium: float = 0.8    # Medium daylight provision

    # View Sky thresholds (sr) - based on dataset distribution
    view_sky_good: float = 0.035    # Good sky visibility
    view_sky_moderate: float = 0.015  # Moderate sky visibility

    # View Greenery thresholds (sr) - based on dataset distribution
    view_greenery_good: float = 0.012    # Good greenery visibility
    view_greenery_moderate: float = 0.004  # Moderate greenery visibility

    # POI thresholds (log10 scale) - based on dataset distribution
    poi_excellent: float = 2.7      # ~500 POIs
    poi_good: float = 1.9           # ~80 POIs


# Default thresholds instance
DEFAULT_THRESHOLDS = AssessmentThresholds()


# =============================================================================
# FLI Label Functions
# =============================================================================

def get_fli_label(
    fli_score: float,
    thresholds: Optional[AssessmentThresholds] = None
) -> str:
    """
    Convert FLI score to linguistic label.

    Args:
        fli_score: Fuzzy Livability Index score (0-100)
        thresholds: Assessment thresholds. If None, uses defaults.

    Returns:
        Linguistic label: 'excellent', 'good', 'fair', or 'poor'
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if fli_score >= thresholds.fli_excellent:
        return 'excellent'
    elif fli_score >= thresholds.fli_good:
        return 'good'
    elif fli_score >= thresholds.fli_fair:
        return 'fair'
    else:
        return 'poor'


def get_fli_color(label: str) -> str:
    """
    Get display color for FLI linguistic label.

    Args:
        label: Linguistic label

    Returns:
        Hex color code
    """
    colors = {
        'excellent': '#10b981',  # green
        'good': '#3b82f6',       # blue
        'fair': '#f59e0b',       # orange
        'poor': '#ef4444'        # red
    }
    return colors.get(label.lower(), '#6b7280')  # gray fallback


# =============================================================================
# Feature Assessment Functions
# =============================================================================

def get_noise_assessment(
    noise_lden: float,
    thresholds: Optional[AssessmentThresholds] = None
) -> str:
    """
    Get linguistic assessment for day noise level (Lden).

    Args:
        noise_lden: Day-evening-night noise level in dBA
        thresholds: Assessment thresholds. If None, uses defaults.

    Returns:
        Assessment: 'Quiet', 'Moderate', or 'Noisy'
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if noise_lden < thresholds.noise_quiet:
        return 'Quiet'
    elif noise_lden < thresholds.noise_moderate:
        return 'Moderate'
    else:
        return 'Noisy'


def get_noise_lnight_assessment(
    noise_lnight: float,
    thresholds: Optional[AssessmentThresholds] = None
) -> str:
    """
    Get linguistic assessment for night noise level (Lnight).

    Args:
        noise_lnight: Night noise level in dBA
        thresholds: Assessment thresholds. If None, uses defaults.

    Returns:
        Assessment: 'Quiet', 'Moderate', or 'Noisy'
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if noise_lnight < thresholds.noise_lnight_quiet:
        return 'Quiet'
    elif noise_lnight < thresholds.noise_lnight_moderate:
        return 'Moderate'
    else:
        return 'Noisy'


def get_daylight_assessment(
    daylight_klx: float,
    thresholds: Optional[AssessmentThresholds] = None
) -> str:
    """
    Get linguistic assessment for daylight level.

    Args:
        daylight_klx: Daylight illuminance in klx
        thresholds: Assessment thresholds. If None, uses defaults.

    Returns:
        Assessment: 'High', 'Medium', or 'Low'
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if daylight_klx > thresholds.daylight_high:
        return 'High'
    elif daylight_klx > thresholds.daylight_medium:
        return 'Medium'
    else:
        return 'Low'


def get_view_assessment(
    view_sr: float,
    view_type: str,
    thresholds: Optional[AssessmentThresholds] = None
) -> str:
    """
    Get linguistic assessment for view (sky or greenery).

    Args:
        view_sr: View in steradians
        view_type: Either 'sky' or 'greenery'
        thresholds: Assessment thresholds. If None, uses defaults.

    Returns:
        Assessment: 'Good', 'Moderate', or 'Limited'
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    if view_type == 'sky':
        good_threshold = thresholds.view_sky_good
        moderate_threshold = thresholds.view_sky_moderate
    else:  # greenery
        good_threshold = thresholds.view_greenery_good
        moderate_threshold = thresholds.view_greenery_moderate

    if view_sr > good_threshold:
        return 'Good'
    elif view_sr > moderate_threshold:
        return 'Moderate'
    else:
        return 'Limited'


def get_poi_assessment(
    poi_count: int,
    thresholds: Optional[AssessmentThresholds] = None
) -> str:
    """
    Get linguistic assessment for POI accessibility.

    Args:
        poi_count: Number of POIs within walking distance
        thresholds: Assessment thresholds. If None, uses defaults.

    Returns:
        Assessment: 'Excellent', 'Good', or 'Moderate'
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS

    # Convert to log10 scale for comparison
    poi_log = math.log10(max(poi_count, 0) + 1)

    if poi_log >= thresholds.poi_excellent:
        return 'Excellent'
    elif poi_log >= thresholds.poi_good:
        return 'Good'
    else:
        return 'Moderate'


# =============================================================================
# Comprehensive Assessment
# =============================================================================

def get_all_assessments(
    noise_lden: float,
    daylight_klx: float,
    view_sky_sr: float,
    view_greenery_sr: float,
    poi_count: int,
    noise_lnight: Optional[float] = None,
    thresholds: Optional[AssessmentThresholds] = None
) -> Dict[str, str]:
    """
    Get all feature assessments for a dwelling.

    Args:
        noise_lden: Day-evening-night noise level in dBA
        daylight_klx: Daylight illuminance in klx
        view_sky_sr: Sky view in steradians
        view_greenery_sr: Greenery view in steradians
        poi_count: Number of POIs within walking distance
        noise_lnight: Night noise level in dBA (optional)
        thresholds: Assessment thresholds. If None, uses defaults.

    Returns:
        Dictionary of feature assessments
    """
    result = {
        'noise': get_noise_assessment(noise_lden, thresholds),
        'daylight': get_daylight_assessment(daylight_klx, thresholds),
        'view_sky': get_view_assessment(view_sky_sr, 'sky', thresholds),
        'view_greenery': get_view_assessment(view_greenery_sr, 'greenery', thresholds),
        'location': get_poi_assessment(poi_count, thresholds)
    }

    if noise_lnight is not None:
        result['noise_night'] = get_noise_lnight_assessment(noise_lnight, thresholds)

    return result


def get_recommendations(
    fli_score: float,
    assessments: Dict[str, str]
) -> list[str]:
    """
    Generate recommendations based on assessment results.

    Args:
        fli_score: Fuzzy Livability Index score
        assessments: Dictionary of feature assessments

    Returns:
        List of recommendation strings
    """
    recommendations = []

    if assessments.get('noise') == 'Noisy':
        recommendations.append(
            "Consider noise reduction measures (better windows, insulation)"
        )

    if assessments.get('daylight') == 'Low':
        recommendations.append(
            "Improve natural lighting (larger windows, lighter colors)"
        )

    if assessments.get('view_sky') == 'Limited':
        recommendations.append(
            "Limited sky view - consider higher floors or less obstructed locations"
        )

    if assessments.get('view_greenery') == 'Limited':
        recommendations.append(
            "Add indoor plants or consider locations with more greenery"
        )

    if fli_score >= 65:
        recommendations.append(
            "Excellent livability! This dwelling meets high standards."
        )
    elif fli_score < 35:
        recommendations.append(
            "Significant improvements needed for better livability"
        )

    return recommendations
