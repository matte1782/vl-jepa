# Typography & Visual Hierarchy Enhancement Plan

**Project:** Lecture Mind
**Date:** January 2026
**Focus:** Award-winning text experiences with kinetic typography and advanced visual hierarchy

---

## Current State Analysis

### Existing Typography Foundation

The current implementation uses a solid foundation:

- **Primary Font:** Inter (weights 400-800)
- **Monospace Font:** JetBrains Mono (weights 400-500)
- **Type Scale:** Fixed rem values (0.75rem to 3rem)
- **Line Heights:** 1.0 to 1.625
- **Letter Spacing:** -0.05em to 0.1em

### Identified Opportunities

1. **Static Type Scale** - No fluid typography using modern CSS clamp()
2. **Limited Font Expressiveness** - No variable font features utilized
3. **No Kinetic Typography** - Text is static, missing motion opportunities
4. **Hierarchy Gaps** - Missing optical size adjustments for different contexts
5. **No Text Effects** - Missing gradient fills, glow effects, text shadows

---

## 1. Variable Font Implementation

### Recommended Variable Fonts

```css
/* Primary: Inter Variable - includes optical sizing */
@font-face {
  font-family: 'Inter Variable';
  src: url('https://fonts.gstatic.com/s/inter/v13/UcC73FwrK3iLTeHuS_fvQtMwCp50KnMa1ZL7.woff2') format('woff2');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
  font-optical-sizing: auto;
}

/* Alternative Premium: Satoshi Variable */
@font-face {
  font-family: 'Satoshi Variable';
  src: url('/fonts/Satoshi-Variable.woff2') format('woff2');
  font-weight: 300 900;
  font-display: swap;
}

/* Display Headlines: Cabinet Grotesk Variable */
@font-face {
  font-family: 'Cabinet Grotesk Variable';
  src: url('/fonts/CabinetGrotesk-Variable.woff2') format('woff2');
  font-weight: 100 900;
  font-display: swap;
}
```

### Weight Animation on Hover

```css
/* CSS Custom Properties for dynamic weight */
:root {
  --font-weight-normal: 400;
  --font-weight-hover: 600;
  --font-weight-active: 700;
  --font-weight-transition: 200ms;
}

/* Interactive text elements */
.nav-link,
.tabs-trigger,
.feature-title {
  font-variation-settings: 'wght' var(--font-weight-normal);
  transition: font-variation-settings var(--font-weight-transition) var(--ease-out);
}

.nav-link:hover,
.tabs-trigger:hover,
.feature-title:hover {
  font-variation-settings: 'wght' var(--font-weight-hover);
}

.nav-link:active,
.tabs-trigger:active {
  font-variation-settings: 'wght' var(--font-weight-active);
}

/* Smooth weight morphing for active states */
.tabs-trigger[data-state="active"] {
  font-variation-settings: 'wght' 650;
}
```

### Optical Size Adjustments

```css
/* Headlines get bolder, tighter spacing */
.hero-title {
  font-optical-sizing: auto;
  font-variation-settings: 'wght' 800, 'opsz' 72;
  letter-spacing: -0.04em;
}

/* Body text optimized for reading */
.feature-description,
.hero-subtitle,
p {
  font-optical-sizing: auto;
  font-variation-settings: 'wght' 400, 'opsz' 14;
  letter-spacing: 0;
}

/* Small text needs slightly heavier weight */
.text-xs,
.badge,
.caption {
  font-variation-settings: 'wght' 450;
}
```

---

## 2. Kinetic Typography

### Letter-by-Letter Reveal Animation

```css
/* Base styles for text reveal */
.text-reveal {
  overflow: hidden;
}

.text-reveal span {
  display: inline-block;
  opacity: 0;
  transform: translateY(100%);
  animation: letterReveal 0.6s var(--spring-bounce-1) forwards;
}

@keyframes letterReveal {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Stagger each letter */
.text-reveal span:nth-child(1) { animation-delay: 0.00s; }
.text-reveal span:nth-child(2) { animation-delay: 0.03s; }
.text-reveal span:nth-child(3) { animation-delay: 0.06s; }
.text-reveal span:nth-child(4) { animation-delay: 0.09s; }
.text-reveal span:nth-child(5) { animation-delay: 0.12s; }
/* Continue pattern for additional characters */
```

### Typewriter Animation

