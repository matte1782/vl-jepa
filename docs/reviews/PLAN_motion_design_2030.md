# Advanced Motion Design Plan - Award-Winning Animations

> **Version**: 2030 Edition
> **Target**: Award-winning web animations with performance-first approach
> **Framework**: Physics-based, choreographed, GPU-accelerated

---

## Current State Analysis

### Existing Animation Implementation

**animations.css** (902 lines):
- Noise texture overlay with SVG filter
- Floating particles with CSS keyframes
- Aurora gradient blobs with blur effects
- Light beams with opacity transitions
- Parallax layers (JS-driven)
- Glow rings and morphing backgrounds
- 3D card tilt effects
- Button ripple effects
- Cursor glow trail
- Magnetic button effects
- Scroll-linked animations (CSS animation-timeline)
- Stagger reveals
- Liquid gradient effects

**app.js** Animation Functions:
- `initAnimatedCounters()` - Counter animations with IntersectionObserver
- `initTypewriter()` - Character-by-character reveal
- `initInteractiveParticles()` - RAF-throttled cursor interaction
- `initCardTilt()` - 3D perspective transforms
- `initButtonRipple()` - Material-style ripples
- `initCursorGlow()` - Smooth cursor follower
- `initMagneticButtons()` - Hover attraction effect
- `initSectionTransitions()` - Scroll-triggered color shifts
- `initVisibilityHandler()` - Tab visibility optimization
- `initParallax()` - Hero section parallax

**components.css** (2205 lines):
- Base component transitions
- Modal animations (fadeIn, scaleIn)
- Study card stagger animations
- Flashcard 3D flip
- Various micro-interactions

### Identified Gaps for Award-Winning Motion

1. **No true spring physics** - Using cubic-bezier approximations
2. **Limited gesture support** - No drag/swipe physics
3. **No orchestrated sequences** - Individual animations, not choreographed
4. **Basic ambient motion** - Particles don't feel "alive"
5. **No inertial scrolling** - Standard browser behavior
6. **Missing follow-through** - Animations end abruptly

---

## Part 1: Physics-Based Animation Engine

### 1.1 Spring Dynamics System

```javascript
// motion-engine.js - Core Physics Engine

/**
 * Spring Physics Calculator
 * Based on damped harmonic oscillator: F = -kx - cv
 */
class SpringPhysics {
  constructor(config = {}) {
    // Spring presets (inspired by Apple's Motion guidelines)
    this.presets = {
      gentle: { tension: 120, friction: 14, mass: 1 },
      bouncy: { tension: 300, friction: 10, mass: 1 },
      snappy: { tension: 400, friction: 28, mass: 1 },
      stiff: { tension: 500, friction: 35, mass: 1 },
      slow: { tension: 90, friction: 20, mass: 1 },
      molasses: { tension: 50, friction: 30, mass: 1 },
    };

    this.tension = config.tension ?? 170;
    this.friction = config.friction ?? 26;
    this.mass = config.mass ?? 1;
    this.precision = config.precision ?? 0.01;

    this.velocity = 0;
    this.current = config.from ?? 0;
    this.target = config.to ?? 1;
  }

  /**
   * RK4 Integration for accurate spring simulation
   */
  step(dt) {
    const acceleration = (position, velocity) => {
      const springForce = -this.tension * (position - this.target);
      const dampingForce = -this.friction * velocity;
      return (springForce + dampingForce) / this.mass;
    };

    // Runge-Kutta 4th order integration
    const k1v = acceleration(this.current, this.velocity);
    const k1x = this.velocity;

    const k2v = acceleration(this.current + k1x * dt/2, this.velocity + k1v * dt/2);
    const k2x = this.velocity + k1v * dt/2;

    const k3v = acceleration(this.current + k2x * dt/2, this.velocity + k2v * dt/2);
    const k3x = this.velocity + k2v * dt/2;

    const k4v = acceleration(this.current + k3x * dt, this.velocity + k3v * dt);
    const k4x = this.velocity + k3v * dt;

    this.velocity += (k1v + 2*k2v + 2*k3v + k4v) * dt / 6;
    this.current += (k1x + 2*k2x + 2*k3x + k4x) * dt / 6;

    return this.current;
  }

  isAtRest() {
    return (
      Math.abs(this.velocity) < this.precision &&
      Math.abs(this.current - this.target) < this.precision
    );
  }

  setTarget(target) {
    this.target = target;
  }

  applyPreset(name) {
    const preset = this.presets[name];
    if (preset) {
      Object.assign(this, preset);
    }
    return this;
  }
}

/**
 * 2D Spring for position animations
 */
class Spring2D {
  constructor(config = {}) {
    this.x = new SpringPhysics({ ...config, from: config.fromX ?? 0, to: config.toX ?? 0 });
    this.y = new SpringPhysics({ ...config, from: config.fromY ?? 0, to: config.toY ?? 0 });
  }

  step(dt) {
    return {
      x: this.x.step(dt),
      y: this.y.step(dt)
    };
  }

  setTarget(x, y) {
    this.x.setTarget(x);
    this.y.setTarget(y);
  }

  isAtRest() {
    return this.x.isAtRest() && this.y.isAtRest();
  }
}

/**
 * Animation Loop Manager - RAF-optimized
 */
class AnimationLoop {
  constructor() {
    this.animations = new Map();
    this.lastTime = 0;
    this.isRunning = false;
    this.rafId = null;
  }

  add(id, animation) {
    this.animations.set(id, animation);
    if (!this.isRunning) this.start();
  }

  remove(id) {
    this.animations.delete(id);
    if (this.animations.size === 0) this.stop();
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;
    this.lastTime = performance.now();
    this.tick();
  }

  stop() {
    this.isRunning = false;
    if (this.rafId) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  tick() {
    if (!this.isRunning) return;

    const now = performance.now();
    const dt = Math.min((now - this.lastTime) / 1000, 0.064); // Cap at ~15fps for stability
    this.lastTime = now;

    for (const [id, anim] of this.animations) {
      const shouldRemove = anim.update(dt);
      if (shouldRemove) this.remove(id);
    }

    this.rafId = requestAnimationFrame(() => this.tick());
  }
}

// Global animation loop singleton
const animationLoop = new AnimationLoop();

export { SpringPhysics, Spring2D, AnimationLoop, animationLoop };
```

### 1.2 Inertial Scrolling with Momentum

