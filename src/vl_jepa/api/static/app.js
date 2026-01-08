/**
 * Lecture Mind - Frontend Application
 *
 * Premium UI interactions with:
 * - Safe DOM manipulation (XSS-free)
 * - Accessible animations (prefers-reduced-motion)
 * - Toast notifications
 * - Proper error handling with retry
 */

// ============================================
// CONFIGURATION
// ============================================
const CONFIG = {
  POLL_INTERVAL: 500,
  SEARCH_DEBOUNCE: 300,
  FETCH_TIMEOUT: 30000,
  MAX_FILE_SIZE: 500 * 1024 * 1024, // 500MB
  TOAST_DURATION: 5000,
  VALID_TYPES: ['video/mp4', 'video/webm', 'video/avi', 'video/quicktime', 'video/x-matroska'],
};

// ============================================
// STATE
// ============================================
let currentJobId = null;
let processingResult = null;
let pollInterval = null;
let abortController = null;

// Check for reduced motion preference
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

// ============================================
// DOM ELEMENTS
// ============================================
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);

const elements = {
  uploadZone: $('#upload-zone'),
  fileInput: $('#file-input'),
  uploadSection: $('#upload-section'),
  progressSection: $('#progress-section'),
  progressStage: $('#progress-stage'),
  progressMessage: $('#progress-message'),
  progressPercent: $('#progress-percent'),
  progressBar: $('#progress-bar'),
  videoInfo: $('#video-info'),
  eventsSection: $('#events-section'),
  eventsList: $('#events-list'),
  searchInput: $('#search-input'),
  searchResults: $('#search-results'),
  transcriptContent: $('#transcript-content'),
  exportBtn: $('#export-btn'),
  themeToggle: $('#theme-toggle'),
  toastContainer: $('#toast-container'),
};

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initHeaderScroll();
  initScrollAnimations();
  initAdvancedEffects();
  initUpload();
  initTabs();
  initSearch();
  initExport();
  initExportOptions();
});

// ============================================
// ADVANCED UI EFFECTS
// ============================================
function initAdvancedEffects() {
  if (prefersReducedMotion.matches) return;

  initAnimatedCounters();
  initTypewriter();
  initCardTilt();
  initButtonRipple();
  initCursorGlow();
  initMagneticButtons();
  initSectionTransitions();
  initInteractiveParticles();
}

// 1. ANIMATED STATS COUNTER
function initAnimatedCounters() {
  const counters = document.querySelectorAll('.hero-stat-value');
  if (counters.length === 0) return;

  const observerOptions = { threshold: 0.5 };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        entry.target.dataset.animated = 'true';
        animateCounter(entry.target);
      }
    });
  }, observerOptions);

  counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
  const text = element.textContent.trim();
  const hasPrefix = text.startsWith('<') || text.startsWith('>');
  const hasSuffix = text.endsWith('+') || text.endsWith('ms') || text.endsWith('K+');

  let prefix = '';
  let suffix = '';
  let numStr = text;

  if (text.startsWith('<')) { prefix = '< '; numStr = text.slice(2); }
  if (text.startsWith('>')) { prefix = '> '; numStr = text.slice(2); }

  if (text.endsWith('K+')) { suffix = 'K+'; numStr = numStr.slice(0, -2); }
  else if (text.endsWith('ms')) { suffix = 'ms'; numStr = numStr.slice(0, -2); }
  else if (text.endsWith('+')) { suffix = '+'; numStr = numStr.slice(0, -1); }

  const target = parseInt(numStr, 10);
  if (isNaN(target)) return;

  const duration = 2000;
  const steps = 60;
  const stepDuration = duration / steps;
  let current = 0;

  const interval = setInterval(() => {
    current += target / steps;
    if (current >= target) {
      current = target;
      clearInterval(interval);
    }
    element.textContent = prefix + Math.round(current) + suffix;
  }, stepDuration);
}

