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

    /* Additional Academic & Scientific UI Components */
    .academic-hero {{
        background: linear-gradient(135deg, {SURFACE_CARD} 0%, {SURFACE_INSET} 100%);
        border: 1px solid {BORDER_STRONG};
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }}
    .academic-hero-title {{
        color: {TEXT_PRIMARY};
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 6px;
    }}
    .academic-hero-subtitle {{
        color: {TEXT_SECONDARY};
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 12px;
    }}
    .academic-hero-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
    }}

    /* Badges & Pills */
    .badge-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    .badge-kmeans {{
        background: rgba(56, 189, 248, 0.12);
        color: {COLOR_KMEANS};
        border: 1px solid rgba(56, 189, 248, 0.35);
    }}
    .badge-mst {{
        background: rgba(249, 115, 22, 0.12);
        color: {COLOR_MST};
        border: 1px solid rgba(249, 115, 22, 0.35);
    }}
    .badge-neutral {{
        background: rgba(148, 163, 184, 0.12);
        color: {TEXT_SECONDARY};
        border: 1px solid rgba(148, 163, 184, 0.25);
    }}
    .badge-success {{
        background: rgba(16, 185, 129, 0.12);
        color: {STATUS_SUCCESS};
        border: 1px solid rgba(16, 185, 129, 0.35);
    }}
    .badge-warning {{
        background: rgba(245, 158, 11, 0.12);
        color: {STATUS_WARNING};
        border: 1px solid rgba(245, 158, 11, 0.35);
    }}

    /* Quick-Start Workflow Cards */
    .workflow-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
        margin-bottom: 20px;
    }}
    .workflow-card {{
        background-color: {SURFACE_CARD};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 8px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }}
    .workflow-card:hover {{
        border-color: {BORDER_STRONG};
        background-color: {SURFACE_HOVER};
    }}
    .workflow-card-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }}
    .workflow-card-num {{
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: rgba(56, 189, 248, 0.15);
        color: {COLOR_KMEANS};
        border: 1px solid rgba(56, 189, 248, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
    }}
    .workflow-card-title {{
        color: {TEXT_PRIMARY};
        font-weight: 600;
        font-size: 0.9rem;
    }}
    .workflow-card-desc {{
        color: {TEXT_SECONDARY};
        font-size: 0.8rem;
        line-height: 1.4;
    }}

    /* Comparison Cards */
    .comparison-container {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
    }}
    .comparison-card {{
        background-color: {SURFACE_CARD};
        border-radius: 8px;
        padding: 16px 20px;
        border: 1px solid {BORDER_SUBTLE};
    }}
    .comparison-card-kmeans {{
        border-top: 3px solid {COLOR_KMEANS};
    }}
    .comparison-card-mst {{
        border-top: 3px solid {COLOR_MST};
    }}
    .comparison-card-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid {BORDER_SUBTLE};
    }}
    .comparison-card-title {{
        color: {TEXT_PRIMARY};
        font-size: 1.05rem;
        font-weight: 700;
    }}

    /* Accessibility Focus & Overflow Protection */
    *:focus-visible {{
        outline: 2px solid {BORDER_FOCUS} !important;
        outline-offset: 2px !important;
    }}
    .stPlotlyChart {{
        max-width: 100% !important;
        overflow-x: auto !important;
    }}
    .stDataFrame {{
        max-width: 100% !important;
        overflow-x: auto !important;
    }}
    </style>
    """


def apply_custom_theme() -> None:
    """Inject centralized, scoped CSS tokens and styles into current Streamlit view."""
    st.markdown(get_theme_css(), unsafe_allow_html=True)


def render_metric_card_html(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = STATUS_SUCCESS,
) -> str:
    """Return safe HTML for a standardized academic metric card."""
    import html
    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    delta_html = ""
    if delta:
        safe_delta = html.escape(str(delta))
        safe_color = html.escape(str(delta_color))
        delta_html = f'<div class="academic-metric-delta" style="color: {safe_color};">{safe_delta}</div>'

    return f"""
    <div class="academic-metric-card">
        <div class="academic-metric-title">{safe_title}</div>
        <div class="academic-metric-value">{safe_value}</div>
        {delta_html}
    </div>
    """


def render_hero_html(
    title: str,
    subtitle: str,
    badges: Optional[List[tuple[str, str]]] = None,
) -> str:
    """Return safe HTML for an academic section hero banner.

    Args:
        title: Section title text.
        subtitle: Descriptive explanation.
        badges: List of (badge_text, badge_style) tuples.
                badge_style can be 'kmeans', 'mst', 'neutral', 'success', 'warning'.
    """
    import html
    safe_title = html.escape(str(title))
    safe_subtitle = html.escape(str(subtitle))
    badges_html = ""
    if badges:
        items = []
        for text, style in badges:
            safe_text = html.escape(str(text))
            safe_style = html.escape(str(style))
            items.append(f'<span class="badge-pill badge-{safe_style}">{safe_text}</span>')
        badges_html = f'<div class="academic-hero-badges">{" ".join(items)}</div>'

    return f"""
    <div class="academic-hero">
        <div class="academic-hero-title">{safe_title}</div>
        <div class="academic-hero-subtitle">{safe_subtitle}</div>
        {badges_html}
    </div>
    """