```javascript
// inertial-scroll.js

/**
 * Inertial scroll with elastic bounds and momentum
 */
class InertialScroller {
  constructor(element, options = {}) {
    this.element = element;
    this.bounds = options.bounds ?? { min: 0, max: 1000 };
    this.friction = options.friction ?? 0.95;
    this.elasticity = options.elasticity ?? 0.1;
    this.maxOverscroll = options.maxOverscroll ?? 100;

    this.position = 0;
    this.velocity = 0;
    this.isDragging = false;
    this.lastY = 0;
    this.lastTime = 0;
    this.velocityHistory = [];

    this.spring = new SpringPhysics({
      tension: 170,
      friction: 26,
      from: 0,
      to: 0
    });

    this.bindEvents();
  }

  bindEvents() {
    // Touch events
    this.element.addEventListener('touchstart', this.onDragStart.bind(this), { passive: false });
    this.element.addEventListener('touchmove', this.onDragMove.bind(this), { passive: false });
    this.element.addEventListener('touchend', this.onDragEnd.bind(this), { passive: false });

    // Mouse events for desktop
    this.element.addEventListener('mousedown', this.onDragStart.bind(this));
    window.addEventListener('mousemove', this.onDragMove.bind(this));
    window.addEventListener('mouseup', this.onDragEnd.bind(this));
  }

  onDragStart(e) {
    this.isDragging = true;
    this.lastY = this.getY(e);
    this.lastTime = performance.now();
    this.velocityHistory = [];
    this.velocity = 0;

    // Cancel any ongoing momentum
    animationLoop.remove('inertial-scroll-' + this.element.id);
  }

  onDragMove(e) {
    if (!this.isDragging) return;
    e.preventDefault();

    const y = this.getY(e);
    const now = performance.now();
    const dt = now - this.lastTime;
    const dy = y - this.lastY;

    // Track velocity for momentum calculation
    if (dt > 0) {
      this.velocityHistory.push({ v: dy / dt * 1000, t: now });
      // Keep only last 100ms of velocity data
      this.velocityHistory = this.velocityHistory.filter(v => now - v.t < 100);
    }

    // Apply elastic resistance at bounds
    let newPosition = this.position + dy;

    if (newPosition < this.bounds.min) {
      const overscroll = this.bounds.min - newPosition;
      const resistance = 1 - (overscroll / (overscroll + this.maxOverscroll));
      newPosition = this.bounds.min - overscroll * resistance * this.elasticity;
    } else if (newPosition > this.bounds.max) {
      const overscroll = newPosition - this.bounds.max;
      const resistance = 1 - (overscroll / (overscroll + this.maxOverscroll));
      newPosition = this.bounds.max + overscroll * resistance * this.elasticity;
    }

    this.position = newPosition;
    this.applyPosition();

    this.lastY = y;
    this.lastTime = now;
  }

  onDragEnd(e) {
    if (!this.isDragging) return;
    this.isDragging = false;

    // Calculate release velocity from history
    if (this.velocityHistory.length > 0) {
      this.velocity = this.velocityHistory.reduce((sum, v) => sum + v.v, 0) /
                      this.velocityHistory.length;
    }

    // Start momentum animation
    this.startMomentum();
  }

  startMomentum() {
    const id = 'inertial-scroll-' + this.element.id;

    animationLoop.add(id, {
      update: (dt) => {
        // Check if we're outside bounds - use spring physics to return
        if (this.position < this.bounds.min || this.position > this.bounds.max) {
          this.spring.current = this.position;
          this.spring.velocity = this.velocity;
          this.spring.target = this.position < this.bounds.min ?
                               this.bounds.min : this.bounds.max;

          this.position = this.spring.step(dt);
          this.velocity = this.spring.velocity;

          this.applyPosition();
          return this.spring.isAtRest();
        }

        // Normal momentum with friction
        this.velocity *= Math.pow(this.friction, dt * 60);
        this.position += this.velocity * dt;

        this.applyPosition();

        // Stop when velocity is negligible
        return Math.abs(this.velocity) < 0.5;
      }
    });
  }

  getY(e) {
    return e.touches ? e.touches[0].clientY : e.clientY;
  }

  applyPosition() {
    this.element.style.transform = `translate3d(0, ${-this.position}px, 0)`;
  }
}

export { InertialScroller };
```

### 1.3 Natural Decay Curves

```javascript
// decay-curves.js

/**
 * Exponential decay for natural feeling animations
 */
function exponentialDecay(value, target, lambda, dt) {
  return target + (value - target) * Math.exp(-lambda * dt);
}

/**
 * Critically damped spring (no oscillation)
 */
function criticalDamp(current, target, velocity, omega, dt) {
  const x0 = current - target;
  const newX = (x0 + (velocity + omega * x0) * dt) * Math.exp(-omega * dt);
  const newV = (velocity - omega * omega * x0 * dt) * Math.exp(-omega * dt);

  return {
    value: target + newX,
    velocity: newV
  };
}

/**
 * Friction-based deceleration for flings/swipes
 */
function frictionDeceleration(velocity, friction, dt) {
  const sign = Math.sign(velocity);
  const absVel = Math.abs(velocity);
  const newVel = Math.max(0, absVel - friction * dt);
  return sign * newVel;
}

export { exponentialDecay, criticalDamp, frictionDeceleration };
```

---

## Part 2: Choreographed Sequences

### 2.1 Orchestration Engine

