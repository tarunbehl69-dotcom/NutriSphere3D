/**
 * NutriSphere 3D - Global Client Application
 * Handles navigation state, API fetching, toast notifications, and demo mode.
 */

const NutriSphere = {
  apiBase: '/api',

  // Display user notifications
  showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const borderColors = {
      info: 'border-teal-200 bg-white text-teal-900 shadow-md',
      warn: 'border-amber-200 bg-white text-amber-900 shadow-md',
      error: 'border-rose-200 bg-white text-rose-900 shadow-md'
    };

    toast.className = `p-3.5 rounded-xl border text-xs font-medium transition-all duration-300 opacity-0 transform translate-y-2 ${borderColors[type] || borderColors.info}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.remove('opacity-0', 'translate-y-2');
    }, 10);

    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  // Check health status
  async checkHealth() {
    try {
      const res = await fetch(`${this.apiBase}/health`);
      return await res.json();
    } catch (e) {
      console.error('Health check failed:', e);
      return { status: 'offline' };
    }
  },

  // Server-validated authentication token helpers
  getToken() {
    return localStorage.getItem('nutrisphere_auth_token') || 'nutrisphere_dev_demo_token_secure_2026';
  },

  setToken(token) {
    localStorage.setItem('nutrisphere_auth_token', token);
  },

  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.getToken()}`
    };
  },

  // Quick-load demo report into localStorage for offline interactive viewing
  async loadDemoSession() {
    try {
      const res = await fetch(`${this.apiBase}/demo-report`);
      const data = await res.json();
      localStorage.setItem('nutrisphere_active_report', JSON.stringify(data));
      this.showToast('Synthetic Demo Report loaded successfully!', 'info');
      setTimeout(() => {
        window.location.href = '/results';
      }, 500);
    } catch (e) {
      this.showToast('Unable to load demo report.', 'error');
    }
  }
};

window.NutriSphere = NutriSphere;