// 2. TYPEWRITER EFFECT
function initTypewriter() {
  const element = document.querySelector('.hero-title-gradient');
  if (!element) return;

  const text = element.textContent;
  element.textContent = '';
  element.classList.add('typewriter');

  const cursor = document.createElement('span');
  cursor.className = 'typewriter-cursor';

  let i = 0;
  const speed = 80;

  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    } else {
      element.appendChild(cursor);
      setTimeout(() => cursor.remove(), 3000);
    }
  }

  // Start after a delay
  setTimeout(type, 500);
}

// 3. INTERACTIVE PARTICLES
function initInteractiveParticles() {
  const particles = document.querySelectorAll('.particle');
  const hero = document.querySelector('.hero');
  if (!hero || particles.length === 0) return;

  particles.forEach(p => p.classList.add('interactive'));

  let mouseX = 0, mouseY = 0;

  hero.addEventListener('mousemove', (e) => {
    const rect = hero.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;

    particles.forEach(particle => {
      const pRect = particle.getBoundingClientRect();
      const pX = pRect.left - rect.left + pRect.width / 2;
      const pY = pRect.top - rect.top + pRect.height / 2;

      const dx = mouseX - pX;
      const dy = mouseY - pY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 150) {
        const force = (150 - distance) / 150;
        const moveX = -dx * force * 0.3;
        const moveY = -dy * force * 0.3;
        particle.style.transform = `translate(${moveX}px, ${moveY}px)`;
      } else {
        particle.style.transform = '';
      }
    });
  });

  hero.addEventListener('mouseleave', () => {
    particles.forEach(p => p.style.transform = '');
  });
}

// 4. 3D CARD TILT
function initCardTilt() {
  const cards = document.querySelectorAll('.feature-card, .tech-card');

  cards.forEach(card => {
    card.classList.add('tilt-card');

    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = (y - centerY) / centerY * -8;
      const rotateY = (x - centerX) / centerX * 8;

      card.style.setProperty('--rotateX', `${rotateX}deg`);
      card.style.setProperty('--rotateY', `${rotateY}deg`);
    });

    card.addEventListener('mouseleave', () => {
      card.style.setProperty('--rotateX', '0deg');
      card.style.setProperty('--rotateY', '0deg');
    });
  });
}

// 5. BUTTON RIPPLE EFFECT
function initButtonRipple() {
  const buttons = document.querySelectorAll('.btn');

  buttons.forEach(btn => {
    btn.addEventListener('click', function(e) {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      ripple.style.left = x + 'px';
      ripple.style.top = y + 'px';

      btn.appendChild(ripple);

      setTimeout(() => ripple.remove(), 600);
    });
  });
}

// 6. CURSOR GLOW TRAIL
function initCursorGlow() {
  // Only on desktop
  if (window.innerWidth < 768) return;

  const glow = document.createElement('div');
  glow.className = 'cursor-glow';
  document.body.appendChild(glow);

  const hero = document.querySelector('.hero');
  if (!hero) return;

  let glowX = 0, glowY = 0;
  let currentX = 0, currentY = 0;

  hero.addEventListener('mouseenter', () => glow.classList.add('active'));
  hero.addEventListener('mouseleave', () => glow.classList.remove('active'));

  document.addEventListener('mousemove', (e) => {
    glowX = e.clientX;
    glowY = e.clientY;
  });

  function animateGlow() {
    currentX += (glowX - currentX) * 0.1;
    currentY += (glowY - currentY) * 0.1;

    glow.style.left = currentX + 'px';
    glow.style.top = currentY + 'px';

    requestAnimationFrame(animateGlow);
  }

  animateGlow();
}

// 7. MAGNETIC BUTTONS
function initMagneticButtons() {
  const buttons = document.querySelectorAll('.btn-hero, .btn[data-variant="primary"]');

  buttons.forEach(btn => {
    btn.classList.add('magnetic-btn');

    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      btn.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = '';
    });
  });
}