```javascript
// choreographer.js

/**
 * Timeline-based animation orchestration
 * Inspired by GSAP but lightweight and physics-aware
 */
class Choreographer {
  constructor() {
    this.sequences = new Map();
    this.globalTimeline = 0;
  }

  /**
   * Create a choreographed sequence
   */
  sequence(name, config = {}) {
    const seq = new AnimationSequence(config);
    this.sequences.set(name, seq);
    return seq;
  }

  play(name) {
    const seq = this.sequences.get(name);
    if (seq) seq.play();
  }

  pause(name) {
    const seq = this.sequences.get(name);
    if (seq) seq.pause();
  }
}

class AnimationSequence {
  constructor(config = {}) {
    this.tracks = [];
    this.duration = 0;
    this.currentTime = 0;
    this.isPlaying = false;
    this.loop = config.loop ?? false;
    this.onComplete = config.onComplete ?? null;

    // Golden ratio timing for natural stagger
    this.goldenRatio = 1.618033988749;
  }

  /**
   * Add animation track with timing
   */
  add(target, properties, timing = {}) {
    const track = {
      target: typeof target === 'string' ? document.querySelector(target) : target,
      properties,
      start: timing.start ?? this.duration,
      duration: timing.duration ?? 400,
      easing: timing.easing ?? 'spring',
      springConfig: timing.springConfig ?? { tension: 170, friction: 26 }
    };

    this.tracks.push(track);
    this.duration = Math.max(this.duration, track.start + track.duration);

    return this;
  }

  /**
   * Add staggered animations with golden ratio timing
   */
  stagger(selector, properties, timing = {}) {
    const elements = document.querySelectorAll(selector);
    const staggerDelay = timing.staggerDelay ?? 50;
    const staggerType = timing.staggerType ?? 'golden';

    elements.forEach((el, i) => {
      let delay;

      switch (staggerType) {
        case 'golden':
          // Golden ratio spiral delay
          delay = staggerDelay * Math.pow(this.goldenRatio, i * 0.3);
          break;
        case 'linear':
          delay = staggerDelay * i;
          break;
        case 'ease-in':
          delay = staggerDelay * Math.pow(i / elements.length, 2) * elements.length;
          break;
        case 'ease-out':
          delay = staggerDelay * (1 - Math.pow(1 - i / elements.length, 2)) * elements.length;
          break;
        case 'center-out':
          const center = elements.length / 2;
          delay = staggerDelay * Math.abs(i - center);
          break;
        default:
          delay = staggerDelay * i;
      }

      this.add(el, properties, {
        ...timing,
        start: (timing.start ?? this.duration) + delay
      });
    });

    return this;
  }

  /**
   * Anticipation: Small opposite movement before main action
   */
  withAnticipation(target, properties, config = {}) {
    const anticipationAmount = config.anticipationAmount ?? 0.1;
    const anticipationDuration = config.anticipationDuration ?? 100;
    const mainDuration = config.duration ?? 400;

    // Create anticipation properties (opposite direction)
    const anticipationProps = {};
    for (const [key, value] of Object.entries(properties)) {
      if (typeof value === 'number') {
        anticipationProps[key] = value * -anticipationAmount;
      }
    }

    // Anticipation phase
    this.add(target, anticipationProps, {
      start: config.start ?? this.duration,
      duration: anticipationDuration,
      easing: 'easeOut'
    });

    // Main action
    this.add(target, properties, {
      start: (config.start ?? 0) + anticipationDuration,
      duration: mainDuration,
      springConfig: config.springConfig ?? { tension: 300, friction: 20 }
    });

    return this;
  }

  /**
   * Follow-through: Continuation past target then settle
   */
  withFollowThrough(target, properties, config = {}) {
    const overshootAmount = config.overshootAmount ?? 0.15;
    const settleDuration = config.settleDuration ?? 200;
    const mainDuration = config.duration ?? 400;

    // Use bouncy spring for natural overshoot
    this.add(target, properties, {
      start: config.start ?? this.duration,
      duration: mainDuration + settleDuration,
      springConfig: { tension: 200, friction: 12 } // Low friction = more overshoot
    });

    return this;
  }

  /**
   * Squash and stretch for organic feel
   */
  squashAndStretch(target, config = {}) {
    const intensity = config.intensity ?? 0.2;
    const duration = config.duration ?? 300;

    // Squash phase (compress on impact)
    this.add(target, {
      scaleX: 1 + intensity,
      scaleY: 1 - intensity
    }, {
      start: config.start ?? this.duration,
      duration: duration * 0.3,
      easing: 'easeOut'
    });

    // Stretch phase (elongate on release)
    this.add(target, {
      scaleX: 1 - intensity * 0.5,
      scaleY: 1 + intensity * 0.5
    }, {
      start: (config.start ?? 0) + duration * 0.3,
      duration: duration * 0.3,
      easing: 'easeOut'
    });

    // Settle phase
    this.add(target, {
      scaleX: 1,
      scaleY: 1
    }, {
      start: (config.start ?? 0) + duration * 0.6,
      duration: duration * 0.4,
      springConfig: { tension: 400, friction: 30 }
    });

    return this;
  }

  play() {
    if (this.isPlaying) return;
    this.isPlaying = true;
    this.currentTime = 0;

    // Initialize all tracks
    this.tracks.forEach(track => {
      track.spring = new SpringPhysics({
        ...track.springConfig,
        from: 0,
        to: 1
      });
      track.initialValues = {};
      track.targetValues = {};

      // Store initial values
      const computed = getComputedStyle(track.target);
      for (const prop of Object.keys(track.properties)) {
        track.initialValues[prop] = parseFloat(computed[prop]) || 0;
        track.targetValues[prop] = track.properties[prop];
      }
    });

    animationLoop.add('sequence-' + Date.now(), {
      update: (dt) => {
        this.currentTime += dt * 1000;

        let allComplete = true;

        this.tracks.forEach(track => {
          if (this.currentTime < track.start) {
            allComplete = false;
            return;
          }

          const elapsed = this.currentTime - track.start;
          const progress = Math.min(1, elapsed / track.duration);

          if (progress < 1) allComplete = false;

          // Use spring physics for interpolation
          const springProgress = track.spring.step(dt);

          // Apply properties
          for (const [prop, targetValue] of Object.entries(track.targetValues)) {
            const initial = track.initialValues[prop];
            const value = initial + (targetValue - initial) * springProgress;
            track.target.style[prop] = typeof targetValue === 'number' ?
                                        `${value}px` : value;
          }
        });

        if (allComplete) {
          this.isPlaying = false;
          if (this.loop) {
            this.play();
          } else if (this.onComplete) {
            this.onComplete();
          }
          return true;
        }

        return false;
      }
    });
  }

  pause() {
    this.isPlaying = false;
  }
}

const choreographer = new Choreographer();
export { Choreographer, AnimationSequence, choreographer };
```

---

## Part 3: Interactive Motion

### 3.1 Cursor-Responsive Deformations

```javascript
// cursor-effects.js

/**
 * Fluid cursor deformation for elements
 */
class CursorDeformer {
  constructor(element, options = {}) {
    this.element = element;
    this.intensity = options.intensity ?? 0.1;
    this.spring = new Spring2D({
      tension: 150,
      friction: 15
    });

    this.isHovering = false;
    this.center = { x: 0, y: 0 };
    this.rect = null;

    this.bindEvents();
  }

  bindEvents() {
    this.element.addEventListener('mouseenter', () => {
      this.isHovering = true;
      this.updateRect();
    });

    this.element.addEventListener('mousemove', (e) => {
      if (!this.isHovering) return;

      const x = (e.clientX - this.center.x) * this.intensity;
      const y = (e.clientY - this.center.y) * this.intensity;

      this.spring.setTarget(x, y);
    });

    this.element.addEventListener('mouseleave', () => {
      this.isHovering = false;
      this.spring.setTarget(0, 0);
    });

    // Add to animation loop
    animationLoop.add('deformer-' + Date.now(), {
      update: (dt) => {
        const pos = this.spring.step(dt);

        // Apply skew deformation based on cursor offset
        const skewX = pos.x * 0.5;
        const skewY = pos.y * 0.5;

        this.element.style.transform = `
          translate(${pos.x}px, ${pos.y}px)
          skew(${skewX}deg, ${skewY}deg)
        `;

        return false; // Never remove
      }
    });
  }

  updateRect() {
    this.rect = this.element.getBoundingClientRect();
    this.center = {
      x: this.rect.left + this.rect.width / 2,
      y: this.rect.top + this.rect.height / 2
    };
  }
}

/**
 * Magnetic attraction effect
 */
class MagneticElement {
  constructor(element, options = {}) {
    this.element = element;
    this.radius = options.radius ?? 100;
    this.strength = options.strength ?? 0.3;
    this.spring = new Spring2D({
      tension: 300,
      friction: 20
    });

    this.center = { x: 0, y: 0 };
    this.isActive = false;

    this.bindEvents();
  }

  bindEvents() {
    document.addEventListener('mousemove', (e) => {
      this.updateCenter();

      const dx = e.clientX - this.center.x;
      const dy = e.clientY - this.center.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < this.radius) {
        this.isActive = true;
        // Magnetic pull increases as cursor gets closer
        const force = (1 - distance / this.radius) * this.strength;
        this.spring.setTarget(dx * force, dy * force);
      } else if (this.isActive) {
        this.isActive = false;
        this.spring.setTarget(0, 0);
      }
    });

    animationLoop.add('magnetic-' + Date.now(), {
      update: (dt) => {
        const pos = this.spring.step(dt);
        this.element.style.transform = `translate(${pos.x}px, ${pos.y}px)`;
        return false;
      }
    });
  }

  updateCenter() {
    const rect = this.element.getBoundingClientRect();
    this.center = {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    };
  }
}

export { CursorDeformer, MagneticElement };
```