```css
/* Typewriter effect for hero subtitle or search */
.typewriter {
  overflow: hidden;
  border-right: 2px solid var(--primary);
  white-space: nowrap;
  animation:
    typing 3s steps(40, end) forwards,
    blink-caret 0.75s step-end infinite;
  width: 0;
}

@keyframes typing {
  from { width: 0; }
  to { width: 100%; }
}

@keyframes blink-caret {
  from, to { border-color: transparent; }
  50% { border-color: var(--primary); }
}

/* Multi-line typewriter for longer text */
.typewriter-multiline {
  --lines: 3;
  animation:
    typing-multi calc(var(--lines) * 2s) steps(40, end) forwards,
    blink-caret 0.75s step-end infinite;
}
```

### Gradient Text Animation

```css
/* Animated gradient text */
.gradient-text-animated {
  background: linear-gradient(
    135deg,
    var(--primary) 0%,
    var(--accent) 25%,
    var(--primary) 50%,
    var(--accent) 75%,
    var(--primary) 100%
  );
  background-size: 400% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientFlow 8s ease-in-out infinite;
}

@keyframes gradientFlow {
  0% { background-position: 0% center; }
  50% { background-position: 100% center; }
  100% { background-position: 0% center; }
}

/* Faster gradient for emphasis */
.gradient-text-pulse {
  background: linear-gradient(
    90deg,
    var(--foreground) 0%,
    var(--primary) 50%,
    var(--foreground) 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientPulse 2s ease-in-out infinite;
}

@keyframes gradientPulse {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}
```

### Text Morphing Transitions

```css
/* Morphing text with clip-path */
.text-morph {
  position: relative;
  overflow: hidden;
}

.text-morph::before,
.text-morph::after {
  content: attr(data-text);
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.text-morph::before {
  clip-path: polygon(0 0, 100% 0, 100% 50%, 0 50%);
  transform: translateY(0);
  transition: transform 0.4s var(--spring-bounce-1);
}

.text-morph::after {
  clip-path: polygon(0 50%, 100% 50%, 100% 100%, 0 100%);
  transform: translateY(0);
  transition: transform 0.4s var(--spring-bounce-1) 0.1s;
}

.text-morph:hover::before {
  transform: translateY(-100%);
}

.text-morph:hover::after {
  transform: translateY(100%);
}
```

---

## 3. Fluid Type Scale System

### Modern Clamp-Based Scale

```css
:root {
  /* Base fluid unit */
  --fluid-min-width: 320;
  --fluid-max-width: 1440;
  --fluid-screen: 100vw;

  /* Modular Scale Ratios */
  --ratio-minor-second: 1.067;
  --ratio-major-second: 1.125;
  --ratio-minor-third: 1.2;
  --ratio-major-third: 1.25;
  --ratio-perfect-fourth: 1.333;
  --ratio-augmented-fourth: 1.414;
  --ratio-perfect-fifth: 1.5;

  /* Active ratio for the scale */
  --type-ratio: var(--ratio-major-third);

  /* Fluid Type Scale */
  --text-xs: clamp(0.64rem, 0.58rem + 0.25vw, 0.75rem);
  --text-sm: clamp(0.8rem, 0.74rem + 0.25vw, 0.875rem);
  --text-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  --text-lg: clamp(1.125rem, 1.04rem + 0.4vw, 1.35rem);
  --text-xl: clamp(1.25rem, 1.12rem + 0.6vw, 1.6rem);
  --text-2xl: clamp(1.5rem, 1.3rem + 1vw, 2rem);
  --text-3xl: clamp(1.875rem, 1.5rem + 1.5vw, 2.5rem);
  --text-4xl: clamp(2.25rem, 1.7rem + 2.5vw, 3.5rem);
  --text-5xl: clamp(3rem, 2rem + 4vw, 5rem);
  --text-6xl: clamp(3.75rem, 2.5rem + 5vw, 6rem);

  /* Display sizes for hero text */
  --text-display-sm: clamp(2.5rem, 1.5rem + 4vw, 4rem);
  --text-display-md: clamp(3rem, 2rem + 5vw, 5.5rem);
  --text-display-lg: clamp(4rem, 2.5rem + 6vw, 7rem);
  --text-display-xl: clamp(5rem, 3rem + 8vw, 9rem);
}

/* Responsive line-height adjustments */
h1, .hero-title {
  line-height: clamp(1.05, 0.95 + 0.1vw, 1.15);
}

h2, .section-title {
  line-height: clamp(1.1, 1 + 0.15vw, 1.25);
}

h3, h4 {
  line-height: clamp(1.2, 1.1 + 0.1vw, 1.3);
}

p, .body-text {
  line-height: clamp(1.5, 1.4 + 0.1vw, 1.65);
}
```

### Optical Balance Adjustments

