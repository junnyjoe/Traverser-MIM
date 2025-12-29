/**
 * Bible Verse Drawing Application
 * Admin JavaScript - Dashboard and verse management
 */

// ============== DOM ELEMENTS ==============
const loginSection = document.getElementById('login-section');
const dashboardSection = document.getElementById('dashboard-section');
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const addVerseForm = document.getElementById('add-verse-form');
const verseTextInput = document.getElementById('verse-text');
const verseReferenceInput = document.getElementById('verse-reference');
const addMessage = document.getElementById('add-message');
const versesList = document.getElementById('verses-list');
const totalVersesSpan = document.getElementById('total-verses');
const totalDrawsSpan = document.getElementById('total-draws');
const drawsList = document.getElementById('draws-list');

// ============== STATE ==============
let isLoggedIn = false;

// ============== UI HELPERS ==============
/**
 * Show a message element with given type and text
 * @param {HTMLElement} element - Message element
 * @param {string} text - Message text
 * @param {string} type - 'success' or 'error'
 */
function showMessage(element, text, type) {
    element.textContent = text;
    element.className = `message ${type}`;
    element.classList.remove('hidden');

    // Auto-hide success messages
    if (type === 'success') {
        setTimeout(() => {
            element.classList.add('hidden');
        }, 3000);
    }
}

/**
 * Hide a message element
 * @param {HTMLElement} element - Message element
 */
function hideMessage(element) {
    element.classList.add('hidden');
}

/**
 * Show dashboard and hide login
 */
function showDashboard() {
    loginSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');
    isLoggedIn = true;
}

/**
 * Show login and hide dashboard
 */
function showLogin() {
    dashboardSection.classList.add('hidden');
    loginSection.classList.remove('hidden');
    isLoggedIn = false;
}

// ============== API CALLS ==============

/**
 * Check if admin is logged in
 */
