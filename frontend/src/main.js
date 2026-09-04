import './style.css'

// The router
const routes = {
  'overview': '/views/overview.html',
  'action-queue': '/views/action-queue.html',
  'impact-simulator': '/views/impact-simulator.html',
  'category-deep-dive': '/views/category-deep-dive.html'
};

async function loadView(path) {
  const contentDiv = document.getElementById('app-content');
  const route = routes[path] || routes['overview'];
  
  try {
    const response = await fetch(route);
    if (!response.ok) throw new Error("Failed to load view");
    const html = await response.text();
    contentDiv.innerHTML = html;
    
    // Execute any scripts within the loaded HTML (since innerHTML doesn't execute script tags)
    const scripts = contentDiv.querySelectorAll('script');
    scripts.forEach(script => {
      const newScript = document.createElement('script');
      if (script.src) {
        newScript.src = script.src;
      } else {
        newScript.textContent = `(() => {\n${script.textContent}\n})();`;
      }
      document.body.appendChild(newScript);
      document.body.removeChild(newScript);
    });
    
    // Initialize view-specific logic
    if (path === 'overview' || path === '') {
      fetchDashboardKPIs();
    }

  } catch (error) {
    console.error(error);
    contentDiv.innerHTML = `<div class="p-lg text-error">Failed to load view.</div>`;
  }
  
  updateActiveNav(path);
}

// API Base URL — injected by Vercel via VITE_API_URL, defaults to localhost for dev
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchDashboardKPIs() {
  try {
    const res = await fetch(`${API_BASE}/api/v2/kpis?days=30`);
    if (res.ok) {
      const data = await res.json();
      console.log('Live KPIs from API:', data);
      // In a full implementation, we would querySelector and update the DOM elements here.
      // Example: document.getElementById('high-intent-metric').textContent = data.high_intent_users;
    }
  } catch (err) {
    console.warn("API Backend not reachable. Using mock UI data.", err);
  }
}

function updateActiveNav(path) {
  const nav = document.getElementById('sidebar-nav');
  const activeClasses = nav.dataset.activeClasses.trim();
  const defaultClasses = "text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface".trim();
  const baseClasses = "nav-link flex items-center gap-sm px-md py-sm rounded-xl transition-all".trim();
  
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.dataset.path === path) {
      link.className = `${baseClasses} ${activeClasses}`;
      link.setAttribute('aria-current', 'page');
    } else {
      link.className = `${baseClasses} ${defaultClasses}`;
      link.removeAttribute('aria-current');
    }
  });
}

function handleHashChange() {
  const path = window.location.hash.slice(1) || 'overview';
  loadView(path);
}

window.addEventListener('hashchange', handleHashChange);
window.addEventListener('DOMContentLoaded', handleHashChange);