```css
/* Compensate for optical weight differences at large sizes */
.hero-title {
  font-size: var(--text-display-md);
  letter-spacing: calc(-0.02em - 0.001em * var(--text-display-md));
}

/* Small caps styling with optical adjustments */
.small-caps {
  font-variant-caps: small-caps;
  letter-spacing: 0.05em;
  font-variation-settings: 'wght' 500;
}

/* Superscripts and subscripts */
sup, sub {
  font-size: 0.75em;
  font-variation-settings: 'wght' 500;
}

/* Numbers in large displays */
.stat-value, .hero-stat-value {
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum' 1;
}
```

---

## 4. Hierarchy Refinement

### Clear Heading Levels

```css
/* Primary Heading - Page Title/Hero */
.heading-1, h1 {
  font-size: var(--text-display-sm);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.1;
  color: var(--foreground);
  text-wrap: balance;
}

/* Secondary Heading - Section Title */
.heading-2, h2 {
  font-size: var(--text-4xl);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.15;
  color: var(--foreground);
  text-wrap: balance;
}

/* Tertiary Heading - Card Title */
.heading-3, h3 {
  font-size: var(--text-2xl);
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.25;
  color: var(--foreground);
}

/* Quaternary Heading - Subsection */
.heading-4, h4 {
  font-size: var(--text-xl);
  font-weight: 600;
  letter-spacing: 0;
  line-height: 1.3;
  color: var(--foreground);
}

/* Quinary Heading - Label */
.heading-5, h5 {
  font-size: var(--text-lg);
  font-weight: 600;
  letter-spacing: 0;
  line-height: 1.4;
  color: var(--foreground);
}

/* Senary Heading - Eyebrow */
.heading-6, h6 {
  font-size: var(--text-sm);
  font-weight: 600;
  letter-spacing: 0.05em;
  line-height: 1.5;
  text-transform: uppercase;
  color: var(--foreground-muted);
}
```

### Supporting Text Contrast

```css
/* Lead paragraph - larger body text */
.lead, .text-lead {
  font-size: var(--text-xl);
  line-height: 1.6;
  color: var(--foreground-muted);
  font-weight: 400;
}

/* Standard body text */
.body, .text-body {
  font-size: var(--text-base);
  line-height: 1.65;
  color: var(--foreground);
}

/* Secondary body text */
.body-secondary, .text-secondary {
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--foreground-muted);
}

/* Small supporting text */
.supporting, .text-supporting {
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--foreground-muted);
}
```

### Caption and Label Styling

```css
/* Captions - below images/figures */
.caption {
  font-size: var(--text-sm);
  font-style: italic;
  color: var(--foreground-muted);
  line-height: 1.4;
  margin-top: var(--space-2);
}

/* Labels - form fields, metadata */
.label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--foreground);
  letter-spacing: 0.01em;
}

/* Meta labels - timestamps, status */
.meta {
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--foreground-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Eyebrow text - above headings */
.eyebrow {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: var(--space-2);
}
```

### Code and Monospace Treatments

```css
/* Inline code */
code:not([class*="language-"]) {
  font-family: var(--font-mono);
  font-size: 0.9em;
  font-weight: 500;
  padding: 0.15em 0.4em;
  background: var(--background-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--primary);
}

/* Code blocks */
pre {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.7;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  overflow-x: auto;
  tab-size: 2;
}

/* Keyboard shortcuts */
kbd {
  font-family: var(--font-mono);
  font-size: 0.85em;
  font-weight: 500;
  padding: 0.2em 0.5em;
  background: linear-gradient(180deg, var(--surface) 0%, var(--background-subtle) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  box-shadow: 0 2px 0 var(--border);
}

/* Timestamps */
.timestamp, time {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}
```

---

## 5. Text Effects

### Gradient Fills

```css
/* Primary brand gradient */
.text-gradient-primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Warm gradient */
.text-gradient-warm {
  background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Cool gradient */
.text-gradient-cool {
  background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Metallic gradient */
.text-gradient-metallic {
  background: linear-gradient(
    135deg,
    #c0c0c0 0%,
    #f5f5f5 25%,
    #c0c0c0 50%,
    #a0a0a0 75%,
    #c0c0c0 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Rainbow gradient */
.text-gradient-rainbow {
  background: linear-gradient(
    90deg,
    #ef4444, #f59e0b, #22c55e, #06b6d4, #8b5cf6, #ec4899
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: rainbowShift 5s linear infinite;
}

@keyframes rainbowShift {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}
```

### Text Shadows for Depth