async function checkAuth() {
    try {
        const response = await fetch('/api/admin/check', {
            credentials: 'include'
        });
        const data = await response.json();

        if (data.logged_in) {
            showDashboard();
            loadVerses();
        } else {
            showLogin();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        showLogin();
    }
}

/**
 * Login to admin
 * @param {string} username
 * @param {string} password
 */
async function login(username, password) {
    try {
        const response = await fetch('/api/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });

        const data = await response.json();

        if (data.success) {
            showDashboard();
            loadVerses();
            return true;
        } else {
            showMessage(loginError, data.error || 'Identifiants incorrects', 'error');
            return false;
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage(loginError, 'Erreur de connexion', 'error');
        return false;
    }
}

/**
 * Logout from admin
 */
async function logout() {
    try {
        await fetch('/api/admin/logout', {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    showLogin();
    usernameInput.value = '';
    passwordInput.value = '';
}

/**
 * Load all verses and update the list
 */
async function loadVerses() {
    try {
        const response = await fetch('/api/admin/verses', {
            credentials: 'include'
        });

        if (response.status === 401) {
            showLogin();
            return;
        }

        const data = await response.json();

        if (data.success) {
            renderVersesList(data.verses);
            updateStats(data.stats);
            // Also load draws for admin view
            loadDraws();
        }
    } catch (error) {
        console.error('Load verses error:', error);
        versesList.innerHTML = '<p class="loading-text">Erreur de chargement</p>';
    }
}

/**
 * Load all draws (emails) for admin
 */
async function loadDraws() {
    if (!drawsList) return;
    try {
        const response = await fetch('/api/admin/draws', { credentials: 'include' });
        if (response.status === 401) {
            showLogin();
            return;
        }
        const data = await response.json();
        if (data.success) {
            renderDrawsList(data.draws);
        } else {
            drawsList.innerHTML = '<p class="empty-text">Erreur de chargement des tirages</p>';
        }
    } catch (err) {
        console.error('Load draws error:', err);
        drawsList.innerHTML = '<p class="empty-text">Erreur de chargement des tirages</p>';
    }
}

/**
 * Render draws list (email, reference, date)
 * @param {Array} draws
 */
function renderDrawsList(draws) {
    if (!draws || draws.length === 0) {
        drawsList.innerHTML = '<p class="empty-text">Aucun tirage trouvé.</p>';
        return;
    }

    // Build a simple table
    const rows = draws.map(d => `
        <tr>
            <td>${escapeHtml(d.email)}</td>
            <td>${escapeHtml(((d.first_name||'') + ' ' + (d.last_name||'')).trim())}</td>
            <td>${escapeHtml(d.reference || '')}</td>
            <td>${escapeHtml(d.drawn_at)}</td>
        </tr>
    `).join('');

    drawsList.innerHTML = `
        <div style="overflow:auto">
        <table style="width:100%;border-collapse:collapse">
            <thead>
                <tr style="text-align:left;font-weight:600;padding:8px">
                    <th>Email</th>
                    <th>Nom complet</th>
                    <th>Référence</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                ${rows}
            </tbody>
        </table>
        </div>
    `;
}

/**
 * Add a new verse
 * @param {string} text - Verse text
 * @param {string} reference - Verse reference
 */
async function addVerse(text, reference) {
    try {
        const response = await fetch('/api/admin/verses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text, reference }),
            credentials: 'include'
        });

        const data = await response.json();

        if (data.success) {
            showMessage(addMessage, 'Verset ajouté avec succès !', 'success');
            verseTextInput.value = '';
            verseReferenceInput.value = '';
            loadVerses();
            return true;
        } else {
            showMessage(addMessage, data.error || 'Erreur lors de l\'ajout', 'error');
            return false;
        }
    } catch (error) {
        console.error('Add verse error:', error);
        showMessage(addMessage, 'Erreur de connexion', 'error');
        return false;
    }
}

/**
 * Delete a verse
 * @param {number} verseId - ID of the verse to delete
 */
async function deleteVerse(verseId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce verset ?')) {
        return;
    }

    try {
        const response = await fetch(`/api/admin/verses/${verseId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        const data = await response.json();

        if (data.success) {
            loadVerses();
        } else {
            alert(data.error || 'Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Delete verse error:', error);
        alert('Erreur de connexion');
    }
}

// ============== RENDER FUNCTIONS ==============

/**
 * Render the verses list
 * @param {Array} verses - Array of verse objects
 */
function renderVersesList(verses) {
    if (!verses || verses.length === 0) {
        versesList.innerHTML = '<p class="empty-text">Aucun verset. Ajoutez-en un !</p>';
        return;
    }

    versesList.innerHTML = verses.map(verse => `
        <div class="verse-item" data-id="${verse.id}">
            <div class="verse-item-content">
                <p class="verse-item-text">${escapeHtml(verse.text)}</p>
                <span class="verse-item-reference">${escapeHtml(verse.reference)}</span>
            </div>
            <div class="verse-item-actions">
                <button class="btn btn-danger delete-btn" data-id="${verse.id}">
                    Supprimer
                </button>
            </div>
        </div>
    `).join('');

    // Add delete event listeners
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const verseId = parseInt(e.target.dataset.id);
            deleteVerse(verseId);
        });
    });
}

/**
 * Update stats display
 * @param {object} stats - Stats object
 */
function updateStats(stats) {
    totalVersesSpan.textContent = stats.total_verses || 0;
    totalDrawsSpan.textContent = stats.total_draws || 0;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} - Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============== EVENT LISTENERS ==============

// Login form submission
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
        showMessage(loginError, 'Veuillez remplir tous les champs', 'error');
        return;
    }

    hideMessage(loginError);
    await login(username, password);
});

// Logout button
logoutBtn.addEventListener('click', () => {
    logout();
});

// Add verse form submission
addVerseForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const text = verseTextInput.value.trim();
    const reference = verseReferenceInput.value.trim();

    if (!text || !reference) {
        showMessage(addMessage, 'Veuillez remplir tous les champs', 'error');
        return;
    }

    hideMessage(addMessage);
    await addVerse(text, reference);
});

// Hide error on input
usernameInput.addEventListener('focus', () => hideMessage(loginError));
passwordInput.addEventListener('focus', () => hideMessage(loginError));

// ============== INITIALIZATION ==============
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    console.log('🔐 Admin panel initialized');
});
