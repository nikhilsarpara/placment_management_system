/**
 * Main JavaScript for Placement Management Platform
 * Handles: sidebar toggle, alert auto-dismiss, form validation, dynamic interactions
 */

document.addEventListener('DOMContentLoaded', function () {

  // ─── Sidebar Toggle (mobile) ──────────────────────────────
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    // Close sidebar on outside click
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ─── Auto-dismiss flash alerts ────────────────────────────
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  // ─── Alert close buttons ──────────────────────────────────
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.transition = 'opacity 0.3s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }
    });
  });

  // ─── Highlight active sidebar link ────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-link').forEach(link => {
    if (link.getAttribute('href') && currentPath.startsWith(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });

  // ─── Confirm before dangerous actions ────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      const msg = this.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  // ─── Skills input tag manager ─────────────────────────────
  const skillsInput = document.getElementById('skillsInput');
  const skillsHidden = document.getElementById('skillsHidden');
  const skillsDisplay = document.getElementById('skillsDisplay');
  if (skillsInput && skillsHidden && skillsDisplay) {
    skillsInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ',') {
        e.preventDefault();
        const val = this.value.trim().replace(/,$/, '');
        if (val) {
          addSkillTag(val);
          this.value = '';
        }
      }
    });

    function addSkillTag(skill) {
      const currentSkills = skillsHidden.value ? skillsHidden.value.split(',') : [];
      if (!currentSkills.includes(skill)) {
        currentSkills.push(skill);
        skillsHidden.value = currentSkills.join(',');
        const tag = document.createElement('span');
        tag.className = 'skill-tag';
        tag.innerHTML = `${skill} <button type="button" onclick="removeSkill(this, '${skill}')">&times;</button>`;
        skillsDisplay.appendChild(tag);
      }
    }

    // Populate existing skills on load
    if (skillsHidden.value) {
      skillsHidden.value.split(',').forEach(s => {
        if (s.trim()) {
          const tag = document.createElement('span');
          tag.className = 'skill-tag';
          tag.innerHTML = `${s.trim()} <button type="button" onclick="removeSkill(this, '${s.trim()}')">&times;</button>`;
          skillsDisplay.appendChild(tag);
        }
      });
    }
  }

  // ─── File upload preview ──────────────────────────────────
  document.querySelectorAll('input[type="file"][data-preview]').forEach(input => {
    const previewId = input.dataset.preview;
    const preview = document.getElementById(previewId);
    if (preview) {
      input.addEventListener('change', function () {
        const file = this.files[0];
        if (file && file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = e => {
            preview.src = e.target.result;
            preview.style.display = 'block';
          };
          reader.readAsDataURL(file);
        }
      });
    }
  });

  // ─── Animate stat numbers on load ────────────────────────
  document.querySelectorAll('.stat-value[data-value]').forEach(el => {
    const target = parseInt(el.dataset.value, 10);
    let current = 0;
    const increment = Math.ceil(target / 30);
    const timer = setInterval(() => {
      current = Math.min(current + increment, target);
      el.textContent = current.toLocaleString();
      if (current >= target) clearInterval(timer);
    }, 30);
  });

});

// Global helper for skill tag removal
function removeSkill(btn, skill) {
  const hidden = document.getElementById('skillsHidden');
  if (hidden) {
    hidden.value = hidden.value.split(',').filter(s => s !== skill).join(',');
  }
  btn.closest('.skill-tag').remove();
}
