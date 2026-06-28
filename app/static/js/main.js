/**
 * ============================================================
 *  AI Event Planner — Main JavaScript
 *  Production-quality helpers for the SaaS dashboard UI.
 * ============================================================
 */

/* ----------------------------------------------------------
 * 1. AOS (Animate On Scroll) Initialization
 * -------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 600, once: true, offset: 50 });
    }
});

/* ----------------------------------------------------------
 * 2. Sidebar Toggle
 *    • Toggles `.collapsed` on #sidebar
 *    • Persists state in localStorage
 *    • Adjusts main-content margin for the transition
 *    • Handles Bootstrap offcanvas for mobile viewports
 * -------------------------------------------------------- */
const SIDEBAR_KEY = 'sidebarCollapsed';

function initSidebar() {
    const sidebar      = document.getElementById('sidebar');
    const toggleBtn    = document.getElementById('sidebarToggle');
    const mainContent  = document.getElementById('mainContent');
    if (!sidebar || !toggleBtn) return;

    // Restore saved state
    const saved = localStorage.getItem(SIDEBAR_KEY);
    if (saved === 'true') {
        sidebar.classList.add('collapsed');
        if (mainContent) mainContent.classList.add('sidebar-collapsed');
    }

    // Desktop toggle
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem(SIDEBAR_KEY, isCollapsed);
        if (mainContent) mainContent.classList.toggle('sidebar-collapsed', isCollapsed);
    });

    // Mobile offcanvas
    const mobileToggle = document.getElementById('mobileMenuToggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            const offcanvas = bootstrap.Offcanvas.getOrCreateInstance(
                document.getElementById('mobileSidebar')
            );
            offcanvas.toggle();
        });
    }
}

document.addEventListener('DOMContentLoaded', initSidebar);

/* ----------------------------------------------------------
 * 3. Toast Notification System
 *    showToast(message, type?, duration?)
 *    Types: success | error | warning | info
 * -------------------------------------------------------- */
const TOAST_ICONS = {
    success : 'bi-check-circle-fill',
    error   : 'bi-x-circle-fill',
    warning : 'bi-exclamation-triangle-fill',
    info    : 'bi-info-circle-fill',
};

const TOAST_COLORS = {
    success : '#10b981',
    error   : '#ef4444',
    warning : '#f59e0b',
    info    : '#3b82f6',
};

function getToastContainer() {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Dynamically create and show a Bootstrap toast.
 * @param {string}  message  — text to display
 * @param {string}  type     — success | error | warning | info
 * @param {number}  duration — auto-hide delay in ms
 */
function showToast(message, type = 'success', duration = 3000) {
    const container = getToastContainer();
    const icon      = TOAST_ICONS[type]  || TOAST_ICONS.info;
    const color     = TOAST_COLORS[type] || TOAST_COLORS.info;

    const toastEl = document.createElement('div');
    toastEl.className = 'toast align-items-center border-0 mb-2';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.style.cssText = `
        border-left: 4px solid ${color};
        animation: slideInRight 0.35s ease;
    `;

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center gap-2">
                <i class="bi ${icon}" style="color:${color};font-size:1.15rem"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close me-2 m-auto"
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>`;

    container.appendChild(toastEl);

    const bsToast = new bootstrap.Toast(toastEl, { delay: duration });
    bsToast.show();

    // Remove element from DOM after it hides
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

// Inject slide-in keyframe once
(function injectToastAnimation() {
    if (document.getElementById('toast-animation-style')) return;
    const style = document.createElement('style');
    style.id = 'toast-animation-style';
    style.textContent = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to   { transform: translateX(0);    opacity: 1; }
        }`;
    document.head.appendChild(style);
})();

/* ----------------------------------------------------------
 * 4. API Helper
 *    apiRequest(url, method?, data?)
 *    • JSON fetch wrapper
 *    • Reads CSRF token from <meta name="csrf-token">
 *    • Shows toasts on errors
 * -------------------------------------------------------- */

/**
 * Get the CSRF token from the page <meta> tag.
 * @returns {string|null}
 */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : null;
}

/**
 * Perform an API request with JSON body.
 * @param {string}      url    — endpoint path or full URL
 * @param {string}      method — HTTP verb (GET, POST, PUT, DELETE …)
 * @param {object|null} data   — request body (will be JSON-stringified)
 * @returns {Promise<object>}  — parsed JSON response
 */
