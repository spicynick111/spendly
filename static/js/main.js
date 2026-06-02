// AI auto-categorize: fires when user leaves the description field
const descInput = document.getElementById('description');
const categorySelect = document.getElementById('category');
const aiCatHint = document.getElementById('ai-cat-hint');

if (descInput && categorySelect) {
    descInput.addEventListener('blur', async () => {
        const desc = descInput.value.trim();
        if (desc.length < 3) return;
        try {
            const res = await fetch('/api/ai/categorize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: desc }),
            });
            const data = await res.json();
            if (data.category && data.ai) {
                categorySelect.value = data.category;
                if (aiCatHint) aiCatHint.textContent = `AI suggested: ${data.category}`;
            }
        } catch (_) {}
    });
}

// Natural language expense parsing via Claude tool use
const nlInput = document.getElementById('nl-input');
const nlBtn = document.getElementById('nl-parse-btn');
const nlStatus = document.getElementById('nl-status');

if (nlBtn && nlInput) {
    nlBtn.addEventListener('click', async () => {
        const text = nlInput.value.trim();
        if (!text) return;

        nlBtn.textContent = 'Parsing…';
        nlBtn.disabled = true;
        if (nlStatus) nlStatus.textContent = '';

        try {
            const res = await fetch('/api/ai/parse-nl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'parse failed');
            }
            const data = await res.json();

            if (data.amount !== undefined) document.getElementById('amount').value = data.amount;
            if (data.category) document.getElementById('category').value = data.category;
            if (data.description) document.getElementById('description').value = data.description;
            if (data.date) document.getElementById('date').value = data.date;

            if (nlStatus) {
                nlStatus.textContent = '✓ Filled from AI — review before saving';
                nlStatus.style.color = 'var(--accent)';
            }
        } catch (e) {
            if (nlStatus) {
                nlStatus.textContent = e.message.includes('API_KEY')
                    ? 'Add ANTHROPIC_API_KEY to .env to use AI parsing.'
                    : 'Could not parse — please fill manually.';
                nlStatus.style.color = 'var(--danger)';
            }
        } finally {
            nlBtn.textContent = 'Fill with AI';
            nlBtn.disabled = false;
        }
    });

    // Also trigger on Enter in the NL input
    nlInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); nlBtn.click(); }
    });
}

// AI monthly insights — loaded async on dashboard
async function loadInsights() {
    const el = document.getElementById('ai-insights-content');
    if (!el) return;
    try {
        const res = await fetch('/api/ai/insights');
        const data = await res.json();
        el.textContent = data.insight || 'No insights available.';
        el.classList.remove('loading');
    } catch (_) {
        el.textContent = 'Could not load insights.';
        el.classList.remove('loading');
    }
}

document.addEventListener('DOMContentLoaded', loadInsights);