// 8. SECTION COLOR TRANSITIONS
function initSectionTransitions() {
  const sections = document.querySelectorAll('.features-section, .how-it-works-section, .tech-section');

  sections.forEach(section => {
    section.classList.add('section-gradient-bg');
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
      } else {
        entry.target.classList.remove('in-view');
      }
    });
  }, { threshold: 0.3 });

  sections.forEach(section => observer.observe(section));
}

// ============================================
// HEADER SCROLL STATE
// ============================================
function initHeaderScroll() {
  const header = document.querySelector('.header-landing');
  if (!header) return;

  const scrollThreshold = 50;
  let ticking = false;

  function updateHeader() {
    if (window.scrollY > scrollThreshold) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    ticking = false;
  }

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateHeader);
      ticking = true;
    }
  }, { passive: true });

  // Initial check
  updateHeader();
}

// ============================================
// SCROLL-TRIGGERED ANIMATIONS (AOS Replacement)
// ============================================
function initScrollAnimations() {
  // Skip if user prefers reduced motion
  if (prefersReducedMotion.matches) return;

  const animatedElements = document.querySelectorAll('[data-aos]');
  if (animatedElements.length === 0) return;

  // Create intersection observer
  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -10% 0px',
    threshold: 0.1
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const animation = el.getAttribute('data-aos') || 'fade-up';
        const delay = parseInt(el.getAttribute('data-aos-delay') || '0', 10);

        setTimeout(() => {
          el.classList.add('aos-animate');
          el.setAttribute('data-aos-animated', 'true');
        }, delay);

        // Unobserve after animation
        observer.unobserve(el);
      }
    });
  }, observerOptions);

  // Observe all elements with data-aos
  animatedElements.forEach(el => {
    el.classList.add('aos-init');
    observer.observe(el);
  });

  // Initialize parallax effect for hero
  initParallax();
}

// ============================================
// PARALLAX SCROLL EFFECT
// ============================================
function initParallax() {
  if (prefersReducedMotion.matches) return;

  const hero = document.querySelector('.hero');
  const morphBg = document.querySelector('.morph-bg');
  const auroraBlobs = document.querySelectorAll('.aurora-blob');
  const heroContent = document.querySelector('.hero-content');
  const heroVisual = document.querySelector('.hero-visual');

  if (!hero) return;

  let ticking = false;

  function updateParallax() {
    const scrollY = window.scrollY;
    const heroHeight = hero.offsetHeight;

    // Only apply parallax within hero section
    if (scrollY > heroHeight) {
      ticking = false;
      return;
    }

    const scrollPercent = scrollY / heroHeight;

    // Parallax for morph background (slow)
    if (morphBg) {
      morphBg.style.transform = `translateY(${scrollY * 0.3}px) rotate(${scrollPercent * 5}deg)`;
    }

    // Parallax for aurora blobs (medium)
    auroraBlobs.forEach((blob, i) => {
      const speed = 0.1 + (i * 0.05);
      blob.style.transform = `translateY(${scrollY * speed}px)`;
    });

    // Parallax for hero content (subtle fade out)
    if (heroContent) {
      const opacity = Math.max(0, 1 - scrollPercent * 1.5);
      const translateY = scrollY * 0.4;
      heroContent.style.opacity = opacity;
      heroContent.style.transform = `translateY(${translateY}px)`;
    }

    // Parallax for hero visual (moves slower)
    if (heroVisual) {
      const opacity = Math.max(0, 1 - scrollPercent * 1.2);
      const translateY = scrollY * 0.2;
      heroVisual.style.opacity = opacity;
      heroVisual.style.transform = `translateY(${translateY}px)`;
    }

    ticking = false;
  }

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateParallax);
      ticking = true;
    }
  }, { passive: true });
}

// ============================================
// THEME MANAGEMENT
// ============================================
function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (saved === 'dark' || (!saved && prefersDark)) {
    document.documentElement.classList.add('dark');
  }

  elements.themeToggle.addEventListener('click', toggleTheme);
}

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');

  // Animate the toggle button
  if (!prefersReducedMotion.matches) {
    elements.themeToggle.animate([
      { transform: 'scale(0.9)' },
      { transform: 'scale(1)' }
    ], { duration: 200, easing: 'ease-out' });
  }
}