### 3.2 Fluid Drag Interactions

```javascript
// drag-physics.js

/**
 * Physics-based draggable elements
 */
class DraggablePhysics {
  constructor(element, options = {}) {
    this.element = element;
    this.bounds = options.bounds ?? null;
    this.snapPoints = options.snapPoints ?? [];
    this.snapThreshold = options.snapThreshold ?? 50;
    this.throwMultiplier = options.throwMultiplier ?? 1;

    this.spring = new Spring2D({
      tension: 200,
      friction: 25
    });

    this.position = { x: 0, y: 0 };
    this.velocity = { x: 0, y: 0 };
    this.isDragging = false;
    this.velocityHistory = [];

    this.bindEvents();
  }

  bindEvents() {
    this.element.addEventListener('pointerdown', this.onDragStart.bind(this));
    document.addEventListener('pointermove', this.onDragMove.bind(this));
    document.addEventListener('pointerup', this.onDragEnd.bind(this));

    // Start animation loop
    animationLoop.add('draggable-' + Date.now(), {
      update: (dt) => {
        if (this.isDragging) return false;

        const pos = this.spring.step(dt);
        this.position = { x: pos.x, y: pos.y };
        this.applyPosition();

        return false;
      }
    });
  }

  onDragStart(e) {
    e.preventDefault();
    this.isDragging = true;
    this.element.setPointerCapture(e.pointerId);
    this.element.style.cursor = 'grabbing';
    this.velocityHistory = [];

    // Add will-change for performance
    this.element.style.willChange = 'transform';
  }

  onDragMove(e) {
    if (!this.isDragging) return;

    const now = performance.now();
    const newPos = {
      x: this.position.x + e.movementX,
      y: this.position.y + e.movementY
    };

    // Track velocity
    this.velocityHistory.push({
      vx: e.movementX,
      vy: e.movementY,
      t: now
    });
    this.velocityHistory = this.velocityHistory.filter(v => now - v.t < 100);

    // Apply bounds with elastic resistance
    if (this.bounds) {
      newPos.x = this.elasticBound(newPos.x, this.bounds.left, this.bounds.right);
      newPos.y = this.elasticBound(newPos.y, this.bounds.top, this.bounds.bottom);
    }

    this.position = newPos;
    this.spring.x.current = newPos.x;
    this.spring.y.current = newPos.y;
    this.applyPosition();
  }

  onDragEnd(e) {
    if (!this.isDragging) return;
    this.isDragging = false;
    this.element.releasePointerCapture(e.pointerId);
    this.element.style.cursor = 'grab';

    // Calculate throw velocity
    if (this.velocityHistory.length > 0) {
      const avgVx = this.velocityHistory.reduce((sum, v) => sum + v.vx, 0) / this.velocityHistory.length;
      const avgVy = this.velocityHistory.reduce((sum, v) => sum + v.vy, 0) / this.velocityHistory.length;

      // Apply throw
      this.spring.x.velocity = avgVx * 60 * this.throwMultiplier;
      this.spring.y.velocity = avgVy * 60 * this.throwMultiplier;
    }

    // Check for snap points
    const nearestSnap = this.findNearestSnapPoint();
    if (nearestSnap) {
      this.spring.setTarget(nearestSnap.x, nearestSnap.y);
    } else {
      // Settle in place
      this.spring.setTarget(this.position.x, this.position.y);
    }

    // Remove will-change after settling
    setTimeout(() => {
      this.element.style.willChange = 'auto';
    }, 500);
  }

  elasticBound(value, min, max) {
    if (value < min) {
      const over = min - value;
      return min - over * 0.2;
    }
    if (value > max) {
      const over = value - max;
      return max + over * 0.2;
    }
    return value;
  }

  findNearestSnapPoint() {
    let nearest = null;
    let minDistance = this.snapThreshold;

    for (const point of this.snapPoints) {
      const dx = point.x - this.position.x;
      const dy = point.y - this.position.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < minDistance) {
        minDistance = distance;
        nearest = point;
      }
    }

    return nearest;
  }

  applyPosition() {
    this.element.style.transform = `translate3d(${this.position.x}px, ${this.position.y}px, 0)`;
  }
}

export { DraggablePhysics };
```

### 3.3 Gesture-Driven Animations

```javascript
// gesture-animations.js

/**
 * Swipe gesture with physics
 */
class SwipeGesture {
  constructor(element, options = {}) {
    this.element = element;
    this.direction = options.direction ?? 'horizontal'; // or 'vertical'
    this.threshold = options.threshold ?? 50;
    this.velocityThreshold = options.velocityThreshold ?? 0.5;
    this.onSwipe = options.onSwipe ?? (() => {});

    this.spring = new SpringPhysics({
      tension: 300,
      friction: 25
    });

    this.startPos = 0;
    this.currentPos = 0;
    this.startTime = 0;

    this.bindEvents();
  }

  bindEvents() {
    this.element.addEventListener('touchstart', this.onStart.bind(this), { passive: true });
    this.element.addEventListener('touchmove', this.onMove.bind(this), { passive: false });
    this.element.addEventListener('touchend', this.onEnd.bind(this), { passive: true });
  }

  onStart(e) {
    this.startPos = this.direction === 'horizontal' ?
                    e.touches[0].clientX : e.touches[0].clientY;
    this.currentPos = this.startPos;
    this.startTime = performance.now();

    this.element.style.willChange = 'transform';
  }

  onMove(e) {
    const pos = this.direction === 'horizontal' ?
                e.touches[0].clientX : e.touches[0].clientY;
    const delta = pos - this.startPos;

    // Apply resistance at edges
    const resistance = 1 - Math.min(Math.abs(delta) / 300, 0.8);
    const resistedDelta = delta * resistance;

    this.currentPos = pos;

    if (this.direction === 'horizontal') {
      this.element.style.transform = `translateX(${resistedDelta}px)`;
    } else {
      this.element.style.transform = `translateY(${resistedDelta}px)`;
    }

    e.preventDefault();
  }

  onEnd(e) {
    const delta = this.currentPos - this.startPos;
    const elapsed = performance.now() - this.startTime;
    const velocity = Math.abs(delta / elapsed);

    // Determine if it's a swipe
    if (Math.abs(delta) > this.threshold || velocity > this.velocityThreshold) {
      const direction = delta > 0 ?
                        (this.direction === 'horizontal' ? 'right' : 'down') :
                        (this.direction === 'horizontal' ? 'left' : 'up');

      this.animateSwipe(direction);
      this.onSwipe(direction);
    } else {
      // Snap back
      this.animateSnapBack();
    }
  }

  animateSwipe(direction) {
    const distance = direction === 'left' || direction === 'up' ? -300 : 300;

    this.spring.current = this.currentPos - this.startPos;
    this.spring.target = distance;
    this.spring.tension = 200;
    this.spring.friction = 30;

    animationLoop.add('swipe-' + Date.now(), {
      update: (dt) => {
        const pos = this.spring.step(dt);

        if (this.direction === 'horizontal') {
          this.element.style.transform = `translateX(${pos}px)`;
        } else {
          this.element.style.transform = `translateY(${pos}px)`;
        }

        return this.spring.isAtRest();
      }
    });
  }

  animateSnapBack() {
    this.spring.current = this.currentPos - this.startPos;
    this.spring.target = 0;

    animationLoop.add('snapback-' + Date.now(), {
      update: (dt) => {
        const pos = this.spring.step(dt);

        if (this.direction === 'horizontal') {
          this.element.style.transform = `translateX(${pos}px)`;
        } else {
          this.element.style.transform = `translateY(${pos}px)`;
        }

        if (this.spring.isAtRest()) {
          this.element.style.willChange = 'auto';
          return true;
        }
        return false;
      }
    });
  }
}

export { SwipeGesture };
```

