/**
 * script.js
 * ---------
 * Vanilla JavaScript for Smart Complaint Prioritization Using AI.
 * Handles: sidebar, nav, forms, live AI preview, Chart.js, password strength.
 */

/* ================================================================
   0. NEON PARTICLE CANVAS ANIMATION
================================================================ */
(function initParticles() {
  const canvas = document.getElementById('particleCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const numParticles = Math.min(Math.floor(width * 0.05), 65);
  const particles = [];

  for (let i = 0; i < numParticles; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.6,
      vy: (Math.random() - 0.5) * 0.6,
      radius: Math.random() * 2 + 1,
      color: Math.random() > 0.4 ? '#00d4ff' : '#00ffcc'
    });
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    // Update and draw particles
    for (let i = 0; i < particles.length; i++) {
      let p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.shadowBlur = 8;
      ctx.shadowColor = p.color;
      ctx.fill();

      // Connect nearby particles
      for (let j = i + 1; j < particles.length; j++) {
        let p2 = particles[j];
        let dx = p.x - p2.x;
        let dy = p.y - p2.y;
        let dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 130) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(0, 212, 255, ${0.15 * (1 - dist / 130)})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  }

  draw();
})();

/* ================================================================
   1. SIDEBAR TOGGLE (Mobile)
================================================================ */
(function initSidebar() {
  const sidebar      = document.getElementById('sidebar');
  const overlay      = document.getElementById('sidebarOverlay');
  const toggleBtn    = document.getElementById('sidebarToggle');
  const closeBtn     = document.getElementById('sidebarClose');

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add('open');
    if (overlay) { overlay.classList.add('open'); }
    document.body.style.overflow = 'hidden';
  }
  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('open');
    if (overlay) { overlay.classList.remove('open'); }
    document.body.style.overflow = '';
  }

  if (toggleBtn) toggleBtn.addEventListener('click', openSidebar);
  if (closeBtn)  closeBtn.addEventListener('click', closeSidebar);
  if (overlay)   overlay.addEventListener('click', closeSidebar);
})();


/* ================================================================
   2. MOBILE NAV HAMBURGER (Landing page)
================================================================ */
(function initHamburger() {
  const btn   = document.getElementById('hamburger');
  const links = document.querySelector('.nav-links');
  if (!btn || !links) return;

  btn.addEventListener('click', () => {
    links.classList.toggle('open');
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!btn.contains(e.target) && !links.contains(e.target)) {
      links.classList.remove('open');
    }
  });
})();


/* ================================================================
   3. NAVBAR SCROLL EFFECT (Landing page)
================================================================ */
(function initNavScroll() {
  const nav = document.getElementById('mainNav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.style.boxShadow = window.scrollY > 40
      ? '0 4px 24px rgba(0,0,0,0.3)'
      : 'none';
  }, { passive: true });
})();


/* ================================================================
   4. AUTO-DISMISS FLASH MESSAGES
================================================================ */
(function autoDismissAlerts() {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, max-height 0.5s ease';
      alert.style.opacity = '0';
      alert.style.maxHeight = '0';
      alert.style.overflow = 'hidden';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });
})();


/* ================================================================
   5. CHARACTER COUNTERS (Complaint Form)
================================================================ */
(function initCharCounters() {
  const titleEl = document.getElementById('title');
  const descEl  = document.getElementById('description');
  const titleCount = document.getElementById('titleCount');
  const descCount  = document.getElementById('descCount');

  if (titleEl && titleCount) {
    function updateTitle() {
      titleCount.textContent = `${titleEl.value.length} / 150`;
    }
    titleEl.addEventListener('input', updateTitle);
    updateTitle();
  }

  if (descEl && descCount) {
    function updateDesc() {
      descCount.textContent = `${descEl.value.length} / 2000`;
    }
    descEl.addEventListener('input', updateDesc);
    updateDesc();
  }
})();