// ============================================
// FILE UPLOAD
// ============================================
function initUpload() {
  const { uploadZone, fileInput } = elements;

  // Click to upload
  uploadZone.addEventListener('click', () => fileInput.click());

  // Keyboard support
  uploadZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInput.click();
    }
  });

  // File selected
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  });

  // Drag and drop
  uploadZone.addEventListener('dragover', handleDragOver);
  uploadZone.addEventListener('dragleave', handleDragLeave);
  uploadZone.addEventListener('drop', handleDrop);
}

function handleDragOver(e) {
  e.preventDefault();
  e.stopPropagation();
  elements.uploadZone.setAttribute('data-dragover', 'true');
}

function handleDragLeave(e) {
  e.preventDefault();
  e.stopPropagation();
  elements.uploadZone.removeAttribute('data-dragover');
}

function handleDrop(e) {
  e.preventDefault();
  e.stopPropagation();
  elements.uploadZone.removeAttribute('data-dragover');

  if (e.dataTransfer.files.length > 0) {
    uploadFile(e.dataTransfer.files[0]);
  }
}

async function uploadFile(file) {
  // Validate file type
  const isValidType = CONFIG.VALID_TYPES.some(t =>
    file.type.includes(t.split('/')[1]) || file.name.toLowerCase().endsWith(t.split('/')[1])
  );

  if (!isValidType) {
    showToast('error', 'Invalid File', 'Please upload a valid video file (MP4, WebM, AVI, MOV, MKV)');
    return;
  }

  // Validate file size
  if (file.size > CONFIG.MAX_FILE_SIZE) {
    showToast('error', 'File Too Large', 'Maximum file size is 500MB');
    return;
  }

  // Show progress section
  showElement(elements.progressSection);
  hideElement(elements.uploadSection);
  updateProgress('Uploading', 'Preparing upload...', 0);

  // Cancel any existing request
  if (abortController) {
    abortController.abort();
  }
  abortController = new AbortController();

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetchWithTimeout('/api/upload', {
      method: 'POST',
      body: formData,
      signal: abortController.signal,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    const data = await response.json();
    currentJobId = data.job_id;

    showToast('success', 'Upload Complete', 'Processing your video...');
    startPolling();

  } catch (error) {
    if (error.name === 'AbortError') {
      showToast('warning', 'Upload Cancelled', 'The upload was cancelled');
    } else {
      showToast('error', 'Upload Failed', error.message);
    }
    resetUpload();
  }
}

// ============================================
// POLLING & PROGRESS
// ============================================
function startPolling() {
  pollInterval = setInterval(async () => {
    try {
      const response = await fetchWithTimeout(`/api/status/${currentJobId}`);
      const data = await response.json();

      updateProgress(
        formatStage(data.stage),
        data.message,
        data.progress * 100
      );

      if (data.status === 'completed') {
        stopPolling();
        await loadResults();
      } else if (data.status === 'failed') {
        stopPolling();
        showToast('error', 'Processing Failed', data.error || 'An error occurred');
        resetUpload();
      }

    } catch (error) {
      console.error('Polling error:', error);
    }
  }, CONFIG.POLL_INTERVAL);
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

function updateProgress(stage, message, percent) {
  elements.progressStage.textContent = stage;
  elements.progressMessage.textContent = message;
  elements.progressPercent.textContent = Math.round(percent) + '%';
  elements.progressBar.style.width = percent + '%';

  // Update ARIA
  elements.progressSection.setAttribute('aria-valuenow', Math.round(percent));
}

function formatStage(stage) {
  const stageNames = {
    'loading': 'Loading Video',
    'extracting_audio': 'Extracting Audio',
    'transcribing': 'Transcribing',
    'sampling_frames': 'Sampling Frames',
    'encoding_frames': 'Encoding Frames',
    'encoding_text': 'Encoding Text',
    'detecting_events': 'Detecting Events',
    'building_index': 'Building Index',
    'completed': 'Complete'
  };
  return stageNames[stage] || 'Processing';
}

// ============================================
// RESULTS LOADING
// ============================================
async function loadResults() {
  try {
    const response = await fetchWithTimeout(`/api/results/${currentJobId}`);
    const data = await response.json();

    if (data.status !== 'completed' || !data.result) {
      throw new Error('Results not available');
    }

    processingResult = data.result;

    // Hide progress, show results with animation
    hideElement(elements.progressSection);
    showElement(elements.videoInfo);
    showElement(elements.eventsSection);

    // Populate video info
    const meta = data.result.metadata;
    $('#info-filename').textContent = meta.filename;
    $('#info-duration').textContent = formatDuration(meta.duration);
    $('#info-resolution').textContent = `${meta.width}x${meta.height}`;
    $('#info-fps').textContent = `${meta.fps.toFixed(1)} fps`;

    // Populate events and transcript
    renderEvents(data.result.events);
    renderTranscript(data.result.transcript);

    // Enable export
    elements.exportBtn.disabled = false;

    // Update search placeholder
    updateSearchPlaceholder('Type to search transcript');

    showToast('success', 'Processing Complete', 'Your video is ready to explore');

  } catch (error) {
    showToast('error', 'Error', error.message);
  }
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ============================================
// RENDER FUNCTIONS (Safe DOM)
// ============================================
function createElement(tag, className, attrs = {}) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  Object.entries(attrs).forEach(([key, value]) => {
    if (key === 'textContent') {
      el.textContent = value;
    } else {
      el.setAttribute(key, value);
    }
  });
  return el;
}

function clearElement(el) {
  while (el.firstChild) {
    el.removeChild(el.firstChild);
  }
}

function renderEvents(events) {
  clearElement(elements.eventsList);

  events.forEach((event, i) => {
    const card = createElement('div', 'event-card animate-fadeInUp', {
      role: 'listitem',
      tabindex: '0',
    });
    card.style.animationDelay = `${i * 50}ms`;

    const indexBox = createElement('div', 'event-card-index', { textContent: String(i + 1) });

    const content = createElement('div', 'event-card-content');
    const timestamp = createElement('p', 'event-card-timestamp', { textContent: event.timestamp_formatted });
    const confidence = createElement('p', 'event-card-confidence', {
      textContent: `Confidence: ${Math.round(event.confidence * 100)}%`
    });
    content.appendChild(timestamp);
    content.appendChild(confidence);

    const arrow = createSvgIcon('M9 5l7 7-7 7', 'event-card-arrow');

    card.appendChild(indexBox);
    card.appendChild(content);
    card.appendChild(arrow);

    // Keyboard support
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        // Could trigger video seek here
      }
    });

    elements.eventsList.appendChild(card);
  });
}