async function apiRequest(url, method = 'GET', data = null) {
    const headers = {
        'Content-Type' : 'application/json',
        'Accept'       : 'application/json',
    };
    const csrf = getCsrfToken();
    if (csrf) headers['X-CSRFToken'] = csrf;

    const options = { method, headers };
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const msg = errorData.message || errorData.error || `Request failed (${response.status})`;
            showToast(msg, 'error');
            throw new Error(msg);
        }

        // Handle 204 No Content
        if (response.status === 204) return {};

        return await response.json();
    } catch (err) {
        if (err.name === 'TypeError') {
            // Network error
            showToast('Network error — please check your connection.', 'error');
        }
        throw err;
    }
}

/* ----------------------------------------------------------
 * 5. Chart.js Helpers
 *    createChart(canvasId, type, labels, datasets, options?)
 * -------------------------------------------------------- */
const CHART_COLORS = {
    purple : '#6c63ff',
    blue   : '#3b82f6',
    green  : '#10b981',
    yellow : '#f59e0b',
    red    : '#ef4444',
    cyan   : '#06b6d4',
};

const CHART_COLOR_ARRAY = Object.values(CHART_COLORS);

/**
 * Create (or re-create) a Chart.js chart.
 * @param {string}   canvasId  — <canvas> element id
 * @param {string}   type      — chart type (bar, line, doughnut …)
 * @param {string[]} labels    — x-axis labels
 * @param {object[]} datasets  — Chart.js dataset objects
 * @param {object}   options   — extra Chart.js options (merged)
 * @returns {Chart}
 */
function createChart(canvasId, type, labels, datasets, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.warn(`[createChart] Canvas #${canvasId} not found.`);
        return null;
    }

    // Destroy existing chart on this canvas to avoid "Canvas is already in use"
    const existing = Chart.getChart(canvas);
    if (existing) existing.destroy();

    // Apply default colors if not set
    datasets.forEach((ds, i) => {
        if (!ds.backgroundColor) {
            ds.backgroundColor = CHART_COLOR_ARRAY[i % CHART_COLOR_ARRAY.length];
        }
        if (!ds.borderColor && (type === 'line' || type === 'radar')) {
            ds.borderColor = CHART_COLOR_ARRAY[i % CHART_COLOR_ARRAY.length];
        }
    });

    const defaultOptions = {
        responsive          : true,
        maintainAspectRatio : false,
        plugins: {
            legend: {
                labels: {
                    font      : { family: "'Inter', sans-serif", size: 12 },
                    usePointStyle : true,
                    padding   : 16,
                },
            },
            tooltip: {
                backgroundColor : 'rgba(15, 16, 35, 0.9)',
                titleFont       : { family: "'Inter', sans-serif", size: 13 },
                bodyFont        : { family: "'Inter', sans-serif", size: 12 },
                padding         : 12,
                cornerRadius    : 8,
                displayColors   : true,
            },
        },
        scales: ['bar', 'line'].includes(type) ? {
            x: {
                grid : { display: false },
                ticks: { font: { family: "'Inter', sans-serif", size: 11 } },
            },
            y: {
                grid : { color: 'rgba(0,0,0,0.06)' },
                ticks: { font: { family: "'Inter', sans-serif", size: 11 } },
                beginAtZero: true,
            },
        } : {},
    };

    // Deep-merge user options over defaults
    const merged = deepMerge(defaultOptions, options);

    return new Chart(canvas, { type, data: { labels, datasets }, options: merged });
}

/** Recursively merge source into target. */
function deepMerge(target, source) {
    const out = { ...target };
    for (const key of Object.keys(source)) {
        if (
            source[key] &&
            typeof source[key] === 'object' &&
            !Array.isArray(source[key]) &&
            target[key] &&
            typeof target[key] === 'object'
        ) {
            out[key] = deepMerge(target[key], source[key]);
        } else {
            out[key] = source[key];
        }
    }
    return out;
}

/* ----------------------------------------------------------
 * 6. Modal Form Handler
 *    setupModalForm(modalId, formId, submitUrl, onSuccess)
 * -------------------------------------------------------- */

/**
 * Wire a Bootstrap modal form for AJAX submission.
 * @param {string}   modalId    — modal element id
 * @param {string}   formId     — <form> element id inside the modal
 * @param {string}   submitUrl  — API endpoint for POST
 * @param {Function} onSuccess  — callback(responseData)
 */