---

## Part 4: Ambient Motion

### 4.1 Breathing Backgrounds

```css
/* ambient-motion.css */

/**
 * Breathing gradient backgrounds
 * Uses CSS custom properties for JS control
 */
.breathing-bg {
  --breath-phase: 0;
  --breath-intensity: 1;

  background: radial-gradient(
    ellipse at calc(30% + var(--breath-phase) * 10%) calc(40% + var(--breath-phase) * 5%),
    rgba(6, 182, 212, calc(0.15 * var(--breath-intensity))) 0%,
    transparent 50%
  ),
  radial-gradient(
    ellipse at calc(70% - var(--breath-phase) * 8%) calc(60% - var(--breath-phase) * 3%),
    rgba(139, 92, 246, calc(0.12 * var(--breath-intensity))) 0%,
    transparent 45%
  );
}

/**
 * Organic blob breathing
 */
.breathing-blob {
  --breath: 0;

  transform: scale(calc(1 + var(--breath) * 0.05));
  opacity: calc(0.6 + var(--breath) * 0.2);
  filter: blur(calc(60px + var(--breath) * 20px));
}

/**
 * Slow color shift
 */
.color-breathing {
  --hue-shift: 0;

  filter: hue-rotate(calc(var(--hue-shift) * 1deg));
}
```

```javascript
// breathing-animations.js

/**
 * Breathing animation controller
 */
class BreathingController {
  constructor(element, options = {}) {
    this.element = element;
    this.period = options.period ?? 4000; // 4 seconds per breath cycle
    this.phase = 0;

    this.start();
  }

  start() {
    animationLoop.add('breathing-' + Date.now(), {
      update: (dt) => {
        this.phase += dt * 1000;

        // Sinusoidal breathing pattern
        const breath = (Math.sin(this.phase / this.period * Math.PI * 2) + 1) / 2;

        this.element.style.setProperty('--breath-phase', breath);
        this.element.style.setProperty('--breath', breath);

        return false;
      }
    });
  }
}

export { BreathingController };
```

### 4.2 Floating Particles with Physics

```javascript
// physics-particles.js

/**
 * Particle system with realistic physics
 */
class PhysicsParticleSystem {
  constructor(container, options = {}) {
    this.container = container;
    this.count = options.count ?? 30;
    this.gravity = options.gravity ?? 0.01;
    this.wind = options.wind ?? { x: 0.001, y: 0 };
    this.turbulence = options.turbulence ?? 0.1;
    this.particles = [];

    this.init();
  }

  init() {
    const rect = this.container.getBoundingClientRect();

    for (let i = 0; i < this.count; i++) {
      const particle = this.createParticle(rect);
      this.particles.push(particle);
      this.container.appendChild(particle.element);
    }

    this.start();
  }

  createParticle(rect) {
    const el = document.createElement('div');
    el.className = 'physics-particle';

    const size = Math.random() * 4 + 2;
    el.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      background: rgba(6, 182, 212, ${Math.random() * 0.5 + 0.3});
      border-radius: 50%;
      pointer-events: none;
      will-change: transform;
    `;

    return {
      element: el,
      x: Math.random() * rect.width,
      y: Math.random() * rect.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size,
      noise: {
        x: Math.random() * 1000,
        y: Math.random() * 1000
      }
    };
  }

  /**
   * Simplex noise approximation for turbulence
   */
  noise2D(x, y) {
    const X = Math.floor(x) & 255;
    const Y = Math.floor(y) & 255;
    const xf = x - Math.floor(x);
    const yf = y - Math.floor(y);

    // Simple hash-based pseudo-noise
    const n = Math.sin(X * 12.9898 + Y * 78.233) * 43758.5453123;
    return (n - Math.floor(n)) * 2 - 1;
  }

  start() {
    const rect = this.container.getBoundingClientRect();
    let time = 0;

    animationLoop.add('particles-' + Date.now(), {
      update: (dt) => {
        time += dt;

        this.particles.forEach(p => {
          // Turbulence (Perlin-like movement)
          const turbX = this.noise2D(p.noise.x + time * 0.3, p.noise.y) * this.turbulence;
          const turbY = this.noise2D(p.noise.x, p.noise.y + time * 0.3) * this.turbulence;

          // Apply forces
          p.vx += this.wind.x + turbX;
          p.vy += -this.gravity + this.wind.y + turbY; // Negative gravity = float up

          // Friction
          p.vx *= 0.99;
          p.vy *= 0.99;

          // Update position
          p.x += p.vx;
          p.y += p.vy;

          // Wrap around bounds
          if (p.y < -10) p.y = rect.height + 10;
          if (p.y > rect.height + 10) p.y = -10;
          if (p.x < -10) p.x = rect.width + 10;
          if (p.x > rect.width + 10) p.x = -10;

          // Apply transform
          p.element.style.transform = `translate3d(${p.x}px, ${p.y}px, 0)`;
        });

        return false;
      }
    });
  }
}

export { PhysicsParticleSystem };
```

### 4.3 Morphing Shapes

```javascript
// morphing-shapes.js

/**
 * SVG path morphing with physics
 */