function renderTranscript(transcript) {
  clearElement(elements.transcriptContent);

  if (!transcript || transcript.length === 0) {
    const empty = createEmptyState(
      'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
      'No transcript available',
      'Transcript will appear here after processing'
    );
    elements.transcriptContent.appendChild(empty);
    return;
  }

  transcript.forEach((chunk, i) => {
    const card = createElement('div', 'transcript-chunk animate-fadeInUp');
    card.style.animationDelay = `${i * 30}ms`;

    const time = createElement('p', 'transcript-chunk-time', {
      textContent: `${chunk.start_formatted} - ${chunk.end_formatted}`
    });
    const text = createElement('p', 'transcript-chunk-text', { textContent: chunk.text });

    card.appendChild(time);
    card.appendChild(text);
    elements.transcriptContent.appendChild(card);
  });
}

function createSvgIcon(pathD, className = 'icon') {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('class', className);
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('stroke-width', '2');

  // Set explicit size for empty-state-icon to prevent overflow
  if (className === 'empty-state-icon') {
    svg.setAttribute('width', '40');
    svg.setAttribute('height', '40');
  }

  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('stroke-linecap', 'round');
  path.setAttribute('stroke-linejoin', 'round');
  path.setAttribute('d', pathD);

  svg.appendChild(path);
  return svg;
}

