// tabs behavior (ADDED)
function toggleNav(e, targetId) {
  // deactivate all tabs
  document.querySelectorAll('.nav-links').forEach(btn => {
    btn.classList.remove('active');
    btn.setAttribute('aria-selected', 'false');
  });

  // activate clicked tab
  e.currentTarget.classList.add('active');
  e.currentTarget.setAttribute('aria-selected', 'true');

  // hide all panels
  document.querySelectorAll('.nav-content').forEach(p => p.style.display = 'none');

  // show target panel
  const target = document.getElementById(targetId);
  if (target) target.style.display = 'block';
}