/* ================================================================
   6. PASSWORD STRENGTH METER (Register page)
================================================================ */
(function initPwStrength() {
  const pwInput  = document.getElementById('password');
  const pwBar    = document.getElementById('pwBar');
  const pwLabel  = document.getElementById('pwLabel');
  if (!pwInput || !pwBar) return;

  pwInput.addEventListener('input', () => {
    const val = pwInput.value;
    let score = 0;
    if (val.length >= 6)  score++;
    if (val.length >= 10) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;

    const levels = [
      { label: '',         width: '0%',   color: '' },
      { label: 'Weak',     width: '20%',  color: '#ef4444' },
      { label: 'Fair',     width: '40%',  color: '#f97316' },
      { label: 'Good',     width: '60%',  color: '#f59e0b' },
      { label: 'Strong',   width: '80%',  color: '#10b981' },
      { label: 'Very Strong', width: '100%', color: '#059669' },
    ];

    const level = levels[Math.min(score, 5)];
    pwBar.style.width    = level.width;
    pwBar.style.background = level.color;
    if (pwLabel) pwLabel.textContent = val.length > 0 ? level.label : '';
  });
})();


/* ================================================================
   7. TOGGLE PASSWORD VISIBILITY
================================================================ */
function togglePw(inputId, btn) {
  const input = document.getElementById(inputId);
  const icon  = btn.querySelector('i');
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    icon.classList.replace('fa-eye', 'fa-eye-slash');
  } else {
    input.type = 'password';
    icon.classList.replace('fa-eye-slash', 'fa-eye');
  }
}


/* ================================================================
   8. LIVE AI PRIORITY PREVIEW (Complaint Form)
================================================================ */
let aiDebounceTimer = null;

function triggerAnalysis() {
  clearTimeout(aiDebounceTimer);
  aiDebounceTimer = setTimeout(runAiAnalysis, 600);
}

async function runAiAnalysis() {
  const titleEl = document.getElementById('title');
  const descEl  = document.getElementById('description');
  if (!titleEl || !descEl) return;

  const title       = titleEl.value.trim();
  const description = descEl.value.trim();

  const placeholder = document.getElementById('aiResult');
  const content     = document.getElementById('aiResultContent');

  if (title.length < 3 || description.length < 10) {
    if (placeholder) placeholder.style.display = 'block';
    if (content)     content.style.display     = 'none';
    return;
  }

  // Show loading
  if (placeholder) {
    placeholder.innerHTML = '<i class="fas fa-spinner fa-spin"></i><p>Analyzing…</p>';
    placeholder.style.display = 'block';
  }
  if (content) content.style.display = 'none';

  try {
    const resp = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description }),
    });

    if (!resp.ok) throw new Error('API error');

    const data = await resp.json();

    // Populate result
    const priorityColors = {
      Critical: '#dc2626',
      High:     '#f97316',
      Medium:   '#f59e0b',
      Low:      '#10b981',
    };
    const scoreBarColors = {
      Critical: '#dc2626',
      High:     '#f97316',
      Medium:   '#f59e0b',
      Low:      '#10b981',
    };

    const priorityEl  = document.getElementById('aiPriority');
    const scoreNumEl  = document.getElementById('aiScoreNum');
    const scoreFillEl = document.getElementById('aiScoreFill');
    const categoryEl  = document.getElementById('aiCategory');
    const tipsEl      = document.getElementById('aiTips');

    if (priorityEl) {
      priorityEl.textContent = data.priority;
      priorityEl.style.color = priorityColors[data.priority] || '#64748b';
    }
    if (scoreNumEl)  scoreNumEl.textContent = data.score;
    if (scoreFillEl) {
      scoreFillEl.style.width = data.score + '%';
      scoreFillEl.style.background = scoreBarColors[data.priority] || '#3b82f6';
    }
    if (categoryEl)  categoryEl.textContent = data.category;

    // Tips based on priority
    const tipsMap = {
      Critical: '🚨 This is a critical emergency complaint. It will be escalated immediately.',
      High:     '⚠️ High priority — admins will be notified promptly.',
      Medium:   '📋 Medium priority. Your complaint will be reviewed in due course.',
      Low:      '📌 Low priority complaint. Provide more details if the issue is more serious.',
    };
    if (tipsEl) {
      tipsEl.innerHTML = `<div class="alert alert-${data.priority === 'Critical' ? 'danger' : data.priority === 'High' ? 'warning' : 'info'}" style="margin-top:10px;margin-bottom:0">${tipsMap[data.priority] || ''}</div>`;
    }

    if (placeholder) placeholder.style.display = 'none';
    if (content)     content.style.display     = 'block';

  } catch (err) {
    if (placeholder) {
      placeholder.innerHTML = '<i class="fas fa-exclamation-circle"></i><p>Analysis unavailable</p>';
      placeholder.style.display = 'block';
    }
  }
}


