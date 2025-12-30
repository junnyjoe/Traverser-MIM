/**
 * Bible Verse Drawing Application
 * Main JavaScript - User interactions
 */

// ============== DOM ELEMENTS ==============
const drawSection = document.getElementById('draw-section');
const verseSection = document.getElementById('verse-section');
const drawForm = document.getElementById('draw-form');
const emailInput = document.getElementById('email');
const submitBtn = document.getElementById('submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const errorMessage = document.getElementById('error-message');
const firstNameInput = document.getElementById('first-name');
const lastNameInput = document.getElementById('last-name');
const verseText = document.getElementById('verse-text');
const verseReference = document.getElementById('verse-reference');
const alreadyDrawnNotice = document.getElementById('already-drawn-notice');
const newDrawBtn = document.getElementById('new-draw-btn');
// Removed text-download button; keep image-download button
const downloadImageBtn = document.getElementById('download-image-btn');
const posterPreview = document.getElementById('poster-preview');
const posterVerseText = document.getElementById('poster-verse-text');
const posterVerseRef = document.getElementById('poster-verse-ref');

// ============== EMAIL VALIDATION ==============
/**
 * Validate email format using regex
 * @param {string} email - Email address to validate
 * @returns {boolean} - True if email is valid
 */
function isValidEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
}

// ============== UI STATE MANAGEMENT ==============
/**
 * Show loading state on submit button
 */
function showLoading() {
    submitBtn.disabled = true;
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
}

/**
 * Hide loading state on submit button
 */
function hideLoading() {
    submitBtn.disabled = false;
    btnText.classList.remove('hidden');
    btnLoader.classList.add('hidden');
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');

    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.classList.add('hidden');
}

/**
 * Display the drawn verse
 * @param {object} verse - Verse object with text and reference
 * @param {boolean} alreadyDrawn - Whether this verse was already drawn
 */
function displayVerse(verse, alreadyDrawn) {
    // Hide draw section, show verse section
    drawSection.classList.add('hidden');
    verseSection.classList.remove('hidden');

    // Show/hide already drawn notice
    if (alreadyDrawn) {
        alreadyDrawnNotice.classList.remove('hidden');
    } else {
        alreadyDrawnNotice.classList.add('hidden');
    }

    // Populate verse content (use standalone elements if present)
    if (verseText) {
        verseText.textContent = `"${verse.text}"`;
    }
    if (verseReference) {
        verseReference.textContent = `— ${verse.reference}`;
    }

    // Update poster preview (if present)
    if (posterVerseText) {
        posterVerseText.textContent = verse.text;
    }
    if (posterVerseRef) {
        posterVerseRef.textContent = verse.reference;
    }
    if (posterPreview) {
        posterPreview.classList.remove('hidden');
    }

    // Scroll to verse section
    verseSection.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // Enable image download button (if present)
    if (downloadImageBtn) {
        downloadImageBtn.disabled = false;
    }
}

/**
 * Reset to initial state (show draw form)
 */
function resetToDrawForm() {
    verseSection.classList.add('hidden');
    drawSection.classList.remove('hidden');
    emailInput.value = '';
    if (firstNameInput) firstNameInput.value = '';
    if (lastNameInput) lastNameInput.value = '';
    emailInput.focus();
    if (posterPreview) {
        posterPreview.classList.add('hidden');
    }
}

/**
 * Generate a text file for the currently displayed verse and trigger download
 */
function downloadVerse() {
    // Note: text-download feature removed — kept for historical reference.
    // If you later want to re-enable text download, recreate a safe content string
    // from poster preview nodes (`posterVerseText` / `posterVerseRef`).
    return;
}

/**
 * Wrap text into lines for canvas
 */
function wrapText(ctx, text, maxWidth) {
    const words = text.split(' ');
    const lines = [];
    let line = '';

    for (let n = 0; n < words.length; n++) {
        const testLine = line + (line ? ' ' : '') + words[n];
        const metrics = ctx.measureText(testLine);
        const testWidth = metrics.width;
        if (testWidth > maxWidth && line) {
            lines.push(line);
            line = words[n];
        } else {
            line = testLine;
        }
    }
    if (line) lines.push(line);
    return lines;
}

/**
 * Generate an image (PNG) with the background and the displayed verse text, then download it.
 * Uses `/static/images/verse_bg.jpg` as background.
 */