class MorphingShape {
  constructor(svgPath, options = {}) {
    this.path = svgPath;
    this.morphSpeed = options.morphSpeed ?? 0.5;
    this.complexity = options.complexity ?? 8;

    // Generate control points
    this.points = this.generatePoints();
    this.targetPoints = this.generatePoints();
    this.springs = this.points.map((p, i) =>
      new Spring2D({
        tension: 50 + Math.random() * 50,
        friction: 8 + Math.random() * 4,
        fromX: p.x,
        fromY: p.y,
        toX: this.targetPoints[i].x,
        toY: this.targetPoints[i].y
      })
    );

    this.morphTimer = 0;
    this.start();
  }

  generatePoints() {
    const points = [];
    const centerX = 150;
    const centerY = 150;

    for (let i = 0; i < this.complexity; i++) {
      const angle = (i / this.complexity) * Math.PI * 2;
      const radius = 80 + Math.random() * 40;

      points.push({
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius
      });
    }

    return points;
  }

  pointsToPath(points) {
    if (points.length < 3) return '';

    // Catmull-Rom spline to smooth path
    let d = `M ${points[0].x},${points[0].y}`;

    for (let i = 0; i < points.length; i++) {
      const p0 = points[(i - 1 + points.length) % points.length];
      const p1 = points[i];
      const p2 = points[(i + 1) % points.length];
      const p3 = points[(i + 2) % points.length];

      // Calculate control points
      const cp1x = p1.x + (p2.x - p0.x) / 6;
      const cp1y = p1.y + (p2.y - p0.y) / 6;
      const cp2x = p2.x - (p3.x - p1.x) / 6;
      const cp2y = p2.y - (p3.y - p1.y) / 6;

      d += ` C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`;
    }

    return d + ' Z';
  }

  start() {
    animationLoop.add('morph-' + Date.now(), {
      update: (dt) => {
        this.morphTimer += dt;

        // Generate new target points periodically
        if (this.morphTimer > 1 / this.morphSpeed) {
          this.morphTimer = 0;
          this.targetPoints = this.generatePoints();
          this.springs.forEach((spring, i) => {
            spring.setTarget(this.targetPoints[i].x, this.targetPoints[i].y);
          });
        }

        // Update springs and collect current points
        const currentPoints = this.springs.map(spring => spring.step(dt));

        // Update SVG path
        this.path.setAttribute('d', this.pointsToPath(currentPoints));

        return false;
      }
    });
  }
}

export { MorphingShape };
```

### 4.4 Noise-Based Movement

```css
/* noise-motion.css */

/**
 * CSS Custom Properties for noise-based animation
 */
.noise-animated {
  --noise-x: 0;
  --noise-y: 0;
  --noise-rotation: 0;
  --noise-scale: 1;

  transform:
    translate(
      calc(var(--noise-x) * 1px),
      calc(var(--noise-y) * 1px)
    )
    rotate(calc(var(--noise-rotation) * 1deg))
    scale(var(--noise-scale));
}

/**
 * Subtle drift animation
 */
.drift {
  --drift-x: 0;
  --drift-y: 0;

  animation: drift 10s ease-in-out infinite;
}

@keyframes drift {
  0%, 100% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(
      calc(var(--drift-x) * 15px),
      calc(var(--drift-y) * -10px)
    );
  }
  50% {
    transform: translate(
      calc(var(--drift-x) * -10px),
      calc(var(--drift-y) * 15px)
    );
  }
  75% {
    transform: translate(
      calc(var(--drift-x) * 8px),
      calc(var(--drift-y) * -5px)
    );
  }
}
```

---

## Part 5: Performance-First Implementation

### 5.1 GPU-Accelerated Transforms Only

```javascript
// performance-utils.js

/**
 * Ensure only GPU-friendly properties are animated
 */
const GPU_SAFE_PROPERTIES = new Set([
  'transform',
  'opacity',
  'filter',
  'clipPath',
  'perspective'
]);

function validateAnimationProperties(properties) {
  const warnings = [];

  for (const prop of Object.keys(properties)) {
    if (!GPU_SAFE_PROPERTIES.has(prop)) {
      warnings.push(`Warning: Animating '${prop}' may cause layout/paint. Consider using transforms instead.`);
    }
  }

  if (warnings.length > 0 && process.env.NODE_ENV === 'development') {
    console.warn('Performance warnings:', warnings);
  }
}

/**
 * Batch DOM reads and writes
 */
class DOMBatcher {
  constructor() {
    this.reads = [];
    this.writes = [];
    this.scheduled = false;
  }

  read(fn) {
    this.reads.push(fn);
    this.schedule();
  }

  write(fn) {
    this.writes.push(fn);
    this.schedule();
  }

  schedule() {
    if (this.scheduled) return;
    this.scheduled = true;

    requestAnimationFrame(() => {
      // Execute all reads first
      this.reads.forEach(fn => fn());
      this.reads = [];

      // Then all writes
      this.writes.forEach(fn => fn());
      this.writes = [];

      this.scheduled = false;
    });
  }
}

const domBatcher = new DOMBatcher();

export { validateAnimationProperties, domBatcher };
```

### 5.2 will-change Lifecycle Management

```javascript
// will-change-manager.js

/**
 * Intelligent will-change management
 */
class WillChangeManager {
  constructor() {
    this.activeElements = new Map();
    this.cleanupDelay = 500; // ms after animation ends
  }

  /**
   * Start optimizing an element for animation
   */
  prepare(element, properties = ['transform', 'opacity']) {
    // Check if element is visible
    if (!this.isElementVisible(element)) {
      return;
    }

    // Apply will-change
    element.style.willChange = properties.join(', ');

    // Track element
    this.activeElements.set(element, {
      properties,
      startTime: performance.now()
    });

    // Auto-cleanup after 10 seconds (prevent memory leaks)
    setTimeout(() => {
      if (this.activeElements.has(element)) {
        this.cleanup(element);
      }
    }, 10000);
  }

  /**
   * Clean up will-change after animation
   */
  cleanup(element, immediate = false) {
    if (!this.activeElements.has(element)) return;

    const doCleanup = () => {
      element.style.willChange = 'auto';
      this.activeElements.delete(element);
    };

    if (immediate) {
      doCleanup();
    } else {
      setTimeout(doCleanup, this.cleanupDelay);
    }
  }

  /**
   * Clean up all tracked elements
   */
  cleanupAll() {
    for (const element of this.activeElements.keys()) {
      this.cleanup(element, true);
    }
  }

  isElementVisible(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.bottom >= 0 &&
      rect.right >= 0 &&
      rect.top <= window.innerHeight &&
      rect.left <= window.innerWidth
    );
  }
}

const willChangeManager = new WillChangeManager();

// Cleanup on visibility change
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    willChangeManager.cleanupAll();
  }
});

export { willChangeManager };
```

### 5.3 Intersection Observer Triggers

```javascript
// intersection-animations.js

/**
 * Lazy animation initialization based on visibility
 */
