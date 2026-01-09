"""
Premium Design System for Lecture Mind UI.

IMPLEMENTS: S013 - Gradio Web Interface (Premium Styling)
VERSION: 2.0 - Complete UI/UX Overhaul

Design Principles:
- Clean, modern, premium SaaS aesthetic
- Glassmorphism with subtle depth
- 8px spacing grid
- Micro-animations for polish
- Full accessibility support
"""

from __future__ import annotations

# =============================================================================
# DESIGN TOKENS - 8px Grid System
# =============================================================================

SPACING = {
    "0": "0",
    "1": "4px",  # 0.5 unit
    "2": "8px",  # 1 unit
    "3": "12px",  # 1.5 units
    "4": "16px",  # 2 units
    "5": "20px",  # 2.5 units
    "6": "24px",  # 3 units
    "8": "32px",  # 4 units
    "10": "40px",  # 5 units
    "12": "48px",  # 6 units
    "16": "64px",  # 8 units
}

# =============================================================================
# COLOR SYSTEM - Light Theme
# =============================================================================

LIGHT_THEME = {
    # Brand gradient
    "gradient_start": "#6366f1",  # Indigo 500
    "gradient_end": "#8b5cf6",  # Violet 500
    "gradient_accent": "#ec4899",  # Pink 500
    # Primary palette
    "primary_50": "#eef2ff",
    "primary_100": "#e0e7ff",
    "primary_500": "#6366f1",
    "primary_600": "#4f46e5",
    "primary_700": "#4338ca",
    # Neutral palette
    "gray_50": "#f9fafb",
    "gray_100": "#f3f4f6",
    "gray_200": "#e5e7eb",
    "gray_300": "#d1d5db",
    "gray_400": "#9ca3af",
    "gray_500": "#6b7280",
    "gray_600": "#4b5563",
    "gray_700": "#374151",
    "gray_800": "#1f2937",
    "gray_900": "#111827",
    # Semantic colors
    "success": "#10b981",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    # Surface colors
    "background": "#f8fafc",
    "surface": "#ffffff",
    "surface_elevated": "#ffffff",
    # Text colors
    "text_primary": "#111827",
    "text_secondary": "#6b7280",
    "text_muted": "#9ca3af",
    "text_inverse": "#ffffff",
}

DARK_THEME = {
    # Brand gradient (adjusted for dark)
    "gradient_start": "#818cf8",
    "gradient_end": "#a78bfa",
    "gradient_accent": "#f472b6",
    # Primary palette (lighter for dark bg)
    "primary_50": "#1e1b4b",
    "primary_100": "#312e81",
    "primary_500": "#818cf8",
    "primary_600": "#a5b4fc",
    "primary_700": "#c7d2fe",
    # Neutral palette (inverted)
    "gray_50": "#111827",
    "gray_100": "#1f2937",
    "gray_200": "#374151",
    "gray_300": "#4b5563",
    "gray_400": "#6b7280",
    "gray_500": "#9ca3af",
    "gray_600": "#d1d5db",
    "gray_700": "#e5e7eb",
    "gray_800": "#f3f4f6",
    "gray_900": "#f9fafb",
    # Semantic colors (brighter for dark)
    "success": "#34d399",
    "warning": "#fbbf24",
    "error": "#f87171",
    "info": "#60a5fa",
    # Surface colors
    "background": "#0f172a",
    "surface": "#1e293b",
    "surface_elevated": "#334155",
    # Text colors
    "text_primary": "#f9fafb",
    "text_secondary": "#9ca3af",
    "text_muted": "#6b7280",
    "text_inverse": "#111827",
}

# =============================================================================
# TYPOGRAPHY SCALE
# =============================================================================

TYPOGRAPHY = {
    "font_sans": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "font_mono": "'JetBrains Mono', 'Fira Code', Consolas, monospace",
    # Scale (1.25 ratio)
    "text_xs": "0.75rem",  # 12px
    "text_sm": "0.875rem",  # 14px
    "text_base": "1rem",  # 16px
    "text_lg": "1.125rem",  # 18px
    "text_xl": "1.25rem",  # 20px
    "text_2xl": "1.5rem",  # 24px
    "text_3xl": "1.875rem",  # 30px
    "text_4xl": "2.25rem",  # 36px
    # Weights
    "font_normal": "400",
    "font_medium": "500",
    "font_semibold": "600",
    "font_bold": "700",
    # Line heights
    "leading_tight": "1.25",
    "leading_normal": "1.5",
    "leading_relaxed": "1.75",
}

# =============================================================================
# EFFECTS
# =============================================================================

BORDERS = {
    "radius_sm": "6px",
    "radius_md": "8px",
    "radius_lg": "12px",
    "radius_xl": "16px",
    "radius_2xl": "24px",
    "radius_full": "9999px",
}

SHADOWS = {
    "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
    "md": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
    "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)",
    "xl": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
    "2xl": "0 25px 50px -12px rgb(0 0 0 / 0.25)",
    "glow": "0 0 40px -10px rgb(99 102 241 / 0.5)",
}

# =============================================================================
# CUSTOM CSS - Premium Design System
# =============================================================================