```css
/* Subtle shadow for headlines */
.text-shadow-subtle {
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Deep shadow for contrast */
.text-shadow-deep {
  text-shadow:
    0 2px 4px rgba(0, 0, 0, 0.15),
    0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 3D emboss effect */
.text-shadow-emboss {
  text-shadow:
    0 1px 0 rgba(255, 255, 255, 0.4),
    0 -1px 0 rgba(0, 0, 0, 0.2);
}

/* Letterpress / inset effect */
.text-shadow-letterpress {
  color: transparent;
  text-shadow:
    0 1px 1px rgba(255, 255, 255, 0.3),
    0 -1px 1px rgba(0, 0, 0, 0.3);
  background: var(--foreground);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Long shadow */
.text-shadow-long {
  text-shadow:
    1px 1px rgba(0, 0, 0, 0.1),
    2px 2px rgba(0, 0, 0, 0.09),
    3px 3px rgba(0, 0, 0, 0.08),
    4px 4px rgba(0, 0, 0, 0.07),
    5px 5px rgba(0, 0, 0, 0.06),
    6px 6px rgba(0, 0, 0, 0.05);
}
```

### Glow Effects for Emphasis

```css
/* Primary glow */
.text-glow-primary {
  text-shadow:
    0 0 10px rgba(6, 182, 212, 0.5),
    0 0 20px rgba(6, 182, 212, 0.3),
    0 0 40px rgba(6, 182, 212, 0.2);
}

/* Accent glow */
.text-glow-accent {
  text-shadow:
    0 0 10px rgba(139, 92, 246, 0.5),
    0 0 20px rgba(139, 92, 246, 0.3),
    0 0 40px rgba(139, 92, 246, 0.2);
}

/* Pulsing glow */
.text-glow-pulse {
  animation: textGlowPulse 2s ease-in-out infinite;
}

@keyframes textGlowPulse {
  0%, 100% {
    text-shadow:
      0 0 5px rgba(6, 182, 212, 0.4),
      0 0 10px rgba(6, 182, 212, 0.2);
  }
  50% {
    text-shadow:
      0 0 15px rgba(6, 182, 212, 0.6),
      0 0 30px rgba(6, 182, 212, 0.4),
      0 0 45px rgba(6, 182, 212, 0.2);
  }
}

/* Neon glow (dark mode) */
.dark .text-glow-neon {
  color: #fff;
  text-shadow:
    0 0 5px var(--primary),
    0 0 10px var(--primary),
    0 0 20px var(--primary),
    0 0 40px var(--primary),
    0 0 80px var(--primary);
}
```

### Stroke and Outline Variations

```css
/* Text outline */
.text-outline {
  -webkit-text-stroke: 1px var(--foreground);
  color: transparent;
}

/* Text outline with fill on hover */
.text-outline-hover {
  -webkit-text-stroke: 1px var(--foreground);
  color: transparent;
  transition: color 0.3s var(--ease-out);
}

.text-outline-hover:hover {
  color: var(--foreground);
}

/* Thick outline for display text */
.text-outline-thick {
  -webkit-text-stroke: 2px var(--primary);
  color: transparent;
}

/* Double stroke effect */
.text-double-stroke {
  -webkit-text-stroke: 1px var(--foreground);
  color: transparent;
  text-shadow:
    2px 2px 0 var(--primary),
    -2px -2px 0 var(--primary);
}
```

### Background Clip Techniques

```css
/* Pattern fill */
.text-pattern-dots {
  background:
    radial-gradient(circle, var(--primary) 1px, transparent 1px);
  background-size: 4px 4px;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Diagonal stripes */
.text-pattern-stripes {
  background: repeating-linear-gradient(
    45deg,
    var(--primary),
    var(--primary) 2px,
    var(--accent) 2px,
    var(--accent) 4px
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

---

## 6. Reading Experience

### Optimal Line Lengths

```css
/* Prose content containers */
.prose {
  max-width: 65ch; /* Optimal reading width */
  margin-inline: auto;
}

/* Narrow prose for dense text */
.prose-narrow {
  max-width: 55ch;
}

/* Wide prose for lighter content */
.prose-wide {
  max-width: 75ch;
}

/* Full-width for UI elements */
.prose-full {
  max-width: 100%;
}

/* Card descriptions */
.card-description,
.feature-description {
  max-width: 45ch;
}

/* Hero subtitle */
.hero-subtitle {
  max-width: 50ch;
}
```

### Leading Adjustments by Context

```css
/* Tight leading for headlines */
.leading-headline {
  line-height: 1.1;
}

/* Standard leading for body */
.leading-body {
  line-height: 1.65;
}