function setupModalForm(modalId, formId, submitUrl, onSuccess) {
    const modal = document.getElementById(modalId);
    const form  = document.getElementById(formId);
    if (!modal || !form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        // Bootstrap custom validation
        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const submitBtn     = form.querySelector('[type="submit"]');
        const originalLabel = submitBtn ? submitBtn.innerHTML : '';

        try {
            // Loading state
            if (submitBtn) {
                submitBtn.disabled  = true;
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-1" role="status"
                          aria-hidden="true"></span> Saving…`;
            }

            const formData = new FormData(form);
            const payload  = Object.fromEntries(formData.entries());

            const result = await apiRequest(submitUrl, 'POST', payload);

            showToast(result.message || 'Saved successfully!', 'success');

            // Close modal and reset
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
            form.reset();
            form.classList.remove('was-validated');

            if (typeof onSuccess === 'function') onSuccess(result);
        } catch (err) {
            showToast(err.message || 'An error occurred.', 'error');
        } finally {
            if (submitBtn) {
                submitBtn.disabled  = false;
                submitBtn.innerHTML = originalLabel;
            }
        }
    });
}

/* ----------------------------------------------------------
 * 7. Confirm Delete
 *    confirmDelete(itemName, deleteUrl, redirectUrl)
 * -------------------------------------------------------- */

/**
 * Show a confirmation modal, then issue a DELETE request.
 * @param {string} itemName    — human-readable name shown in prompt
 * @param {string} deleteUrl   — API endpoint for DELETE
 * @param {string} redirectUrl — URL to navigate to on success
 */
function confirmDelete(itemName, deleteUrl, redirectUrl) {
    // Create or reuse a global delete-confirm modal
    let modalEl = document.getElementById('deleteConfirmModal');
    if (!modalEl) {
        modalEl = document.createElement('div');
        modalEl.id = 'deleteConfirmModal';
        modalEl.className = 'modal fade';
        modalEl.tabIndex = -1;
        modalEl.innerHTML = `
            <div class="modal-dialog modal-dialog-centered modal-sm">
                <div class="modal-content border-0 shadow">
                    <div class="modal-body text-center p-4">
                        <i class="bi bi-exclamation-triangle-fill text-danger"
                           style="font-size:2.5rem"></i>
                        <h5 class="mt-3 mb-2">Delete confirmation</h5>
                        <p class="text-secondary mb-0" id="deleteConfirmText"></p>
                    </div>
                    <div class="modal-footer justify-content-center border-0 pt-0 pb-4">
                        <button class="btn btn-light btn-sm px-4"
                                data-bs-dismiss="modal">Cancel</button>
                        <button class="btn btn-danger btn-sm px-4"
                                id="deleteConfirmBtn">Delete</button>
                    </div>
                </div>
            </div>`;
        document.body.appendChild(modalEl);
    }

    document.getElementById('deleteConfirmText').textContent =
        `Are you sure you want to delete "${itemName}"? This cannot be undone.`;

    const bsModal   = new bootstrap.Modal(modalEl);
    const confirmBtn = document.getElementById('deleteConfirmBtn');

    // Remove any previous handler
    const newBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);

    newBtn.addEventListener('click', async () => {
        newBtn.disabled  = true;
        newBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;
        try {
            await apiRequest(deleteUrl, 'DELETE');
            bsModal.hide();
            showToast(`"${itemName}" deleted.`, 'success');
            if (redirectUrl) {
                setTimeout(() => (window.location.href = redirectUrl), 600);
            }
        } catch {
            newBtn.disabled = false;
            newBtn.textContent = 'Delete';
        }
    });

    bsModal.show();
}

/* ----------------------------------------------------------
 * 8. Counter Animation
 *    animateCounter(element, target, duration?)
 * -------------------------------------------------------- */

/**
 * Smoothly animate a number from 0 → target inside an element.
 * @param {HTMLElement|string} element  — DOM element or selector
 * @param {number}             target   — final value
 * @param {number}             duration — animation time in ms
 */
function animateCounter(element, target, duration = 1000) {
    const el    = typeof element === 'string' ? document.querySelector(element) : element;
    if (!el) return;

    const start = performance.now();
    const from  = 0;

    function update(now) {
        const elapsed  = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // Ease-out quad
        const ease     = 1 - (1 - progress) * (1 - progress);
        const current  = Math.round(from + (target - from) * ease);

        el.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/** Auto-animate any element with `data-count-to` attribute. */
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-count-to]').forEach((el) => {
        const target   = parseInt(el.dataset.countTo, 10);
        const duration = parseInt(el.dataset.countDuration, 10) || 1000;
        if (!isNaN(target)) animateCounter(el, target, duration);
    });
});

/* ----------------------------------------------------------
 * 9. Search / Filter
 *    setupSearch(inputId, itemsSelector, searchProperty)
 * -------------------------------------------------------- */

/**
 * Real-time filtering of displayed items.
 * @param {string} inputId        — search <input> id
 * @param {string} itemsSelector  — CSS selector for filterable items
 * @param {string} searchProperty — data-attribute name to match against
 *                                   (defaults to textContent)
 */
function setupSearch(inputId, itemsSelector, searchProperty) {
    const input = document.getElementById(inputId);
    if (!input) return;

    let debounceTimer = null;

    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = input.value.trim().toLowerCase();
            const items = document.querySelectorAll(itemsSelector);

            items.forEach((item) => {
                const text = searchProperty
                    ? (item.dataset[searchProperty] || '').toLowerCase()
                    : item.textContent.toLowerCase();

                item.style.display = text.includes(query) ? '' : 'none';
            });
        }, 250); // 250 ms debounce
    });
}

/* ----------------------------------------------------------
 * 10. Theme Toggle
 *     toggleTheme()
 *     Switches data-bs-theme between 'light' and 'dark'.
 * -------------------------------------------------------- */
const THEME_KEY = 'theme';

function applyTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem(THEME_KEY, theme);

    // Update Chart.js defaults if loaded
    if (typeof Chart !== 'undefined') {
        const fontColor = theme === 'dark' ? '#cbd5e1' : '#64748b';
        const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)';

        Chart.defaults.color                     = fontColor;
        Chart.defaults.scale.grid.color           = gridColor;
        Chart.defaults.plugins.legend.labels.color = fontColor;

        // Re-render all active charts
        Object.values(Chart.instances || {}).forEach((c) => c.update());
    }

    // Toggle icon
    const icon = document.getElementById('themeIcon');
    if (icon) {
        icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill';
    }
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-bs-theme') || 'light';
    applyTheme(current === 'light' ? 'dark' : 'light');
}

// Restore saved theme on load
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem(THEME_KEY) || 'light';
    applyTheme(saved);

    const themeBtn = document.getElementById('themeToggleBtn');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
});

/* ----------------------------------------------------------
 * 11. Active Nav Highlighting
 *     Marks the sidebar link whose href matches the current URL.
 * -------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;

    document.querySelectorAll('#sidebar .nav-link, #mobileSidebar .nav-link').forEach((link) => {
        const href = link.getAttribute('href');
        if (!href) return;

        // Exact match or starts-with for nested routes
        if (currentPath === href || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');

            // Expand parent collapse if the link is nested
            const parentCollapse = link.closest('.collapse');
            if (parentCollapse) {
                parentCollapse.classList.add('show');
                const toggler = document.querySelector(`[data-bs-target="#${parentCollapse.id}"]`);
                if (toggler) toggler.setAttribute('aria-expanded', 'true');
            }
        }
    });
});

/* ----------------------------------------------------------
 * 12. Skeleton Loading
 *     showSkeleton(containerId, count?)
 *     hideSkeleton(containerId)
 * -------------------------------------------------------- */

/**
 * Inject skeleton placeholder cards.
 * @param {string} containerId — container element id
 * @param {number} count       — number of skeleton cards
 */
function showSkeleton(containerId, count = 3) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = '';
    for (let i = 0; i < count; i++) {
        html += `
            <div class="skeleton-item card border-0 mb-3" style="border-radius:12px">
                <div class="card-body">
                    <div class="skeleton-line mb-3" style="width:65%;height:14px"></div>
                    <div class="skeleton-line mb-2" style="width:90%;height:10px"></div>
                    <div class="skeleton-line mb-2" style="width:80%;height:10px"></div>
                    <div class="skeleton-line"      style="width:40%;height:10px"></div>
                </div>
            </div>`;
    }
    container.innerHTML = html;
}

/**
 * Remove skeleton placeholders and reveal content.
 * @param {string} containerId
 */
function hideSkeleton(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.querySelectorAll('.skeleton-item').forEach((el) => el.remove());
}

// Inject skeleton CSS once
(function injectSkeletonStyles() {
    if (document.getElementById('skeleton-style')) return;
    const style = document.createElement('style');
    style.id = 'skeleton-style';
    style.textContent = `
        .skeleton-line {
            background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
            background-size: 200% 100%;
            animation: skeletonShimmer 1.4s ease infinite;
            border-radius: 6px;
        }
        @keyframes skeletonShimmer {
            0%   { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }`;
    document.head.appendChild(style);
})();