async function downloadVerseAsImage() {
    try {
        const bgUrl = '/static/images/verse_bg.jpg';

        // Create image and wait for load
        const img = new Image();
        img.crossOrigin = 'anonymous';
        const imgLoaded = new Promise((resolve, reject) => {
            img.onload = () => resolve();
            img.onerror = () => reject(new Error('Impossible de charger l\'image de fond'));
        });
        img.src = bgUrl;
        await imgLoaded;

        const canvas = document.createElement('canvas');
        // Use background image dimensions
        canvas.width = img.naturalWidth || 1200;
        canvas.height = img.naturalHeight || 800;
        const ctx = canvas.getContext('2d');

        // Draw background
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Prepare text
        const fullTextRaw = (posterVerseText && posterVerseText.textContent) || (verseText && verseText.textContent) || '';
        const fullText = fullTextRaw ? fullTextRaw.replace(/^"|"$/g, '') : '';
        const reference = (posterVerseRef && posterVerseRef.textContent) || (verseReference && verseReference.textContent) || '';

        // Text box area - position text in the middle section (below title, above logo)
        const paddingX = canvas.width * 0.08;
        const boxWidth = canvas.width - paddingX * 2;

        // Verse font - white text
        const fontSize = Math.floor(canvas.width / 24);
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // Draw verse text in WHITE
        ctx.font = `bold ${fontSize}px Inter, sans-serif`;
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = 'rgba(0,0,0,0.3)';
        ctx.lineWidth = Math.max(1, Math.floor(fontSize / 20));

        const lines = wrapText(ctx, fullText, boxWidth);

        // Calculate vertical position - center in the middle area of the image
        const lineHeight = fontSize * 1.5;
        const totalHeight = lines.length * lineHeight + lineHeight;
        let startY = canvas.height * 0.45; // Position in middle area

        // Draw verse lines
        for (let i = 0; i < lines.length; i++) {
            const y = startY + i * lineHeight;
            ctx.strokeText(lines[i], canvas.width / 2, y);
            ctx.fillText(lines[i], canvas.width / 2, y);
        }

        // Draw reference in YELLOW/GOLD color
        const refFontSize = Math.floor(fontSize * 0.85);
        ctx.font = `bold ${refFontSize}px Inter, sans-serif`;
        ctx.fillStyle = '#FFD700'; // Gold color
        ctx.strokeStyle = 'rgba(0,0,0,0.3)';
        const refY = startY + lines.length * lineHeight + refFontSize * 0.8;
        ctx.strokeText(reference, canvas.width / 2, refY);
        ctx.fillText(reference, canvas.width / 2, refY);

        // Trigger download
        const dataUrl = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = dataUrl;
        // safe filename from reference
        let filename = reference.replace(/[^a-z0-9\-_. ]/gi, '_').trim();
        if (!filename) filename = 'verset_image';
        a.download = `${filename}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

    } catch (err) {
        console.error(err);
        showError('Impossible de générer l\'image. Vérifiez que le fichier de fond existe.');
    }
}

// ============== API CALLS ==============
/**
 * Draw a verse for the given email
 * @param {string} email - User's email address
 */
async function drawVerse(email) {
    try {
        const response = await fetch('/api/draw-verse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                first_name: (firstNameInput && firstNameInput.value.trim()) || '',
                last_name: (lastNameInput && lastNameInput.value.trim()) || ''
            }),
        });

        const data = await response.json();

        if (data.success) {
            displayVerse(data.verse, data.already_drawn);
        } else {
            showError(data.error || 'Une erreur est survenue. Veuillez réessayer.');
        }
    } catch (error) {
        console.error('API Error:', error);
        showError('Erreur de connexion. Veuillez vérifier votre connexion internet.');
    }
}

// ============== EVENT LISTENERS ==============

// Form submission
drawForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const firstName = firstNameInput ? firstNameInput.value.trim() : '';
    const lastName = lastNameInput ? lastNameInput.value.trim() : '';
    const email = emailInput.value.trim();

    // Client-side validation
    if (!firstName) {
        showError('Veuillez entrer votre prénom.');
        if (firstNameInput) firstNameInput.focus();
        return;
    }
    if (!lastName) {
        showError('Veuillez entrer votre nom.');
        if (lastNameInput) lastNameInput.focus();
        return;
    }
    if (!email) {
        showError('Veuillez entrer votre adresse e-mail.');
        emailInput.focus();
        return;
    }

    if (!isValidEmail(email)) {
        showError('Veuillez entrer une adresse e-mail valide.');
        emailInput.focus();
        return;
    }

    // Hide any existing errors
    hideError();

    // Show loading state
    showLoading();

    // Call API
    await drawVerse(email);

    // Hide loading state
    hideLoading();
});

// New draw button (try with different email)
newDrawBtn.addEventListener('click', () => {
    resetToDrawForm();
});

// Text download removed — no event listener for `download-btn` anymore.

// Download image button
if (downloadImageBtn) {
    downloadImageBtn.disabled = true;
    downloadImageBtn.addEventListener('click', () => {
        downloadVerseAsImage();
    });
}

// Real-time email validation feedback
emailInput.addEventListener('input', () => {
    const email = emailInput.value.trim();

    if (email && !isValidEmail(email)) {
        emailInput.style.borderColor = '#ea4335';
    } else {
        emailInput.style.borderColor = '';
    }
});

// Hide error on new input
emailInput.addEventListener('focus', () => {
    hideError();
});

// ============== INITIALIZATION ==============
document.addEventListener('DOMContentLoaded', () => {
    // Focus on email input
    emailInput.focus();

    console.log('🙏 Bible Verse Drawing App initialized');
});