/* ================================================================
   9. FORM VALIDATION (Login & Register)
================================================================ */
(function initForms() {
  // ---- Login Form ----
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      let valid = true;

      const email = document.getElementById('email');
      const pw    = document.getElementById('password');
      const emailErr = document.getElementById('emailError');
      const pwErr    = document.getElementById('pwError');

      if (emailErr) emailErr.textContent = '';
      if (pwErr)    pwErr.textContent    = '';

      if (!email.value.trim() || !email.value.includes('@')) {
        if (emailErr) emailErr.textContent = 'Please enter a valid email.';
        valid = false;
      }
      if (!pw.value || pw.value.length < 1) {
        if (pwErr) pwErr.textContent = 'Password is required.';
        valid = false;
      }

      if (!valid) { e.preventDefault(); return; }

      // Show loading state on button
      const btn = document.getElementById('loginBtn');
      if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in…';
        btn.disabled = true;
      }
    });
  }

  // ---- Register Form ----
  const regForm = document.getElementById('registerForm');
  if (regForm) {
    regForm.addEventListener('submit', (e) => {
      let valid = true;
      const name    = document.getElementById('name');
      const email   = document.getElementById('email');
      const pw      = document.getElementById('password');
      const confirm = document.getElementById('confirm_password');

      const nameErr    = document.getElementById('nameError');
      const emailErr   = document.getElementById('emailError');
      const pwErr      = document.getElementById('pwError');
      const confirmErr = document.getElementById('confirmError');

      [nameErr, emailErr, pwErr, confirmErr].forEach(el => { if (el) el.textContent = ''; });

      if (!name || name.value.trim().length < 2) {
        if (nameErr) nameErr.textContent = 'Name must be at least 2 characters.';
        valid = false;
      }
      if (!email || !email.value.includes('@')) {
        if (emailErr) emailErr.textContent = 'Enter a valid email address.';
        valid = false;
      }
      if (!pw || pw.value.length < 6) {
        if (pwErr) pwErr.textContent = 'Password must be at least 6 characters.';
        valid = false;
      }
      if (confirm && pw && confirm.value !== pw.value) {
        if (confirmErr) confirmErr.textContent = 'Passwords do not match.';
        valid = false;
      }

      if (!valid) { e.preventDefault(); return; }

      const btn = document.getElementById('registerBtn');
      if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account…';
        btn.disabled = true;
      }
    });
  }

  // ---- Complaint Form ----
  const complaintForm = document.getElementById('complaintForm');
  if (complaintForm) {
    complaintForm.addEventListener('submit', (e) => {
      let valid = true;
      const title = document.getElementById('title');
      const cat   = document.getElementById('category');
      const desc  = document.getElementById('description');
      const titleErr = document.getElementById('titleError');
      const catErr   = document.getElementById('catError');
      const descErr  = document.getElementById('descError');

      [titleErr, catErr, descErr].forEach(el => { if (el) el.textContent = ''; });

      if (!title || title.value.trim().length < 5) {
        if (titleErr) titleErr.textContent = 'Title must be at least 5 characters.';
        valid = false;
      }
      if (!cat || !cat.value) {
        if (catErr) catErr.textContent = 'Please select a category.';
        valid = false;
      }
      if (!desc || desc.value.trim().length < 20) {
        if (descErr) descErr.textContent = 'Description must be at least 20 characters.';
        valid = false;
      }

      if (!valid) { e.preventDefault(); return; }

      const btn = document.getElementById('submitBtn');
      if (btn) {
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting…';
        btn.disabled = true;
      }
    });
  }
})();