class LazyAnimationTrigger {
  constructor(options = {}) {
    this.rootMargin = options.rootMargin ?? '50px';
    this.threshold = options.threshold ?? 0.1;
    this.animations = new Map();

    this.observer = new IntersectionObserver(
      this.handleIntersection.bind(this),
      {
        rootMargin: this.rootMargin,
        threshold: this.threshold
      }
    );
  }

  /**
   * Register element for lazy animation
   */
  register(element, animationFactory) {
    this.animations.set(element, {
      factory: animationFactory,
      instance: null,
      isActive: false
    });

    this.observer.observe(element);
  }

  /**
   * Handle visibility changes
   */
  handleIntersection(entries) {
    entries.forEach(entry => {
      const anim = this.animations.get(entry.target);
      if (!anim) return;

      if (entry.isIntersecting && !anim.isActive) {
        // Element entered viewport - start animation
        anim.instance = anim.factory(entry.target);
        anim.isActive = true;

        // Prepare will-change
        willChangeManager.prepare(entry.target);

      } else if (!entry.isIntersecting && anim.isActive) {
        // Element left viewport - pause animation
        if (anim.instance && anim.instance.pause) {
          anim.instance.pause();
        }
        anim.isActive = false;

        // Cleanup will-change
        willChangeManager.cleanup(entry.target);
      }
    });
  }

  /**
   * Unregister element
   */
  unregister(element) {
    this.observer.unobserve(element);
    this.animations.delete(element);
  }

  /**
   * Cleanup
   */
  destroy() {
    this.observer.disconnect();
    this.animations.clear();
  }
}

export { LazyAnimationTrigger };
```

### 5.4 RAF-Throttled Calculations

```javascript
// throttled-animations.js

/**
 * Throttled animation with frame budget awareness
 */
class FrameBudgetAnimator {
  constructor(options = {}) {
    this.targetFPS = options.targetFPS ?? 60;
    this.frameBudget = 1000 / this.targetFPS; // ~16.67ms for 60fps
    this.priorityQueue = [];
    this.isRunning = false;
  }

  /**
   * Add animation with priority (higher = more important)
   */
  add(id, animation, priority = 0) {
    this.priorityQueue.push({ id, animation, priority });
    this.priorityQueue.sort((a, b) => b.priority - a.priority);

    if (!this.isRunning) this.start();
  }