function createEmptyState(iconPath, title, description) {
  const container = createElement('div', 'empty-state');
  const icon = createSvgIcon(iconPath, 'empty-state-icon');
  const titleEl = createElement('p', 'empty-state-title', { textContent: title });
  const descEl = createElement('p', 'empty-state-description', { textContent: description });

  container.appendChild(icon);
  container.appendChild(titleEl);
  container.appendChild(descEl);

  return container;
}

// ============================================
// TABS
// ============================================
function initTabs() {
  const triggers = $$('.tabs-trigger');

  triggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const tabName = trigger.getAttribute('data-tab');
      switchTab(tabName);
    });
  });
}

function switchTab(tabName) {
  // Update triggers
  $$('.tabs-trigger').forEach(t => {
    const isActive = t.getAttribute('data-tab') === tabName;
    t.setAttribute('data-state', isActive ? 'active' : 'inactive');
    t.setAttribute('aria-selected', isActive ? 'true' : 'false');
  });

  // Update content panels
  $$('.tabs-content').forEach(panel => {
    const isActive = panel.id === `tab-${tabName}`;
    panel.setAttribute('data-state', isActive ? 'active' : 'inactive');
  });
}

// ============================================
// SEARCH
// ============================================
function initSearch() {
  let searchTimeout = null;

  elements.searchInput.addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      performSearch(e.target.value);
    }, CONFIG.SEARCH_DEBOUNCE);
  });
}