/* ================================================================
   10. CHART.JS — ADMIN DASHBOARD
================================================================ */
(function initCharts() {
  if (typeof Chart === 'undefined') return;
  if (typeof statsData === 'undefined') return;

  Chart.defaults.font.family = "'Inter', sans-serif";
  Chart.defaults.font.size   = 12;
  Chart.defaults.color       = '#64748b';

  const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { padding: 16, usePointStyle: true, pointStyleWidth: 10 }
      }
    }
  };

  // ---- Priority Doughnut Chart ----
  const priorityEl = document.getElementById('priorityChart');
  if (priorityEl) {
    const pd = statsData.byPriority || {};
    new Chart(priorityEl, {
      type: 'doughnut',
      data: {
        labels: Object.keys(pd),
        datasets: [{
          data: Object.values(pd),
          backgroundColor: ['#dc2626', '#f97316', '#f59e0b', '#10b981'],
          borderWidth: 3,
          borderColor: '#fff',
          hoverOffset: 6,
        }]
      },
      options: {
        ...chartDefaults,
        cutout: '60%',
        plugins: {
          ...chartDefaults.plugins,
          tooltip: {
            callbacks: {
              label: ctx => ` ${ctx.label}: ${ctx.parsed} complaints`
            }
          }
        }
      }
    });
  }

  // ---- Status Doughnut Chart ----
  const statusEl = document.getElementById('statusChart');
  if (statusEl) {
    const sd = statsData.byStatus || {};
    new Chart(statusEl, {
      type: 'doughnut',
      data: {
        labels: Object.keys(sd),
        datasets: [{
          data: Object.values(sd),
          backgroundColor: ['#fbbf24', '#8b5cf6', '#10b981', '#ef4444'],
          borderWidth: 3,
          borderColor: '#fff',
          hoverOffset: 6,
        }]
      },
      options: {
        ...chartDefaults,
        cutout: '60%',
      }
    });
  }

  // ---- Category Bar Chart ----
  const catEl = document.getElementById('categoryChart');
  if (catEl) {
    const cd = statsData.byCategory || {};
    const cats   = Object.keys(cd);
    const counts  = Object.values(cd);

    // Gradient colors for categories
    const catColors = [
      '#2563eb','#7c3aed','#db2777','#dc2626',
      '#ea580c','#d97706','#16a34a','#0891b2','#6366f1'
    ];

    new Chart(catEl, {
      type: 'bar',
      data: {
        labels: cats,
        datasets: [{
          label: 'Complaints',
          data: counts,
          backgroundColor: cats.map((_, i) => catColors[i % catColors.length] + 'CC'),
          borderColor:     cats.map((_, i) => catColors[i % catColors.length]),
          borderWidth: 2,
          borderRadius: 6,
        }]
      },
      options: {
        ...chartDefaults,
        plugins: {
          ...chartDefaults.plugins,
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 },
            grid: { color: 'rgba(0,0,0,0.05)' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }

  // ---- Monthly Line Chart ----
  const monthlyEl = document.getElementById('monthlyChart');
  if (monthlyEl) {
    const ml = statsData.monthly || {};
    const labels = ml.labels || [];
    const data   = ml.data   || [];

    new Chart(monthlyEl, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Complaints Submitted',
          data,
          borderColor:     '#2563eb',
          backgroundColor: 'rgba(37,99,235,0.08)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#2563eb',
          pointRadius: 5,
          pointHoverRadius: 7,
        }]
      },
      options: {
        ...chartDefaults,
        plugins: {
          ...chartDefaults.plugins,
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 },
            grid: { color: 'rgba(0,0,0,0.05)' }
          },
          x: { grid: { display: false } }
        }
      }
    });
  }
})();


/* ================================================================
   11. SCORE BAR ANIMATION (Complaint Details page)
================================================================ */
(function animateScoreBars() {
  document.querySelectorAll('.score-fill-big').forEach(bar => {
    const target = bar.dataset.score || 0;
    bar.style.width = '0%';
    setTimeout(() => {
      bar.style.width = target + '%';
    }, 300);
  });
})();


/* ================================================================
   12. SEARCH INPUT — Submit on Enter (Admin Complaints)
================================================================ */
(function initSearchSubmit() {
  const searchInput = document.getElementById('searchInput');
  const filterForm  = document.getElementById('adminFilterForm');
  if (!searchInput || !filterForm) return;

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      filterForm.submit();
    }
  });
})();


/* ================================================================
   13. SMOOTH SCROLL (Landing page anchors)
================================================================ */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
