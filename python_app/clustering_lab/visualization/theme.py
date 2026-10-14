"""
clustering_lab.visualization.theme
==================================
Canonical design tokens, color palettes, and visual styling for scientific visualizations
and Streamlit dashboard interface components.

Strictly adheres to the approved Slate & Cyan high-contrast scientific specification:
- Dark canvas (#0b0f19) and elevated card surfaces (#151d30, #1e293b).
- Coherent typography colors with high contrast for accessibility (#f8fafc, #94a3b8).
- Distinct algorithm accents: Cyan (#38bdf8) for K-Means and Warm Orange (#f97316) for Prim MST.
- Semantic status indicators: Emerald (#10b981), Amber (#f59e0b), Coral Red (#ef4444).
- Dark-mode synchronized Matplotlib export styles eliminating theme divergence.
"""

from __future__ import annotations

from typing import Dict, List, Optional
import streamlit as st

# =============================================================================
# 1. Global Color Tokens
# =============================================================================

# Canvas and Elevated Surfaces
CANVAS_BG = "#0b0f19"        # Ultra-dark slate canvas
SURFACE_CARD = "#151d30"     # Elevated card background
SURFACE_HOVER = "#1e293b"    # Interactive hover card
SURFACE_INSET = "#0f172a"    # Inset container background

# Borders and Dividers
BORDER_SUBTLE = "#1e293b"    # Subtle card border
BORDER_STRONG = "#334155"    # Interactive control border
BORDER_FOCUS = "#38bdf8"     # Cyan active focus border

# Typography Colors
TEXT_PRIMARY = "#f8fafc"     # Crisp white header text
TEXT_SECONDARY = "#94a3b8"   # Muted secondary label text
TEXT_MUTED = "#64748b"       # De-emphasized caption text
TEXT_ACCENT = "#38bdf8"      # Cyan highlighted text

# Semantic Status Accents
STATUS_SUCCESS = "#10b981"   # Emerald green (Verified / Optimal)
STATUS_WARNING = "#f59e0b"   # Amber orange (Stale / Caution)
STATUS_ERROR = "#ef4444"     # Coral red (Degraded / Boundary failure)
STATUS_INFO = "#0284c7"      # Sky blue (Informational / Parameter note)

# Scientific Algorithm and Entity Colors
COLOR_KMEANS = "#38bdf8"     # Cyan: Centroid-based Lloyd's K-Means
COLOR_MST = "#f97316"        # Warm Orange: Graph-theoretic Prim's MST
COLOR_INLIER = "#10b981"     # Emerald: True manifold inlier
COLOR_OUTLIER = "#ef4444"    # Crimson Red: Uniform contamination (Label -1)
COLOR_CENTROID = "#fbbf24"   # Golden Amber: Cluster centroid star marker
COLOR_RETAINED_EDGE = "rgba(148, 163, 184, 0.45)"  # Slate-400 translucent tree edge
COLOR_RETAINED_EDGE_SOLID = "#64748b"               # Solid slate for Matplotlib
COLOR_CUT_EDGE = "#ef4444"   # Crimson: Longest edge cut in 2-component partition
COLOR_ACTIVE_EDGE = "#f97316"  # Orange: Active candidate edge in Explorer trace

# Accessible Categorical Cluster Palette (k <= 10)
CLUSTER_COLORS: List[str] = [
    "#38bdf8",  # Cluster 0: Vivid Cyan
    "#f97316",  # Cluster 1: Warm Orange
    "#a855f7",  # Cluster 2: Electric Purple
    "#10b981",  # Cluster 3: Emerald Green
    "#ec4899",  # Cluster 4: Hot Pink
    "#eab308",  # Cluster 5: Sunburst Amber
    "#06b6d4",  # Cluster 6: Cyan Teal
    "#6366f1",  # Cluster 7: Indigo
    "#14b8a6",  # Cluster 8: Teal
    "#f43f5e",  # Cluster 9: Rose Red
]

# Typography Stacks
FONT_FAMILY_SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_FAMILY_MONO = "'JetBrains Mono', 'Fira Code', 'Consolas', monospace"


# =============================================================================
# 2. Scoped CSS Generation & Theme Injection
# =============================================================================

def get_theme_css() -> str:
    """Generate scoped CSS variables and reusable component classes."""
    return f"""
    <style>
    /* Scientific Dark Mode Tokens */
    :root {{
        --color-canvas-bg: {CANVAS_BG};
        --color-surface-card: {SURFACE_CARD};
        --color-surface-hover: {SURFACE_HOVER};
        --color-surface-inset: {SURFACE_INSET};
        --color-border-subtle: {BORDER_SUBTLE};
        --color-border-strong: {BORDER_STRONG};
        --color-border-focus: {BORDER_FOCUS};
        --color-text-primary: {TEXT_PRIMARY};
        --color-text-secondary: {TEXT_SECONDARY};
        --color-text-muted: {TEXT_MUTED};
        --color-text-accent: {TEXT_ACCENT};
        --color-status-success: {STATUS_SUCCESS};
        --color-status-warning: {STATUS_WARNING};
        --color-status-error: {STATUS_ERROR};
        --color-status-info: {STATUS_INFO};
        --color-entity-kmeans: {COLOR_KMEANS};
        --color-entity-mst: {COLOR_MST};
    }}

    /* Stale-State Warning Banner */
    .stale-warning-banner {{
        background-color: #451a03;
        border: 1px solid {STATUS_WARNING};
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .stale-warning-title {{
        color: #fcd34d;
        font-weight: 600;
        font-size: 0.95rem;
    }}
    .stale-warning-body {{
        color: #fef3c7;
        font-size: 0.875rem;
    }}

    /* Scientific Metric Card */
    .academic-metric-card {{
        background-color: {SURFACE_CARD};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }}
    .academic-metric-title {{
        color: {TEXT_SECONDARY};
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }}
    .academic-metric-value {{
        color: {TEXT_PRIMARY};
        font-size: 1.5rem;
        font-weight: 700;
        font-family: {FONT_FAMILY_MONO};
    }}
    .academic-metric-delta {{
        font-size: 0.8rem;
        margin-top: 4px;
    }}

    /* Compact Academic Identity Header */
    .academic-identity-badge {{
        background: linear-gradient(135deg, {SURFACE_CARD} 0%, {SURFACE_INSET} 100%);
        border: 1px solid {BORDER_STRONG};
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }}
    .academic-identity-title {{
        color: {TEXT_PRIMARY};
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: -0.01em;
    }}
    .academic-identity-subtitle {{
        color: {TEXT_SECONDARY};
        font-size: 0.8rem;
        margin-top: 2px;
    }}
    .academic-identity-authors {{
        color: {TEXT_ACCENT};
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 6px;
    }}
    </style>
    """


def apply_custom_theme() -> None:
    """Inject centralized, scoped CSS tokens and styles into current Streamlit view."""
    st.markdown(get_theme_css(), unsafe_allow_html=True)