async function performSearch(query) {
  if (!query.trim() || !currentJobId) {
    updateSearchPlaceholder('Type to search transcript');
    return;
  }

  // Show loading state
  clearElement(elements.searchResults);
  const loading = createElement('div', 'search-loading');
  loading.appendChild(createElement('div', 'spinner'));
  loading.appendChild(createElement('p', 'text-muted', { textContent: 'Searching...' }));
  elements.searchResults.appendChild(loading);

  try {
    const response = await fetchWithTimeout(`/api/search/${currentJobId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: 5 })
    });

    const data = await response.json();
    clearElement(elements.searchResults);

    if (data.results.length === 0) {
      const empty = createEmptyState(
        'M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z',
        'No results found',
        'Try a different search term'
      );
      elements.searchResults.appendChild(empty);
      return;
    }

    data.results.forEach((result, i) => {
      const card = createElement('div', 'search-result animate-fadeInUp');
      card.style.animationDelay = `${i * 50}ms`;

      const header = createElement('div', 'search-result-header');
      const timeBadge = createElement('span', 'search-result-timestamp', {
        textContent: result.timestamp_formatted
      });
      const typeBadge = createElement('span', 'search-result-type', {
        textContent: result.result_type
      });
      header.appendChild(timeBadge);
      header.appendChild(typeBadge);

      const text = createElement('p', 'search-result-text');
      renderHighlightedText(text, result.text, query);

      card.appendChild(header);
      card.appendChild(text);
      elements.searchResults.appendChild(card);
    });

  } catch (error) {
    console.error('Search error:', error);
    updateSearchPlaceholder('Search failed. Please try again.');
  }
}

function renderHighlightedText(container, text, query) {
  const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
  const parts = text.split(regex);

  parts.forEach(part => {
    if (part.toLowerCase() === query.toLowerCase()) {
      const mark = createElement('mark', 'highlight', { textContent: part });
      container.appendChild(mark);
    } else {
      container.appendChild(document.createTextNode(part));
    }
  });
}

function updateSearchPlaceholder(message) {
  clearElement(elements.searchResults);
  const empty = createEmptyState(
    'M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z',
    'Ready to search',
    message
  );
  elements.searchResults.appendChild(empty);
}

function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ============================================
// EXPORT
// ============================================
function initExport() {
  elements.exportBtn.addEventListener('click', handleExport);
}

function initExportOptions() {
  const options = $$('.export-option');
  options.forEach(option => {
    const radio = option.querySelector('input[type="radio"]');
    radio.addEventListener('change', () => {
      options.forEach(o => o.removeAttribute('data-selected'));
      option.setAttribute('data-selected', 'true');
    });
  });
}

async function handleExport() {
  if (!currentJobId) return;

  const format = $('input[name="export-format"]:checked').value;
  const btn = elements.exportBtn;

  try {
    btn.disabled = true;
    btn.textContent = 'Exporting...';

    const response = await fetchWithTimeout(`/api/export/${currentJobId}/${format}`);
    const data = await response.json();

    // Create download
    const blob = new Blob([data.content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = data.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('success', 'Export Complete', `Downloaded ${data.filename}`);

  } catch (error) {
    showToast('error', 'Export Failed', error.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Download';
  }
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(variant, title, message) {
  const toast = createElement('div', 'toast', { 'data-variant': variant });

  // Icon based on variant
  const iconPaths = {
    success: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    error: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
    warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
    info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
  };

  const icon = createSvgIcon(iconPaths[variant] || iconPaths.info, 'toast-icon');
  icon.style.color = `var(--${variant === 'success' ? 'success' : variant === 'error' ? 'error' : variant === 'warning' ? 'warning' : 'primary'})`;

  const content = createElement('div', 'toast-content');
  const titleEl = createElement('p', 'toast-title', { textContent: title });
  const messageEl = createElement('p', 'toast-message', { textContent: message });
  content.appendChild(titleEl);
  content.appendChild(messageEl);

  const closeBtn = createElement('button', 'toast-close', { 'aria-label': 'Dismiss' });
  closeBtn.appendChild(createSvgIcon('M6 18L18 6M6 6l12 12'));
  closeBtn.addEventListener('click', () => removeToast(toast));

  toast.appendChild(icon);
  toast.appendChild(content);
  toast.appendChild(closeBtn);

  elements.toastContainer.appendChild(toast);

  // Auto-remove after duration
  setTimeout(() => removeToast(toast), CONFIG.TOAST_DURATION);
}

function removeToast(toast) {
  if (!toast.parentNode) return;

  toast.style.animation = 'fadeOut 200ms ease-out forwards';
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast);
    }
  }, 200);
}

// ============================================
// UTILITIES
// ============================================
function showElement(el) {
  el.classList.remove('hidden');
  if (!prefersReducedMotion.matches) {
    el.style.opacity = '0';
    requestAnimationFrame(() => {
      el.style.transition = 'opacity 200ms ease-out';
      el.style.opacity = '1';
    });
  }
}

function hideElement(el) {
  if (!prefersReducedMotion.matches) {
    el.style.transition = 'opacity 150ms ease-out';
    el.style.opacity = '0';
    setTimeout(() => el.classList.add('hidden'), 150);
  } else {
    el.classList.add('hidden');
  }
}

async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), CONFIG.FETCH_TIMEOUT);

  try {
    const response = await fetch(url, {
      ...options,
      signal: options.signal || controller.signal,
    });
    return response;
  } finally {
    clearTimeout(timeout);
  }
}

function resetUpload() {
  showElement(elements.uploadSection);
  hideElement(elements.progressSection);
  hideElement(elements.videoInfo);
  hideElement(elements.eventsSection);
  elements.fileInput.value = '';
  currentJobId = null;
  processingResult = null;
  elements.exportBtn.disabled = true;

  // Reset search and transcript
  updateSearchPlaceholder('Upload a video to search through transcript and visual content');

  clearElement(elements.transcriptContent);
  const emptyTranscript = createEmptyState(
    'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
    'No transcript yet',
    'Upload a video to generate a transcript'
  );
  elements.transcriptContent.appendChild(emptyTranscript);
}

// Add fadeOut keyframe dynamically
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeOut {
    from { opacity: 1; transform: translateX(0); }
    to { opacity: 0; transform: translateX(20px); }
  }

  .search-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-8);
  }
`;
document.head.appendChild(style);