/* Relaxed leading for long-form reading */
.leading-relaxed {
  line-height: 1.8;
}

/* Loose leading for large text */
.leading-loose {
  line-height: 2;
}

/* Dynamic leading based on font size */
.dynamic-leading {
  line-height: calc(1em + 0.5rem);
}
```

### Paragraph Spacing

```css
/* Standard paragraph spacing */
.prose p + p {
  margin-top: 1.5em;
}

/* Tight paragraph spacing */
.prose-tight p + p {
  margin-top: 1em;
}

/* Relaxed paragraph spacing */
.prose-relaxed p + p {
  margin-top: 2em;
}

/* Drop cap for article openings */
.prose-dropcap > p:first-of-type::first-letter {
  float: left;
  font-size: 4em;
  line-height: 0.8;
  padding-right: 0.1em;
  font-weight: 700;
  color: var(--primary);
}
```

### First-Line Styling

```css
/* First-line emphasis */
.prose-firstline > p:first-of-type::first-line {
  font-variant: small-caps;
  font-weight: 600;
  letter-spacing: 0.05em;
}

/* Hanging punctuation for quotes */
.prose-hanging {
  hanging-punctuation: first last;
}

/* Balanced text wrapping */
.text-balanced {
  text-wrap: balance;
}

/* Pretty text wrapping (avoid orphans) */
.text-pretty {
  text-wrap: pretty;
}
```

---

## 7. Implementation Priority

### Phase 1: Foundation (Week 1)
1. Implement fluid type scale with clamp()
2. Add variable font support
3. Update heading hierarchy

### Phase 2: Enhancement (Week 2)
1. Add gradient text effects
2. Implement text glow effects
3. Add weight animations on hover

### Phase 3: Kinetic (Week 3)
1. Letter-by-letter reveal for hero
2. Typewriter effect for search
3. Gradient text animations

### Phase 4: Polish (Week 4)
1. Optimize reading experience
2. Add reduced-motion alternatives
3. Performance testing

---

## 8. Accessibility Considerations

```css
/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .text-reveal span,
  .typewriter,
  .gradient-text-animated,
  .text-glow-pulse,
  .text-gradient-rainbow {
    animation: none !important;
    transition: none !important;
  }

  /* Static fallbacks */
  .typewriter {
    width: 100%;
    border-right: none;
  }

  .text-reveal span {
    opacity: 1;
    transform: none;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .text-gradient-primary,
  .text-gradient-cool,
  .text-gradient-warm {
    background: none;
    -webkit-text-fill-color: currentColor;
    color: var(--foreground);
  }

  .text-glow-primary,
  .text-glow-accent {
    text-shadow: none;
  }
}

/* Forced colors mode */
@media (forced-colors: active) {
  .text-gradient-primary,
  .text-outline {
    background: none;
    -webkit-text-stroke: none;
    color: CanvasText;
  }
}
```

---

## 9. Font Loading Strategy

### HTML Preload

```html
<!-- Preload critical fonts -->
<link rel="preload"
      href="/fonts/Inter-Variable.woff2"
      as="font"
      type="font/woff2"
      crossorigin>
```

### CSS Font-Face with Swap

```css
@font-face {
  font-family: 'Inter Variable';
  src: url('/fonts/Inter-Variable.woff2') format('woff2');
  font-weight: 100 900;
  font-display: swap;
}

body {
  font-family: 'Inter Variable', ui-sans-serif, system-ui, sans-serif;
}
```

### Progressive Enhancement

```css
/* Fallback before fonts load */
.hero-title {
  font-weight: 700; /* System font fallback */
}

/* Enhanced styles after fonts load */
.fonts-loaded .hero-title {
  font-variation-settings: 'wght' 800;
}
```

---

## 10. Recommended Font Stack

### Production Fonts

| Use Case | Font | Weights | Notes |
|----------|------|---------|-------|
| Display/Hero | Cabinet Grotesk Variable | 100-900 | Bold geometric for headlines |
| UI/Body | Inter Variable | 100-900 | Excellent x-height, legibility |
| Monospace | JetBrains Mono | 400-700 | Ligatures, clear characters |
| Alternative Display | Satoshi Variable | 300-900 | Modern, slightly playful |

### Self-Hosted vs CDN

For production:
- Self-host fonts for performance and privacy
- Use `font-display: swap` for fast first render
- Subset fonts to reduce file size
- Use WOFF2 format exclusively (best compression)

---

*This typography plan transforms Lecture Mind from a functional interface into an award-winning text experience that delights users while maintaining accessibility and performance.*