  start() {
    if (this.isRunning) return;
    this.isRunning = true;

    let lastTime = performance.now();

    const tick = (now) => {
      if (!this.isRunning) return;

      const dt = (now - lastTime) / 1000;
      lastTime = now;

      const frameStart = performance.now();

      // Process animations within frame budget
      for (let i = 0; i < this.priorityQueue.length; i++) {
        const elapsed = performance.now() - frameStart;

        // Skip low-priority animations if we're over budget
        if (elapsed > this.frameBudget * 0.8 && i > 0) {
          break;
        }

        const { id, animation } = this.priorityQueue[i];
        const shouldRemove = animation.update(dt);

        if (shouldRemove) {
          this.priorityQueue.splice(i, 1);
          i--;
        }
      }

      if (this.priorityQueue.length === 0) {
        this.isRunning = false;
        return;
      }

      requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  }

  stop() {
    this.isRunning = false;
  }
}

export { FrameBudgetAnimator };
```

---

## Part 6: CSS Keyframe Implementations

### 6.1 Award-Winning Entrance Animations

```css
/* entrance-animations.css */

/**
 * Cinematic fade-up with blur
 */
@keyframes cinematicReveal {
  0% {
    opacity: 0;
    transform: translateY(60px) scale(0.9);
    filter: blur(10px);
  }
  40% {
    opacity: 0.8;
    filter: blur(2px);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}

.cinematic-reveal {
  animation: cinematicReveal 1.2s var(--spring-smooth) forwards;
}

/**
 * Elastic pop-in
 */
@keyframes elasticPopIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    transform: scale(1.1);
  }
  70% {
    transform: scale(0.95);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.elastic-pop-in {
  animation: elasticPopIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

/**
 * Slide with momentum
 */
@keyframes slideWithMomentum {
  0% {
    opacity: 0;
    transform: translateX(-100px);
  }
  60% {
    opacity: 1;
    transform: translateX(15px);
  }
  80% {
    transform: translateX(-5px);
  }
  100% {
    transform: translateX(0);
  }
}

.slide-momentum {
  animation: slideWithMomentum 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

/**
 * Morphing entrance
 */
@keyframes morphEntrance {
  0% {
    opacity: 0;
    clip-path: circle(0% at 50% 50%);
    transform: scale(0.8);
  }
  50% {
    clip-path: circle(60% at 50% 50%);
    transform: scale(1.02);
  }
  100% {
    opacity: 1;
    clip-path: circle(100% at 50% 50%);
    transform: scale(1);
  }
}

.morph-entrance {
  animation: morphEntrance 0.9s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/**
 * Typewriter with glow
 */
@keyframes typewriterGlow {
  0%, 100% {
    text-shadow: 0 0 0 transparent;
  }
  50% {
    text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
  }
}

.typewriter-glow {
  animation: typewriterGlow 2s ease-in-out infinite;
}
```

### 6.2 Micro-Interactions

```css
/* micro-interactions.css */

/**
 * Button press with spring
 */
@keyframes buttonPress {
  0% { transform: scale(1); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

.btn-spring:active {
  animation: buttonPress 0.15s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/**
 * Checkbox tick
 */
@keyframes checkTick {
  0% {
    stroke-dashoffset: 24;
  }
  50% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: 0;
    transform: scale(1.1);
  }
}

.checkbox-animated path {
  stroke-dasharray: 24;
  stroke-dashoffset: 24;
}

.checkbox-animated.checked path {
  animation: checkTick 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

/**
 * Input focus glow
 */
@keyframes focusGlow {
  0% {
    box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.4);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(6, 182, 212, 0.2);
  }
  100% {
    box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.3);
  }
}

.input-animated:focus {
  animation: focusGlow 0.3s ease-out forwards;
}

/**
 * Toggle switch
 */
@keyframes toggleOn {
  0% {
    transform: translateX(0) scale(1);
  }
  30% {
    transform: translateX(10px) scale(0.9, 1.1);
  }
  60% {
    transform: translateX(22px) scale(1.1, 0.9);
  }
  100% {
    transform: translateX(20px) scale(1);
  }
}

.toggle-thumb.on {
  animation: toggleOn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

/**
 * Notification badge pulse
 */
@keyframes badgePulse {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
  }
  50% {
    transform: scale(1.15);
    box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
  }
}

.badge-pulse {
  animation: badgePulse 1.5s ease-in-out infinite;
}
```

### 6.3 Loading States

```css
/* loading-animations.css */

/**
 * Skeleton shimmer
 */
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton-shimmer {
  background: linear-gradient(
    90deg,
    var(--surface) 25%,
    var(--surface-elevated) 50%,
    var(--surface) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

/**
 * Dots loading
 */
@keyframes dotsLoading {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.dots-loader span {
  animation: dotsLoading 1.4s ease-in-out infinite;
}

.dots-loader span:nth-child(1) { animation-delay: 0s; }
.dots-loader span:nth-child(2) { animation-delay: 0.16s; }
.dots-loader span:nth-child(3) { animation-delay: 0.32s; }

/**
 * Progress bar with glow
 */
@keyframes progressGlow {
  0% {
    box-shadow: 0 0 5px rgba(6, 182, 212, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.8);
  }
  100% {
    box-shadow: 0 0 5px rgba(6, 182, 212, 0.5);
  }
}

.progress-bar-glow {
  animation: progressGlow 1s ease-in-out infinite;
}

/**
 * Spinner with trail
 */
@keyframes spinnerTrail {
  0% {
    transform: rotate(0deg);
    stroke-dashoffset: 60;
  }
  50% {
    stroke-dashoffset: 20;
  }
  100% {
    transform: rotate(360deg);
    stroke-dashoffset: 60;
  }
}

.spinner-trail circle {
  stroke-dasharray: 60;
  animation: spinnerTrail 1.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}
```

---

## Part 7: Integration Examples

### 7.1 Hero Section Animation Sequence

```javascript
// hero-sequence.js

import { choreographer } from './choreographer.js';
import { PhysicsParticleSystem } from './physics-particles.js';
import { MorphingShape } from './morphing-shapes.js';

function initHeroAnimations() {
  // Create choreographed entrance sequence
  choreographer.sequence('hero-entrance', {
    onComplete: () => console.log('Hero animation complete')
  })
    // Title with anticipation
    .withAnticipation('.hero-title', {
      opacity: 1,
      y: 0
    }, {
      anticipationAmount: 0.15,
      duration: 600
    })
    // Subtitle follows
    .add('.hero-subtitle', {
      opacity: 1,
      y: 0
    }, {
      start: 200,
      duration: 500
    })
    // CTA with bounce
    .withFollowThrough('.hero-cta', {
      opacity: 1,
      scale: 1
    }, {
      start: 400,
      overshootAmount: 0.2,
      duration: 500
    })
    // Stats stagger with golden ratio
    .stagger('.hero-stat', {
      opacity: 1,
      y: 0
    }, {
      start: 600,
      staggerType: 'golden',
      staggerDelay: 80
    });

  // Initialize physics particles
  const heroContainer = document.querySelector('.hero-bg');
  if (heroContainer) {
    new PhysicsParticleSystem(heroContainer, {
      count: 25,
      gravity: 0.005,
      turbulence: 0.08
    });
  }

  // Initialize morphing blob
  const blobPath = document.querySelector('.hero-blob path');
  if (blobPath) {
    new MorphingShape(blobPath, {
      morphSpeed: 0.3,
      complexity: 10
    });
  }

  // Start sequence
  choreographer.play('hero-entrance');
}

export { initHeroAnimations };
```

### 7.2 Card Interaction Setup

```javascript
// card-interactions.js

import { CursorDeformer, MagneticElement } from './cursor-effects.js';
import { DraggablePhysics } from './drag-physics.js';
import { willChangeManager } from './will-change-manager.js';

function initCardInteractions() {
  // Feature cards with deformation
  document.querySelectorAll('.feature-card').forEach(card => {
    new CursorDeformer(card, { intensity: 0.08 });
  });

  // CTA buttons with magnetic effect
  document.querySelectorAll('.btn-cta, .btn-hero').forEach(btn => {
    new MagneticElement(btn, {
      radius: 80,
      strength: 0.25
    });
  });

  // Flashcards with drag physics
  document.querySelectorAll('.flashcard').forEach(card => {
    new DraggablePhysics(card, {
      snapPoints: [
        { x: -200, y: 0 }, // Swipe left
        { x: 200, y: 0 },  // Swipe right
        { x: 0, y: 0 }     // Center
      ],
      snapThreshold: 100,
      throwMultiplier: 1.5
    });
  });
}

export { initCardInteractions };
```

### 7.3 Scroll-Triggered Animations

```javascript
// scroll-animations.js

import { LazyAnimationTrigger } from './intersection-animations.js';
import { BreathingController } from './breathing-animations.js';
import { choreographer } from './choreographer.js';

function initScrollAnimations() {
  const trigger = new LazyAnimationTrigger({
    rootMargin: '100px',
    threshold: 0.2
  });

  // Register section animations
  document.querySelectorAll('.section').forEach((section, i) => {
    trigger.register(section, (el) => {
      // Create section-specific sequence
      const seq = choreographer.sequence(`section-${i}`);

      seq.stagger(el.querySelectorAll('.stagger-item'), {
        opacity: 1,
        y: 0
      }, {
        staggerType: 'ease-out',
        staggerDelay: 60
      });

      seq.play();

      return seq;
    });
  });

  // Register breathing backgrounds
  document.querySelectorAll('.breathing-section').forEach(section => {
    trigger.register(section, (el) => {
      return new BreathingController(el, { period: 5000 });
    });
  });
}

export { initScrollAnimations };
```

---

## Summary

This motion design plan provides a comprehensive framework for creating award-winning animations:

| Category | Features |
|----------|----------|
| **Physics Engine** | Spring dynamics (RK4), inertial scroll, elastic bounds, natural decay |
| **Choreography** | Timeline sequencing, golden ratio stagger, anticipation, follow-through, squash/stretch |
| **Interactivity** | Cursor deformation, magnetic attraction, drag physics, gesture recognition |
| **Ambient Motion** | Breathing backgrounds, physics particles, morphing shapes, noise movement |
| **Performance** | GPU-only transforms, will-change lifecycle, intersection triggers, frame budgeting |

### Implementation Priority

1. **Phase 1**: Core physics engine (SpringPhysics, AnimationLoop)
2. **Phase 2**: Choreographer for sequences
3. **Phase 3**: Interactive effects (cursor, drag)
4. **Phase 4**: Ambient motion systems
5. **Phase 5**: Performance optimizations

### Files to Create

- `src/vl_jepa/api/static/js/motion-engine.js`
- `src/vl_jepa/api/static/js/choreographer.js`
- `src/vl_jepa/api/static/js/cursor-effects.js`
- `src/vl_jepa/api/static/js/drag-physics.js`
- `src/vl_jepa/api/static/js/gesture-animations.js`
- `src/vl_jepa/api/static/js/ambient-motion.js`
- `src/vl_jepa/api/static/js/performance-utils.js`
- `src/vl_jepa/api/static/css/entrance-animations.css`
- `src/vl_jepa/api/static/css/micro-interactions.css`
- `src/vl_jepa/api/static/css/loading-animations.css`
- `src/vl_jepa/api/static/css/ambient-motion.css`

---

*This plan provides the foundation for animations that feel alive, responsive, and delightful - the hallmarks of award-winning motion design.*