CUSTOM_CSS = """
/* ==========================================================================
   LECTURE MIND - Premium Design System v2.0
   Author: Senior UI/UX Engineer
   ========================================================================== */

/* --------------------------------------------------------------------------
   CSS Custom Properties (Design Tokens)
   -------------------------------------------------------------------------- */
:root {
    /* Brand */
    --lm-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
    --lm-gradient-subtle: linear-gradient(135deg, #eef2ff 0%, #faf5ff 50%, #fdf2f8 100%);

    /* Primary */
    --lm-primary: #6366f1;
    --lm-primary-hover: #4f46e5;
    --lm-primary-light: #eef2ff;

    /* Neutrals */
    --lm-bg: #f8fafc;
    --lm-surface: #ffffff;
    --lm-surface-elevated: #ffffff;
    --lm-border: #e5e7eb;
    --lm-border-focus: #6366f1;

    /* Text */
    --lm-text: #111827;
    --lm-text-secondary: #6b7280;
    --lm-text-muted: #9ca3af;

    /* Semantic */
    --lm-success: #10b981;
    --lm-warning: #f59e0b;
    --lm-error: #ef4444;

    /* Effects */
    --lm-shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --lm-shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --lm-shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --lm-shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
    --lm-shadow-glow: 0 0 40px -10px rgb(99 102 241 / 0.4);

    /* Timing */
    --lm-ease: cubic-bezier(0.4, 0, 0.2, 1);
    --lm-ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --lm-duration-fast: 150ms;
    --lm-duration-normal: 200ms;
    --lm-duration-slow: 300ms;

    /* Radius */
    --lm-radius-sm: 6px;
    --lm-radius-md: 8px;
    --lm-radius-lg: 12px;
    --lm-radius-xl: 16px;
    --lm-radius-2xl: 24px;
}

/* Dark theme */
.dark, [data-theme="dark"] {
    --lm-gradient: linear-gradient(135deg, #818cf8 0%, #a78bfa 50%, #f472b6 100%);
    --lm-gradient-subtle: linear-gradient(135deg, #1e1b4b 0%, #2e1065 50%, #4a044e 100%);

    --lm-primary: #818cf8;
    --lm-primary-hover: #a5b4fc;
    --lm-primary-light: #312e81;

    --lm-bg: #0f172a;
    --lm-surface: #1e293b;
    --lm-surface-elevated: #334155;
    --lm-border: #334155;
    --lm-border-focus: #818cf8;

    --lm-text: #f9fafb;
    --lm-text-secondary: #9ca3af;
    --lm-text-muted: #6b7280;

    --lm-success: #34d399;
    --lm-warning: #fbbf24;
    --lm-error: #f87171;
}

/* --------------------------------------------------------------------------
   Base & Reset
   -------------------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

/* --------------------------------------------------------------------------
   Main Container - Gradient Background
   -------------------------------------------------------------------------- */
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--lm-gradient) !important;
    min-height: 100vh !important;
    padding: 24px !important;
}

/* Main content card - Glassmorphism */
.gradio-container > .main,
.gradio-container > div > .main {
    background: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border-radius: var(--lm-radius-2xl) !important;
    box-shadow: var(--lm-shadow-2xl), 0 0 0 1px rgba(255,255,255,0.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    padding: 32px !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
    animation: slideUp 0.5s var(--lm-ease) !important;
}

.dark .gradio-container > .main,
.dark .gradio-container > div > .main {
    background: rgba(30, 41, 59, 0.92) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* --------------------------------------------------------------------------
   Typography
   -------------------------------------------------------------------------- */
h1, .gr-markdown h1 {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    color: var(--lm-text) !important;
    letter-spacing: -0.025em !important;
    line-height: 1.2 !important;
    margin-bottom: 8px !important;
}

/* Special title styling for app header */
.app-title h1,
h1:first-of-type {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

h2, .gr-markdown h2 {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: var(--lm-text) !important;
    letter-spacing: -0.02em !important;
}

p, .gr-markdown p {
    color: var(--lm-text-secondary) !important;
    line-height: 1.6 !important;
}

/* Subtitle/description text with better contrast */
.app-subtitle p,
.gradio-container .main p:first-of-type {
    color: var(--lm-text) !important;
    opacity: 0.85 !important;
    font-size: 1.1rem !important;
}

/* --------------------------------------------------------------------------
   Buttons - Premium with Animations
   -------------------------------------------------------------------------- */
button, .gr-button {
    font-family: inherit !important;
    font-weight: 500 !important;
    border-radius: var(--lm-radius-lg) !important;
    transition: all var(--lm-duration-normal) var(--lm-ease) !important;
    cursor: pointer !important;
}

/* Primary button - gradient with glow */
button.primary,
.gr-button-primary,
button[variant="primary"],
.btn-primary {
    background: var(--lm-gradient) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    font-size: 1rem !important;
    box-shadow: var(--lm-shadow-md), 0 0 20px -5px rgba(99, 102, 241, 0.4) !important;
    position: relative !important;
    overflow: hidden !important;
}

button.primary::before,
.gr-button-primary::before,
button[variant="primary"]::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
    transition: left 0.5s ease !important;
}

button.primary:hover::before,
.gr-button-primary:hover::before {
    left: 100% !important;
}

button.primary:hover,
.gr-button-primary:hover,
button[variant="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--lm-shadow-lg), 0 0 30px -5px rgba(99, 102, 241, 0.5) !important;
}

button.primary:active,
.gr-button-primary:active {
    transform: translateY(0) scale(0.98) !important;
}

/* Secondary button - outline style (explicit class only) */
button.secondary,
.gr-button-secondary,
button[variant="secondary"],
.btn-secondary {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 2px solid var(--lm-border) !important;
    color: var(--lm-text-secondary) !important;
    padding: 10px 24px !important;
    box-shadow: var(--lm-shadow-sm) !important;
}

button.secondary:hover,
.gr-button-secondary:hover,
button[variant="secondary"]:hover,
.btn-secondary:hover {
    border-color: var(--lm-primary) !important;
    color: var(--lm-primary) !important;
    background: var(--lm-primary-light) !important;
    transform: translateY(-1px) !important;
}

/* --------------------------------------------------------------------------
   Input Fields - Clean with Focus States
   -------------------------------------------------------------------------- */
input[type="text"],
input[type="number"],
textarea,
.gr-textbox input,
.gr-input {
    background: var(--lm-surface) !important;
    border: 2px solid var(--lm-border) !important;
    border-radius: var(--lm-radius-lg) !important;
    padding: 12px 16px !important;
    font-size: 1rem !important;
    color: var(--lm-text) !important;
    transition: all var(--lm-duration-fast) var(--lm-ease) !important;
}

input[type="text"]:focus,
input[type="number"]:focus,
textarea:focus,
.gr-textbox input:focus {
    outline: none !important;
    border-color: var(--lm-primary) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
}

input::placeholder,
textarea::placeholder {
    color: var(--lm-text-muted) !important;
}

/* --------------------------------------------------------------------------
   Tabs - Pill Style with Animation
   -------------------------------------------------------------------------- */
.gr-tab-nav,
.tabs > div:first-child {
    background: var(--lm-bg) !important;
    padding: 6px !important;
    border-radius: var(--lm-radius-xl) !important;
    display: inline-flex !important;
    gap: 4px !important;
}

button[role="tab"],
.gr-tab-button {
    background: transparent !important;
    border: none !important;
    padding: 10px 20px !important;
    border-radius: var(--lm-radius-lg) !important;
    font-weight: 500 !important;
    color: var(--lm-text-secondary) !important;
    position: relative !important;
}

button[role="tab"]:hover,
.gr-tab-button:hover {
    color: var(--lm-text) !important;
    background: rgba(99, 102, 241, 0.05) !important;
}

button[role="tab"][aria-selected="true"],
.gr-tab-button.selected {
    background: var(--lm-gradient) !important;
    color: white !important;
    box-shadow: var(--lm-shadow-md) !important;
}

/* --------------------------------------------------------------------------
   File Upload - Premium Drop Zone
   -------------------------------------------------------------------------- */
.gr-file-upload,
[data-testid="upload"],
.upload-zone {
    border: 2px dashed var(--lm-border) !important;
    border-radius: var(--lm-radius-xl) !important;
    background: var(--lm-gradient-subtle) !important;
    padding: 48px 32px !important;
    text-align: center !important;
    transition: all var(--lm-duration-normal) var(--lm-ease) !important;
    cursor: pointer !important;
}

.gr-file-upload:hover,
[data-testid="upload"]:hover {
    border-color: var(--lm-primary) !important;
    background: linear-gradient(135deg, #eef2ff 0%, #f5f3ff 50%, #fdf2f8 100%) !important;
    transform: scale(1.01) !important;
    box-shadow: var(--lm-shadow-lg) !important;
}

/* Drag active state */
.gr-file-upload.drag-active {
    border-color: var(--lm-primary) !important;
    background: var(--lm-primary-light) !important;
    transform: scale(1.02) !important;
}

/* --------------------------------------------------------------------------
   Cards & Panels
   -------------------------------------------------------------------------- */
.gr-panel,
.gr-box,
.gr-form,
.gr-group {
    background: var(--lm-surface) !important;
    border: 1px solid var(--lm-border) !important;
    border-radius: var(--lm-radius-xl) !important;
    padding: 24px !important;
    box-shadow: var(--lm-shadow-sm) !important;
}

/* --------------------------------------------------------------------------
   Slider - Custom Track and Thumb
   -------------------------------------------------------------------------- */
input[type="range"] {
    -webkit-appearance: none !important;
    appearance: none !important;
    height: 6px !important;
    background: var(--lm-gradient) !important;
    border-radius: var(--lm-radius-full) !important;
    cursor: pointer !important;
}

input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none !important;
    width: 20px !important;
    height: 20px !important;
    background: white !important;
    border-radius: 50% !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15), 0 0 0 3px var(--lm-primary) !important;
    cursor: pointer !important;
    transition: all var(--lm-duration-fast) var(--lm-ease) !important;
}

input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.15) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2), 0 0 0 4px var(--lm-primary) !important;
}

/* --------------------------------------------------------------------------
   Radio & Checkbox - Custom Style
   -------------------------------------------------------------------------- */
input[type="radio"],
input[type="checkbox"] {
    -webkit-appearance: none !important;
    appearance: none !important;
    width: 20px !important;
    height: 20px !important;
    border: 2px solid var(--lm-border) !important;
    border-radius: var(--lm-radius-sm) !important;
    cursor: pointer !important;
    transition: all var(--lm-duration-fast) var(--lm-ease) !important;
    position: relative !important;
}

input[type="radio"] {
    border-radius: 50% !important;
}

input[type="radio"]:checked,
input[type="checkbox"]:checked {
    background: var(--lm-gradient) !important;
    border-color: var(--lm-primary) !important;
}

input[type="checkbox"]:checked::after {
    content: '✓' !important;
    position: absolute !important;
    color: white !important;
    font-size: 14px !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
}

/* --------------------------------------------------------------------------
   Progress Bar - Animated Gradient
   -------------------------------------------------------------------------- */
.gr-progress-bar,
.progress-bar {
    background: var(--lm-border) !important;
    border-radius: var(--lm-radius-full) !important;
    height: 8px !important;
    overflow: hidden !important;
}

.gr-progress-bar > div,
.progress-bar > div {
    background: var(--lm-gradient) !important;
    background-size: 200% 100% !important;
    animation: shimmer 2s ease infinite !important;
    border-radius: var(--lm-radius-full) !important;
    height: 100% !important;
}

/* --------------------------------------------------------------------------
   Timeline Component
   -------------------------------------------------------------------------- */
.timeline-container {
    padding: 20px !important;
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-xl) !important;
    border: 1px solid var(--lm-border) !important;
}

.timeline-track {
    position: relative !important;
    height: 48px !important;
    background: linear-gradient(to right, var(--lm-border), var(--lm-border)) !important;
    background-size: 100% 4px !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
    border-radius: var(--lm-radius-sm) !important;
}

.timeline-event {
    position: absolute !important;
    width: 20px !important;
    height: 20px !important;
    border-radius: 50% !important;
    top: 50% !important;
    transform: translate(-50%, -50%) !important;
    cursor: pointer !important;
    transition: all var(--lm-duration-fast) var(--lm-ease-bounce) !important;
    box-shadow: var(--lm-shadow-md) !important;
    z-index: 10 !important;
}

/* Larger invisible click/touch target */
.timeline-event::before {
    content: '' !important;
    position: absolute !important;
    top: -10px !important;
    left: -10px !important;
    right: -10px !important;
    bottom: -10px !important;
    border-radius: 50% !important;
}

.timeline-event:hover {
    transform: translate(-50%, -50%) scale(1.3) !important;
    box-shadow: var(--lm-shadow-lg), var(--lm-shadow-glow) !important;
}

/* Tooltip on hover */
.timeline-event::after {
    content: attr(title) !important;
    position: absolute !important;
    bottom: 130% !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background: var(--lm-surface) !important;
    color: var(--lm-text) !important;
    padding: 6px 12px !important;
    border-radius: var(--lm-radius-md) !important;
    font-size: 0.75rem !important;
    white-space: nowrap !important;
    box-shadow: var(--lm-shadow-lg) !important;
    opacity: 0 !important;
    pointer-events: none !important;
    transition: opacity var(--lm-duration-fast) var(--lm-ease) !important;
}

.timeline-event:hover::after {
    opacity: 1 !important;
}

/* --------------------------------------------------------------------------
   Search Results
   -------------------------------------------------------------------------- */
.search-result {
    padding: 16px !important;
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-lg) !important;
    border: 1px solid var(--lm-border) !important;
    border-left: 4px solid var(--lm-primary) !important;
    margin-bottom: 12px !important;
    cursor: pointer !important;
    transition: all var(--lm-duration-fast) var(--lm-ease) !important;
}

.search-result:hover {
    transform: translateX(4px) !important;
    box-shadow: var(--lm-shadow-md) !important;
    border-left-color: var(--lm-primary-hover) !important;
}

.search-result-header {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    margin-bottom: 8px !important;
}

.search-result-timestamp {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    color: var(--lm-primary) !important;
    background: var(--lm-primary-light) !important;
    padding: 4px 10px !important;
    border-radius: var(--lm-radius-sm) !important;
}

/* Highlight matches */
mark.highlight,
.highlight {
    background: linear-gradient(120deg, #fef08a 0%, #fde047 100%) !important;
    padding: 2px 4px !important;
    border-radius: 3px !important;
}

.dark mark.highlight,
.dark .highlight {
    background: linear-gradient(120deg, #854d0e 0%, #a16207 100%) !important;
    color: #fef08a !important;
}

/* --------------------------------------------------------------------------
   Event Cards
   -------------------------------------------------------------------------- */
.event-card {
    padding: 16px !important;
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-lg) !important;
    border: 1px solid var(--lm-border) !important;
    margin-bottom: 12px !important;
    transition: all var(--lm-duration-fast) var(--lm-ease) !important;
    cursor: pointer !important;
}

.event-card:hover {
    border-color: var(--lm-primary) !important;
    box-shadow: var(--lm-shadow-md), 0 0 0 1px var(--lm-primary-light) !important;
    transform: translateY(-2px) !important;
}

.event-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: 8px !important;
}

.event-timestamp {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.875rem !important;
    color: var(--lm-primary) !important;
    font-weight: 600 !important;
}

.event-confidence {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    padding: 4px 8px !important;
    border-radius: var(--lm-radius-sm) !important;
    background: var(--lm-primary-light) !important;
}

/* --------------------------------------------------------------------------
   Summary Stats
   -------------------------------------------------------------------------- */
.summary-container {
    animation: fadeIn 0.5s var(--lm-ease) !important;
}

.summary-stats {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)) !important;
    gap: 16px !important;
    margin-top: 20px !important;
}

.stat-item {
    background: var(--lm-gradient-subtle) !important;
    padding: 20px !important;
    border-radius: var(--lm-radius-lg) !important;
    text-align: center !important;
    transition: all var(--lm-duration-fast) var(--lm-ease) !important;
}

.stat-item:hover {
    transform: translateY(-4px) !important;
    box-shadow: var(--lm-shadow-md) !important;
}

.stat-icon {
    font-size: 1.5rem !important;
    margin-bottom: 8px !important;
    display: block !important;
}

.stat-value {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--lm-text) !important;
    display: block !important;
}

.stat-label {
    font-size: 0.75rem !important;
    color: var(--lm-text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* --------------------------------------------------------------------------
   Transcript Display
   -------------------------------------------------------------------------- */
.transcript-container {
    max-height: 500px !important;
    overflow-y: auto !important;
    padding: 16px !important;
    background: var(--lm-bg) !important;
    border-radius: var(--lm-radius-lg) !important;
}

.transcript-chunk {
    padding: 12px 16px !important;
    border-radius: var(--lm-radius-md) !important;
    margin-bottom: 8px !important;
    background: var(--lm-surface) !important;
    border-left: 3px solid var(--lm-border) !important;
    transition: all var(--lm-duration-fast) var(--lm-ease) !important;
}

.transcript-chunk:hover {
    background: var(--lm-primary-light) !important;
    border-left-color: var(--lm-primary) !important;
}

.transcript-chunk-active {
    background: var(--lm-primary-light) !important;
    border-left-color: var(--lm-primary) !important;
}

.transcript-timestamp {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    color: var(--lm-primary) !important;
    margin-right: 12px !important;
}

/* --------------------------------------------------------------------------
   Empty States - Enhanced Onboarding Design
   -------------------------------------------------------------------------- */
.empty-state,
.placeholder,
[class*="-placeholder"],
[class*="-empty"] {
    text-align: center !important;
    padding: 48px 24px !important;
    color: var(--lm-text-secondary) !important;
    background: var(--lm-gradient-subtle) !important;
    border-radius: var(--lm-radius-xl) !important;
    border: 2px dashed var(--lm-border) !important;
}

/* Context-specific icons for each placeholder type */
.timeline-placeholder::before {
    content: '🎬' !important;
    display: block !important;
    font-size: 2.5rem !important;
    margin-bottom: 12px !important;
}

.summary-placeholder::before {
    content: '📊' !important;
    display: block !important;
    font-size: 2.5rem !important;
    margin-bottom: 12px !important;
}

.events-placeholder::before {
    content: '📍' !important;
    display: block !important;
    font-size: 2.5rem !important;
    margin-bottom: 12px !important;
}

.transcript-placeholder::before {
    content: '📝' !important;
    display: block !important;
    font-size: 2.5rem !important;
    margin-bottom: 12px !important;
}

.search-placeholder::before {
    content: '🔍' !important;
    display: block !important;
    font-size: 2.5rem !important;
    margin-bottom: 12px !important;
}

/* Keyboard hint for search */
.search-placeholder::after {
    content: 'Press / to search' !important;
    display: block !important;
    font-size: 0.75rem !important;
    margin-top: 8px !important;
    padding: 4px 12px !important;
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-sm) !important;
    color: var(--lm-text-muted) !important;
}

/* --------------------------------------------------------------------------
   Loading States & Skeletons
   -------------------------------------------------------------------------- */
.loading,
.skeleton {
    background: linear-gradient(
        90deg,
        var(--lm-border) 25%,
        var(--lm-bg) 50%,
        var(--lm-border) 75%
    ) !important;
    background-size: 200% 100% !important;
    animation: shimmer 1.5s ease-in-out infinite !important;
    border-radius: var(--lm-radius-md) !important;
}

/* Skeleton variants */
.skeleton-timeline {
    height: 48px !important;
    width: 100% !important;
    background: linear-gradient(90deg, var(--lm-bg) 0%, var(--lm-surface) 50%, var(--lm-bg) 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 1.5s ease-in-out infinite !important;
    border-radius: var(--lm-radius-lg) !important;
}

.skeleton-card {
    height: 100px !important;
    margin-bottom: 12px !important;
    background: linear-gradient(90deg, var(--lm-bg) 0%, var(--lm-surface) 50%, var(--lm-bg) 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 1.5s ease-in-out infinite !important;
    border-radius: var(--lm-radius-lg) !important;
}

.skeleton-text {
    height: 16px !important;
    width: 60% !important;
    display: inline-block !important;
    background: linear-gradient(90deg, var(--lm-bg) 0%, var(--lm-surface) 50%, var(--lm-bg) 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmer 1.5s ease-in-out infinite !important;
    border-radius: var(--lm-radius-sm) !important;
}

/* Processing overlay */
.processing-overlay {
    position: absolute !important;
    inset: 0 !important;
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(4px) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    z-index: 100 !important;
    animation: fadeIn 200ms ease !important;
}

.dark .processing-overlay {
    background: rgba(15, 23, 42, 0.9) !important;
}

/* --------------------------------------------------------------------------
   Error States
   -------------------------------------------------------------------------- */
.error,
[class*="-error"] {
    background: rgba(239, 68, 68, 0.1) !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
    border-radius: var(--lm-radius-lg) !important;
    padding: 16px !important;
    color: var(--lm-error) !important;
}

.error::before {
    content: '⚠️ ' !important;
}

/* --------------------------------------------------------------------------
   Theme Toggle
   -------------------------------------------------------------------------- */
.theme-toggle {
    background: var(--lm-surface) !important;
    border: 1px solid var(--lm-border) !important;
    border-radius: var(--lm-radius-full) !important;
    padding: 8px 16px !important;
    font-size: 0.875rem !important;
    cursor: pointer !important;
    transition: all var(--lm-duration-fast) var(--lm-ease) !important;
}

.theme-toggle:hover {
    background: var(--lm-primary-light) !important;
    border-color: var(--lm-primary) !important;
    transform: scale(1.05) !important;
}

/* --------------------------------------------------------------------------
   Footer
   -------------------------------------------------------------------------- */
footer,
.built-with {
    opacity: 0.5 !important;
    transition: opacity var(--lm-duration-fast) !important;
}

footer:hover,
.built-with:hover {
    opacity: 1 !important;
}

/* --------------------------------------------------------------------------
   Scrollbar
   -------------------------------------------------------------------------- */
::-webkit-scrollbar {
    width: 8px !important;
    height: 8px !important;
}

::-webkit-scrollbar-track {
    background: var(--lm-bg) !important;
    border-radius: var(--lm-radius-full) !important;
}

::-webkit-scrollbar-thumb {
    background: var(--lm-border) !important;
    border-radius: var(--lm-radius-full) !important;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--lm-text-muted) !important;
}

/* --------------------------------------------------------------------------
   Animations
   -------------------------------------------------------------------------- */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-10px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

/* Apply animations to elements */
.gr-panel,
.gr-box,
.search-result,
.event-card {
    animation: fadeIn 0.3s var(--lm-ease) !important;
}

/* --------------------------------------------------------------------------
   Accessibility
   -------------------------------------------------------------------------- */
:focus-visible {
    outline: 2px solid var(--lm-primary) !important;
    outline-offset: 2px !important;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* High contrast */
@media (prefers-contrast: high) {
    :root {
        --lm-border: #111827;
        --lm-text: #000000;
    }
}

/* --------------------------------------------------------------------------
   Responsive
   -------------------------------------------------------------------------- */
@media (max-width: 768px) {
    .gradio-container {
        padding: 12px !important;
    }

    .gradio-container > .main {
        padding: 16px !important;
        border-radius: var(--lm-radius-xl) !important;
    }

    .summary-stats {
        grid-template-columns: repeat(2, 1fr) !important;
    }

    h1 {
        font-size: 1.75rem !important;
    }
}

@media (max-width: 480px) {
    .summary-stats {
        grid-template-columns: 1fr !important;
    }

    button.primary,
    .gr-button-primary {
        width: 100% !important;
    }
}

/* ==========================================================================
   LEVEL B: PRO UI COMPONENTS
   ========================================================================== */

/* --------------------------------------------------------------------------
   B1: Skeleton Loading Components
   -------------------------------------------------------------------------- */

/* Base skeleton animation */
@keyframes skeletonShimmer {
    0% {
        background-position: -200% 0;
    }
    100% {
        background-position: 200% 0;
    }
}

@keyframes skeletonFadeIn {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Skeleton base styles */
.skeleton-text,
.skeleton-title,
.skeleton-icon,
.skeleton-badge,
.skeleton-timestamp,
.skeleton-pulse {
    background: linear-gradient(
        90deg,
        var(--lm-gray-200) 0%,
        var(--lm-gray-100) 50%,
        var(--lm-gray-200) 100%
    ) !important;
    background-size: 200% 100% !important;
    animation: skeletonShimmer 1.5s ease-in-out infinite !important;
    border-radius: var(--lm-radius-sm) !important;
}

.dark .skeleton-text,
.dark .skeleton-title,
.dark .skeleton-icon,
.dark .skeleton-badge,
.dark .skeleton-timestamp,
.dark .skeleton-pulse {
    background: linear-gradient(
        90deg,
        rgba(99, 102, 241, 0.2) 0%,
        rgba(139, 92, 246, 0.3) 50%,
        rgba(99, 102, 241, 0.2) 100%
    ) !important;
}

/* Skeleton sizes */
.skeleton-text {
    height: 16px !important;
    width: 100% !important;
    margin-bottom: 8px !important;
}

.skeleton-text-sm {
    height: 12px !important;
    width: 60px !important;
}

.skeleton-text-lg {
    height: 24px !important;
    width: 80% !important;
}

.skeleton-title {
    height: 32px !important;
    width: 60% !important;
    margin-bottom: 16px !important;
}

.skeleton-icon {
    width: 32px !important;
    height: 32px !important;
    border-radius: 50% !important;
}

.skeleton-badge {
    width: 48px !important;
    height: 20px !important;
    border-radius: var(--lm-radius-full) !important;
}

.skeleton-timestamp {
    width: 60px !important;
    height: 14px !important;
}

/* Skeleton Timeline */
.skeleton-timeline-wrapper {
    padding: var(--lm-space-4) !important;
    animation: skeletonFadeIn 0.3s ease-out !important;
}

.skeleton-timeline {
    height: 48px !important;
    border-radius: var(--lm-radius-lg) !important;
    margin-bottom: var(--lm-space-3) !important;
    overflow: hidden !important;
}

.skeleton-labels {
    display: flex !important;
    justify-content: space-between !important;
}

/* Skeleton Summary */
.skeleton-summary {
    padding: var(--lm-space-6) !important;
    animation: skeletonFadeIn 0.3s ease-out !important;
}

.skeleton-stats-grid {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: var(--lm-space-4) !important;
}

.skeleton-stat-card {
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-lg) !important;
    padding: var(--lm-space-4) !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: var(--lm-space-2) !important;
}

/* Skeleton Events */
.skeleton-events-list {
    display: flex !important;
    flex-direction: column !important;
    gap: var(--lm-space-3) !important;
    padding: var(--lm-space-4) !important;
}

.skeleton-event-card {
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-lg) !important;
    padding: var(--lm-space-4) !important;
    animation: skeletonFadeIn 0.4s ease-out backwards !important;
}

.skeleton-event-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: var(--lm-space-3) !important;
}

/* Skeleton Transcript */
.skeleton-transcript {
    display: flex !important;
    flex-direction: column !important;
    gap: var(--lm-space-2) !important;
    padding: var(--lm-space-4) !important;
}

.skeleton-transcript-chunk {
    display: flex !important;
    gap: var(--lm-space-3) !important;
    align-items: center !important;
    padding: var(--lm-space-3) !important;
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-md) !important;
    animation: skeletonFadeIn 0.3s ease-out backwards !important;
}

/* Skeleton Search Results */
.skeleton-search-results {
    display: flex !important;
    flex-direction: column !important;
    gap: var(--lm-space-3) !important;
    padding: var(--lm-space-4) !important;
}

.skeleton-search-result {
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-lg) !important;
    padding: var(--lm-space-4) !important;
    animation: skeletonFadeIn 0.4s ease-out backwards !important;
}

.skeleton-result-header {
    display: flex !important;
    gap: var(--lm-space-3) !important;
    align-items: center !important;
    margin-bottom: var(--lm-space-3) !important;
}

/* --------------------------------------------------------------------------
   B2: Multi-Stage Progress
   -------------------------------------------------------------------------- */

.multi-stage-progress {
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-xl) !important;
    padding: var(--lm-space-6) !important;
    box-shadow: var(--lm-shadow-md) !important;
}

.progress-stages {
    display: flex !important;
    justify-content: space-between !important;
    margin-bottom: var(--lm-space-6) !important;
    overflow-x: auto !important;
    padding-bottom: var(--lm-space-2) !important;
}

.progress-stage-item {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: var(--lm-space-1) !important;
    min-width: 60px !important;
    transition: all 0.3s ease !important;
}

.stage-icon {
    font-size: 1.25rem !important;
    width: 36px !important;
    height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 50% !important;
    background: var(--lm-gray-100) !important;
    transition: all 0.3s ease !important;
}

.stage-label {
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    color: var(--lm-text-muted) !important;
    text-align: center !important;
    white-space: nowrap !important;
}

/* Stage states */
.stage-completed .stage-icon {
    background: var(--lm-success) !important;
    color: white !important;
}

.stage-completed .stage-label {
    color: var(--lm-success) !important;
}

.stage-active .stage-icon {
    background: linear-gradient(135deg, var(--lm-primary), var(--lm-accent)) !important;
    color: white !important;
    animation: stagePulse 1.5s ease-in-out infinite !important;
}

.stage-active .stage-label {
    color: var(--lm-primary) !important;
    font-weight: 600 !important;
}

.stage-pending .stage-icon {
    background: var(--lm-gray-200) !important;
    color: var(--lm-gray-400) !important;
}

@keyframes stagePulse {
    0%, 100% {
        transform: scale(1);
        box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4);
    }
    50% {
        transform: scale(1.05);
        box-shadow: 0 0 0 8px rgba(99, 102, 241, 0);
    }
}

/* Progress bar */
.progress-bar-wrapper {
    display: flex !important;
    align-items: center !important;
    gap: var(--lm-space-3) !important;
    margin-bottom: var(--lm-space-4) !important;
}

.progress-bar-track {
    flex: 1 !important;
    height: 12px !important;
    background: var(--lm-gray-200) !important;
    border-radius: var(--lm-radius-full) !important;
    overflow: hidden !important;
}

.progress-bar-fill {
    height: 100% !important;
    background: linear-gradient(90deg, var(--lm-primary), var(--lm-accent)) !important;
    border-radius: var(--lm-radius-full) !important;
    position: relative !important;
    transition: width 0.4s ease !important;
}

.progress-bar-shimmer {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.3) 50%,
        transparent 100%
    ) !important;
    animation: progressShimmer 1.5s ease-in-out infinite !important;
}

@keyframes progressShimmer {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(100%);
    }
}

.progress-percentage-label {
    font-size: 0.875rem !important;
    font-weight: 700 !important;
    color: var(--lm-primary) !important;
    min-width: 45px !important;
    text-align: right !important;
}

/* Progress message box */
.progress-message-box {
    display: flex !important;
    align-items: center !important;
    gap: var(--lm-space-3) !important;
    padding: var(--lm-space-3) var(--lm-space-4) !important;
    background: var(--lm-gray-50) !important;
    border-radius: var(--lm-radius-lg) !important;
    border-left: 4px solid var(--lm-primary) !important;
}

.progress-spinner {
    width: 16px !important;
    height: 16px !important;
    border: 2px solid var(--lm-gray-300) !important;
    border-top-color: var(--lm-primary) !important;
    border-radius: 50% !important;
    animation: spin 0.8s linear infinite !important;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.progress-message-text {
    font-size: 0.875rem !important;
    color: var(--lm-text-secondary) !important;
}

/* --------------------------------------------------------------------------
   B3: Tab Transitions
   -------------------------------------------------------------------------- */

/* Tab panel animations */
[role="tabpanel"] {
    animation: tabFadeIn 0.3s ease-out !important;
}

@keyframes tabFadeIn {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Tab button hover effects */
[role="tab"] {
    transition: all 0.2s ease !important;
    position: relative !important;
}

[role="tab"]::after {
    content: '' !important;
    position: absolute !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) scaleX(0) !important;
    width: 80% !important;
    height: 3px !important;
    background: linear-gradient(90deg, var(--lm-primary), var(--lm-accent)) !important;
    border-radius: var(--lm-radius-full) !important;
    transition: transform 0.2s ease !important;
}

[role="tab"][aria-selected="true"]::after {
    transform: translateX(-50%) scaleX(1) !important;
}

[role="tab"]:hover:not([aria-selected="true"])::after {
    transform: translateX(-50%) scaleX(0.5) !important;
}

/* --------------------------------------------------------------------------
   B4: Toast Notifications
   -------------------------------------------------------------------------- */

.toast-container {
    position: fixed !important;
    top: var(--lm-space-6) !important;
    right: var(--lm-space-6) !important;
    z-index: 9999 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: var(--lm-space-3) !important;
    pointer-events: none !important;
}

.toast {
    display: flex !important;
    align-items: center !important;
    gap: var(--lm-space-3) !important;
    padding: var(--lm-space-3) var(--lm-space-4) !important;
    background: var(--lm-surface) !important;
    border-radius: var(--lm-radius-lg) !important;
    box-shadow: var(--lm-shadow-lg) !important;
    pointer-events: auto !important;
    animation: toastSlideIn 0.3s ease-out !important;
    min-width: 280px !important;
    max-width: 400px !important;
}

@keyframes toastSlideIn {
    from {
        opacity: 0;
        transform: translateX(100%);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.toast-icon {
    font-size: 1.25rem !important;
    flex-shrink: 0 !important;
}

.toast-message {
    flex: 1 !important;
    font-size: 0.875rem !important;
    color: var(--lm-text-primary) !important;
}

.toast-dismiss {
    background: transparent !important;
    border: none !important;
    padding: var(--lm-space-1) !important;
    cursor: pointer !important;
    color: var(--lm-text-muted) !important;
    font-size: 1.25rem !important;
    line-height: 1 !important;
    transition: color 0.2s ease !important;
}

.toast-dismiss:hover {
    color: var(--lm-text-primary) !important;
}

/* Toast variants */
.toast-success {
    border-left: 4px solid var(--lm-success) !important;
}

.toast-error {
    border-left: 4px solid var(--lm-error) !important;
}

.toast-warning {
    border-left: 4px solid var(--lm-warning) !important;
}

.toast-info {
    border-left: 4px solid var(--lm-info) !important;
}

/* --------------------------------------------------------------------------
   B5: Responsive Improvements
   -------------------------------------------------------------------------- */

@media (max-width: 768px) {
    .progress-stages {
        gap: var(--lm-space-1) !important;
    }

    .progress-stage-item {
        min-width: 40px !important;
    }

    .stage-label {
        display: none !important;
    }

    .stage-icon {
        width: 28px !important;
        height: 28px !important;
        font-size: 1rem !important;
    }

    .skeleton-stats-grid {
        grid-template-columns: 1fr !important;
    }

    .toast-container {
        top: auto !important;
        bottom: var(--lm-space-4) !important;
        right: var(--lm-space-4) !important;
        left: var(--lm-space-4) !important;
    }

    .toast {
        min-width: auto !important;
        max-width: none !important;
    }
}

/* --------------------------------------------------------------------------
   B6: Search Result Animations
   -------------------------------------------------------------------------- */

.search-results-list .search-result {
    animation: searchResultFadeIn 0.3s ease-out backwards !important;
}

.search-results-list .search-result:nth-child(1) { animation-delay: 0s !important; }
.search-results-list .search-result:nth-child(2) { animation-delay: 0.05s !important; }
.search-results-list .search-result:nth-child(3) { animation-delay: 0.1s !important; }
.search-results-list .search-result:nth-child(4) { animation-delay: 0.15s !important; }
.search-results-list .search-result:nth-child(5) { animation-delay: 0.2s !important; }
.search-results-list .search-result:nth-child(6) { animation-delay: 0.25s !important; }
.search-results-list .search-result:nth-child(7) { animation-delay: 0.3s !important; }
.search-results-list .search-result:nth-child(8) { animation-delay: 0.35s !important; }
.search-results-list .search-result:nth-child(9) { animation-delay: 0.4s !important; }
.search-results-list .search-result:nth-child(10) { animation-delay: 0.45s !important; }

@keyframes searchResultFadeIn {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Events list animations */
.events-list .event-card {
    animation: eventCardSlideIn 0.4s ease-out backwards !important;
}

.events-list .event-card:nth-child(1) { animation-delay: 0s !important; }
.events-list .event-card:nth-child(2) { animation-delay: 0.08s !important; }
.events-list .event-card:nth-child(3) { animation-delay: 0.16s !important; }
.events-list .event-card:nth-child(4) { animation-delay: 0.24s !important; }
.events-list .event-card:nth-child(5) { animation-delay: 0.32s !important; }

@keyframes eventCardSlideIn {
    from {
        opacity: 0;
        transform: translateX(-16px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* Transcript chunk animations */
.transcript-container .transcript-chunk {
    animation: transcriptFadeIn 0.3s ease-out backwards !important;
}

@keyframes transcriptFadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

/* --------------------------------------------------------------------------
   Print
   -------------------------------------------------------------------------- */
@media print {
    .gradio-container {
        background: white !important;
    }

    .gradio-container > .main {
        box-shadow: none !important;
    }
}

/* ==========================================================================
   LEVEL C: BEST-IN-CLASS IMPROVEMENTS
   ========================================================================== */

/* --------------------------------------------------------------------------
   C1: Accessibility - Focus States
   -------------------------------------------------------------------------- */

/* Focus visible outline for keyboard navigation */
*:focus-visible {
    outline: 3px solid var(--lm-primary) !important;
    outline-offset: 2px !important;
    border-radius: var(--lm-radius-sm) !important;
}

/* Remove default focus for mouse users */
*:focus:not(:focus-visible) {
    outline: none !important;
}

/* Enhanced focus for interactive elements */
button:focus-visible,
[role="button"]:focus-visible,
[role="tab"]:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
a:focus-visible {
    outline: 3px solid var(--lm-primary) !important;
    outline-offset: 2px !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
}

/* Skip link for screen readers */
.skip-link {
    position: absolute !important;
    top: -100px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background: var(--lm-primary) !important;
    color: white !important;
    padding: var(--lm-space-3) var(--lm-space-6) !important;
    border-radius: var(--lm-radius-lg) !important;
    z-index: 10000 !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    transition: top 0.2s ease !important;
}

.skip-link:focus {
    top: var(--lm-space-4) !important;
}

/* Screen reader only content */
.sr-only {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}

/* Announce live regions */
[aria-live="polite"],
[aria-live="assertive"] {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}

/* --------------------------------------------------------------------------
   C2: Reduced Motion Support
   -------------------------------------------------------------------------- */

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }

    /* Disable specific animations */
    .skeleton-text,
    .skeleton-title,
    .skeleton-icon,
    .skeleton-badge,
    .skeleton-timestamp,
    .skeleton-pulse {
        animation: none !important;
        background: var(--lm-gray-200) !important;
    }

    .progress-bar-shimmer {
        animation: none !important;
        display: none !important;
    }

    .stage-active .stage-icon {
        animation: none !important;
    }

    .progress-spinner {
        animation: none !important;
        border-color: var(--lm-primary) !important;
    }

    /* Use solid indicators instead of animations */
    .skeleton-text::after,
    .skeleton-title::after {
        content: 'Loading...' !important;
        position: absolute !important;
        color: var(--lm-text-muted) !important;
        font-size: 0.75rem !important;
    }
}

/* --------------------------------------------------------------------------
   C3: Advanced Micro-interactions
   -------------------------------------------------------------------------- */

/* Button press effect */
button:active:not(:disabled),
[role="button"]:active:not([aria-disabled="true"]) {
    transform: scale(0.97) !important;
    transition: transform 0.1s ease !important;
}

/* Card lift on hover */
.event-card:hover,
.search-result:hover,
.stat-item:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--lm-shadow-lg) !important;
    transition: all 0.2s ease !important;
}

/* Tab underline animation */
[role="tab"] {
    position: relative !important;
    overflow: hidden !important;
}

[role="tab"]::before {
    content: '' !important;
    position: absolute !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 3px !important;
    background: linear-gradient(90deg, var(--lm-primary), var(--lm-accent)) !important;
    transform: scaleX(0) !important;
    transform-origin: right !important;
    transition: transform 0.3s ease !important;
}

[role="tab"]:hover::before {
    transform: scaleX(1) !important;
    transform-origin: left !important;
}

[role="tab"][aria-selected="true"]::before {
    transform: scaleX(1) !important;
}

/* Input focus glow */
input:focus,
textarea:focus {
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    border-color: var(--lm-primary) !important;
    transition: all 0.2s ease !important;
}

/* Timeline marker hover expand */
.timeline-event:hover {
    transform: scale(1.3) translateY(-2px) !important;
    z-index: 10 !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

/* Ripple effect for buttons */
.btn-primary::after,
.btn-secondary::after {
    content: '' !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    width: 0 !important;
    height: 0 !important;
    background: rgba(255, 255, 255, 0.3) !important;
    border-radius: 50% !important;
    transform: translate(-50%, -50%) !important;
    transition: width 0.4s ease, height 0.4s ease, opacity 0.4s ease !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

.btn-primary:active::after,
.btn-secondary:active::after {
    width: 200px !important;
    height: 200px !important;
    opacity: 1 !important;
    transition: width 0s, height 0s, opacity 0s !important;
}

/* Progress bar glow */
.progress-bar-fill {
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.5) !important;
}

/* Icon bounce on hover */
.stat-icon:hover {
    animation: iconBounce 0.4s ease !important;
}

@keyframes iconBounce {
    0%, 100% { transform: translateY(0); }
    25% { transform: translateY(-4px); }
    50% { transform: translateY(0); }
    75% { transform: translateY(-2px); }
}

/* --------------------------------------------------------------------------
   C4: Focus Management & Keyboard Navigation
   -------------------------------------------------------------------------- */

/* Focus trap indicator */
[data-focus-trap="true"] {
    position: relative !important;
}

[data-focus-trap="true"]::before {
    content: '' !important;
    position: absolute !important;
    inset: -4px !important;
    border: 2px dashed var(--lm-primary) !important;
    border-radius: var(--lm-radius-lg) !important;
    pointer-events: none !important;
    opacity: 0 !important;
    transition: opacity 0.2s ease !important;
}

[data-focus-trap="true"]:focus-within::before {
    opacity: 0.5 !important;
}

/* Keyboard navigation hints */
[data-keyboard-hint]::after {
    content: attr(data-keyboard-hint) !important;
    position: absolute !important;
    bottom: -24px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    background: var(--lm-gray-800) !important;
    color: white !important;
    padding: 2px 8px !important;
    border-radius: var(--lm-radius-sm) !important;
    font-size: 0.7rem !important;
    white-space: nowrap !important;
    opacity: 0 !important;
    pointer-events: none !important;
    transition: opacity 0.2s ease !important;
}

[data-keyboard-hint]:focus-visible::after {
    opacity: 1 !important;
}

/* Tab list keyboard navigation */
[role="tablist"] {
    display: flex !important;
    gap: var(--lm-space-1) !important;
}

[role="tablist"] [role="tab"] {
    flex: 0 0 auto !important;
}

/* Arrow key navigation indicator */
[role="tablist"]:focus-within::after {
    content: '← →' !important;
    position: absolute !important;
    right: var(--lm-space-2) !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    color: var(--lm-text-muted) !important;
    font-size: 0.75rem !important;
    opacity: 0.6 !important;
}

/* --------------------------------------------------------------------------
   C5: High Contrast Mode
   -------------------------------------------------------------------------- */

@media (prefers-contrast: more) {
    :root {
        --lm-primary: #0000ff !important;
        --lm-success: #008000 !important;
        --lm-warning: #ff8c00 !important;
        --lm-error: #ff0000 !important;
        --lm-text-primary: #000000 !important;
        --lm-text-secondary: #333333 !important;
        --lm-border: #000000 !important;
    }

    .dark {
        --lm-primary: #6699ff !important;
        --lm-success: #66ff66 !important;
        --lm-warning: #ffcc00 !important;
        --lm-error: #ff6666 !important;
        --lm-text-primary: #ffffff !important;
        --lm-text-secondary: #cccccc !important;
        --lm-border: #ffffff !important;
    }

    /* High contrast borders */
    button,
    input,
    textarea,
    select,
    .event-card,
    .search-result,
    .transcript-chunk {
        border: 2px solid var(--lm-border) !important;
    }

    /* High contrast focus */
    *:focus-visible {
        outline: 4px solid var(--lm-primary) !important;
        outline-offset: 2px !important;
    }

    /* Remove gradients in high contrast */
    .gradio-container,
    button.primary,
    .btn-primary,
    .progress-bar-fill {
        background: var(--lm-primary) !important;
        background-image: none !important;
    }

    /* Ensure text contrast */
    .timeline-placeholder,
    .summary-placeholder,
    .events-placeholder,
    .transcript-placeholder,
    .search-placeholder {
        background: var(--lm-surface) !important;
        color: var(--lm-text-primary) !important;
        border: 2px solid var(--lm-border) !important;
    }
}

/* Forced colors mode (Windows High Contrast) */
@media (forced-colors: active) {
    button,
    [role="button"],
    [role="tab"] {
        border: 2px solid ButtonText !important;
    }

    button:focus,
    [role="button"]:focus,
    [role="tab"]:focus {
        outline: 3px solid Highlight !important;
    }

    .progress-bar-fill {
        background: Highlight !important;
    }

    .timeline-event {
        background: Highlight !important;
        forced-color-adjust: none !important;
    }
}

/* --------------------------------------------------------------------------
   C6: Performance Optimizations
   -------------------------------------------------------------------------- */

/* CSS containment for better rendering */
.event-card,
.search-result,
.transcript-chunk,
.skeleton-event-card,
.skeleton-search-result,
.skeleton-transcript-chunk {
    contain: layout style !important;
}

/* Large containers use full containment */
.events-list,
.search-results-list,
.transcript-container {
    contain: layout style paint !important;
}

/* Will-change hints for animated elements */
.timeline-event,
.progress-bar-fill,
.toast,
[role="tab"]::before,
[role="tab"]::after {
    will-change: transform !important;
}

.skeleton-text,
.skeleton-title,
.skeleton-icon,
.progress-bar-shimmer {
    will-change: background-position !important;
}

/* Remove will-change after animation completes */
.event-card,
.search-result {
    will-change: auto !important;
}

.event-card:hover,
.search-result:hover {
    will-change: transform, box-shadow !important;
}

/* GPU acceleration for smooth animations */
.toast,
.progress-bar-fill,
.timeline-event:hover {
    transform: translateZ(0) !important;
    backface-visibility: hidden !important;
}

/* Content-visibility for off-screen optimization */
.transcript-chunk:not(:nth-child(-n+10)) {
    content-visibility: auto !important;
    contain-intrinsic-size: 0 60px !important;
}

.event-card:not(:nth-child(-n+5)) {
    content-visibility: auto !important;
    contain-intrinsic-size: 0 100px !important;
}

/* Optimize paint for fixed elements */
.toast-container,
.skip-link {
    isolation: isolate !important;
}

/* Font display optimization */
@font-face {
    font-display: swap !important;
}
"""


def get_theme_colors(dark_mode: bool = False) -> dict[str, str]:
    """Get color palette for current theme."""
    return DARK_THEME if dark_mode else LIGHT_THEME


def get_css() -> str:
    """Get the complete custom CSS."""
    return CUSTOM_CSS
