"""
Common utilities for scripts in the Swiss Livability Assessment project.

This module provides shared functionality to reduce code duplication across scripts:
- Path setup and sys.path configuration
- Data loading utilities
- Feature column definitions
- Formatting helpers
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple, Optional

import pandas as pd


# =============================================================================
# Path Setup
# =============================================================================

def setup_paths() -> Tuple[Path, Path]:
    """
    Initialize project paths and add src to sys.path.

    Returns:
        Tuple of (ROOT, SRC) paths
    """
    # Determine script location - works whether called from scripts/ or elsewhere
    scripts_dir = Path(__file__).resolve().parent
    root = scripts_dir.parent
    src = root / 'src'

    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

    return root, src


# Initialize paths on import
ROOT, SRC = setup_paths()


# =============================================================================
# Feature Columns (Single Source of Truth)
# =============================================================================

# V2 aligned feature columns used by FIS
FEATURE_COLUMNS = [
    'noise_lden',
    'noise_lnight',
    'daylight',
    'view_sky',
    'view_greenery',
    'location_poi'
]

# Raw feature columns (original units for display)
RAW_FEATURE_COLUMNS = [
    'raw_noise_day_dba',
    'raw_noise_night_dba',
    'raw_daylight_klx',
    'raw_view_sky_sr',
    'raw_view_greenery_sr',
    'raw_poi_count'
]

# Feature display names for visualization
FEATURE_DISPLAY_NAMES = {
    'noise_lden': 'Noise Lden (dBA)',
    'noise_lnight': 'Noise Lnight (dBA)',
    'daylight': 'Daylight (klx)',
    'view_sky': 'View Sky (sr)',
    'view_greenery': 'View Greenery (sr)',
    'location_poi': 'Location POI (log10)',
    'raw_daylight_klx': 'Daylight (klx)',
    'raw_view_sky_sr': 'View Sky (sr)',
    'raw_view_greenery_sr': 'View Greenery (sr)',
    'raw_poi_count': 'POI Count'
}


# =============================================================================
# Data Loading
# =============================================================================

def load_dwellings_data(root: Optional[Path] = None) -> pd.DataFrame:
    """
    Load the processed dwellings dataset.

    Args:
        root: Project root directory. If None, uses module-level ROOT.

    Returns:
        DataFrame with dwelling features

    Raises:
        FileNotFoundError: If data file doesn't exist
    """
    if root is None:
        root = ROOT

    data_path = root / 'data' / 'processed' / 'dwellings_full.csv'

    if not data_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {data_path}\n"
            "Please run: python scripts/prepare_full_features.py"
        )

    return pd.read_csv(data_path)


def load_fli_results(root: Optional[Path] = None) -> pd.DataFrame:
    """
    Load the FLI results dataset.

    Args:
        root: Project root directory. If None, uses module-level ROOT.

    Returns:
        DataFrame with FLI scores

    Raises:
        FileNotFoundError: If results file doesn't exist
    """
    if root is None:
        root = ROOT

    results_path = root / 'results' / 'outputs' / 'fli_results.csv'

    if not results_path.exists():
        raise FileNotFoundError(
            f"Results file not found: {results_path}\n"
            "Please run: python scripts/run_prototype.py"
        )

    return pd.read_csv(results_path)


# =============================================================================
# Formatting Helpers
# =============================================================================

def print_section_header(title: str, width: int = 80, char: str = '=') -> None:
    """
    Print a formatted section header.

    Args:
        title: Section title text
        width: Total width of the header line
        char: Character to use for the border
    """
    print(f"\n{char * width}")
    print(title)
    print(char * width)


def print_subsection_header(title: str, width: int = 80, char: str = '-') -> None:
    """
    Print a formatted subsection header.

    Args:
        title: Subsection title text
        width: Total width of the header line
        char: Character to use for the border
    """
    print(f"\n{char * width}")
    print(title)
    print(char * width)


def print_label_distribution(labels: pd.Series, total: Optional[int] = None) -> None:
    """
    Print linguistic label distribution with counts and percentages.

    Args:
        labels: Series of linguistic labels
        total: Total count for percentage calculation. If None, uses len(labels).
    """
    if total is None:
        total = len(labels)

    label_counts = labels.value_counts()

    for label in ['excellent', 'good', 'fair', 'poor']:
        if label in label_counts.index:
            count = label_counts[label]
            pct = 100.0 * count / total if total > 0 else 0
            print(f"  {label.capitalize():10s}: {count:5d} ({pct:5.1f}%)")
