/**
 * TravelMate AI - Client Application Logic
 * Multilingual Wikimedia RAG Integration, Web Speech Voice Input & TTS Playback,
 * Session Context Memory, Trip Planner & Developer Debug Panel.
 */

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const sidebar = document.getElementById('sidebar');
    const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');
    const newChatBtn = document.getElementById('newChatBtn');

    const welcomeScreen = document.getElementById('welcomeScreen');
    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const voiceMicBtn = document.getElementById('voiceMicBtn');
    const recordingIndicator = document.getElementById('recordingIndicator');
    const uiLangSelect = document.getElementById('uiLangSelect');
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    
    const toggleDebugBtn = document.getElementById('toggleDebugBtn');
    const debugModal = document.getElementById('debugModal');
    const closeDebugBtn = document.getElementById('closeDebugBtn');
    const debugMetrics = document.getElementById('debugMetrics');

    const sidebarNavItems = document.querySelectorAll('.sidebar-nav-item');
    const viewPanels = document.querySelectorAll('.view-panel');
    const suggestionCards = document.querySelectorAll('.suggestion-card');
    const suggestPills = document.querySelectorAll('.suggest-pill');
    const quickDestBtns = document.querySelectorAll('.quick-dest-btn');

    const plannerForm = document.getElementById('plannerForm');
    const plannerResults = document.getElementById('plannerResults');
    const plannerEmptyState = document.getElementById('plannerEmptyState');

    const destSearchInput = document.getElementById('destSearchInput');
    const regionFilterTabs = document.getElementById('regionFilterTabs');
    const destinationGrid = document.getElementById('destinationGrid');

    let isRecording = false;
    let recognition = null;
    let activeRegion = 'all';
    let currentSessionContext = { current_destination: "", current_language: "en" };
    let lastDebugPayload = null;

    // Configure Marked JS
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    // --- 1. Sidebar Toggle & Navigation ---
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener('click', () => {
            sidebar.classList.remove('open');
        });
    }

    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            welcomeScreen.classList.remove('hidden');
            chatMessages.classList.add('hidden');
            chatMessages.innerHTML = '';
            userInput.value = '';
            userInput.style.height = 'auto';
            currentSessionContext = { current_destination: "", current_language: uiLangSelect.value };
            sidebar.classList.remove('open');
        });
    }

    sidebarNavItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetView = item.getAttribute('data-view');
            
            sidebarNavItems.forEach(i => i.classList.remove('active'));
            viewPanels.forEach(v => v.classList.remove('active'));

            item.classList.add('active');
            document.getElementById(targetView).classList.add('active');
            sidebar.classList.remove('open');

            if (targetView === 'explorerView') {
                loadDestinations();
            }
        });
    });

    // --- 2. Theme Toggle ---
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            themeToggleBtn.innerHTML = newTheme === 'dark' ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun"></i>';
        });
    }

    // --- 3. Developer Debug Panel ---
    if (toggleDebugBtn && debugModal) {
        toggleDebugBtn.addEventListener('click', () => {
            debugModal.classList.remove('hidden');
            if (lastDebugPayload) {
                debugMetrics.textContent = JSON.stringify(lastDebugPayload, null, 2);
            } else {
                debugMetrics.textContent = "No active query trace. Ask a question to view diagnostic payload.";
            }
        });
    }

    if (closeDebugBtn && debugModal) {
        closeDebugBtn.addEventListener('click', () => {
            debugModal.classList.add('hidden');
        });
    }

    // --- 4. History Management ---
    const STORAGE_KEY = 'travelmate_recent_history';
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const historyList = document.getElementById('historyList');

    function loadSavedHistory() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved) {
                const items = JSON.parse(saved);
                if (items && items.length > 0) {
                    renderHistoryItems(items);
                    return;
                }
            }
        } catch (e) {
            console.warn('LocalStorage error:', e);
        }
        bindHistoryItemEvents();
    }

    function saveHistoryItem(promptText, titleText) {
        try {
            let items = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            items = items.filter(i => i.prompt !== promptText);
            items.unshift({
                prompt: promptText,
                title: titleText || promptText
            });
            items = items.slice(0, 15);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
            renderHistoryItems(items);
        } catch (e) {
            console.warn('Error saving history:', e);
        }
    }

    function renderHistoryItems(items) {
        if (!historyList) return;
        if (!items || items.length === 0) {
            historyList.innerHTML = '<div style="padding: 0.6rem; font-size: 0.8rem; color: var(--text-muted); text-align: center;">No recent chats.</div>';
            return;
        }

        historyList.innerHTML = items.map(item => `
            <div class="history-item" data-prompt="${escapeHtml(item.prompt)}">
                <span class="history-text"><i class="fa-regular fa-compass"></i> ${escapeHtml(item.title)}</span>
                <button class="delete-item-btn" title="Delete chat"><i class="fa-regular fa-trash-can"></i></button>
            </div>
        `).join('');

        bindHistoryItemEvents();
    }

    function bindHistoryItemEvents() {
        const items = document.querySelectorAll('.history-item');
        items.forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.closest('.delete-item-btn')) {
                    e.stopPropagation();
                    deleteSingleHistoryItem(item);
                    return;
                }
                const promptText = item.getAttribute('data-prompt');
                userInput.value = promptText;
                chatForm.dispatchEvent(new Event('submit'));
            });
        });
    }

    function deleteSingleHistoryItem(itemElem) {
        const promptToDelete = itemElem.getAttribute('data-prompt');
        itemElem.remove();

        try {
            let items = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            items = items.filter(i => i.prompt !== promptToDelete);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
        } catch (e) {
            console.warn('Error deleting history item:', e);
        }
    }

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', () => {
            if (confirm('Delete all chat history?')) {
                localStorage.removeItem(STORAGE_KEY);
                if (historyList) historyList.innerHTML = '<div style="padding: 0.6rem; font-size: 0.8rem; color: var(--text-muted); text-align: center;">No recent chats.</div>';
                welcomeScreen.classList.remove('hidden');
                chatMessages.classList.add('hidden');
                chatMessages.innerHTML = '';
            }
        });
    }

    loadSavedHistory();

    // Suggestion Buttons
    suggestionCards.forEach(card => {
        card.addEventListener('click', () => {
            userInput.value = card.getAttribute('data-prompt');
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    suggestPills.forEach(pill => {
        pill.addEventListener('click', () => {
            userInput.value = pill.getAttribute('data-prompt');
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    quickDestBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            userInput.value = btn.getAttribute('data-prompt');
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    // --- 5. Auto-resizing Textarea ---
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // --- 6. Web Speech Voice Input ---
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            isRecording = true;
            voiceMicBtn.classList.add('recording');
            recordingIndicator.classList.remove('hidden');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            recordingIndicator.classList.add('hidden');
            voiceMicBtn.classList.remove('recording');
            chatForm.dispatchEvent(new Event('submit'));
        };

        recognition.onerror = (event) => {
            console.warn('Speech recognition error:', event.error);
            stopRecording();
        };

        recognition.onend = () => {
            stopRecording();
        };
    } else {
        if (voiceMicBtn) voiceMicBtn.style.display = 'none';
    }

    if (voiceMicBtn) {
        voiceMicBtn.addEventListener('click', () => {
            if (!recognition) return;
            if (isRecording) {
                recognition.stop();
            } else {
                const selectedLang = uiLangSelect.value;
                const bcp47Map = {
                    'te': 'te-IN', 'hi': 'hi-IN', 'ta': 'ta-IN', 'kn': 'kn-IN',
                    'ml': 'ml-IN', 'bn': 'bn-IN', 'mr': 'mr-IN', 'en': 'en-US',
                    'es': 'es-ES', 'fr': 'fr-FR', 'de': 'de-DE', 'ja': 'ja-JP'
                };
                recognition.lang = bcp47Map[selectedLang] || 'en-US';
                recognition.start();
            }
        });
    }

    function stopRecording() {
        isRecording = false;
        if (voiceMicBtn) voiceMicBtn.classList.remove('recording');
        if (recordingIndicator) recordingIndicator.classList.add('hidden');
    }

    // --- 7. TravelMate AI Chat Form Submission ---
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;

        welcomeScreen.classList.add('hidden');
        chatMessages.classList.remove('hidden');

        appendUserMessage(query);
        saveHistoryItem(query, query);
        userInput.value = '';
        userInput.style.height = 'auto';

        const loadingId = appendProgressiveLoadingMessage();

        try {
            const selectedLang = uiLangSelect.value;
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    query: query, 
                    language: selectedLang,
                    session_context: currentSessionContext
                })
            });

            const data = await response.json();
            removeMessage(loadingId);

            if (data.status === 'success') {
                lastDebugPayload = data;
                if (data.debug_info && data.debug_info.resolved_query) {
                    currentSessionContext.current_destination = data.debug_info.resolved_query;
                }
                appendAssistantMessage(data);
            } else {
                appendSimpleMessage('assistant', `⚠️ ${data.message || 'An error occurred.'}`);
            }
        } catch (err) {
            console.error('Chat error:', err);
            removeMessage(loadingId);
            appendSimpleMessage('assistant', '⚠️ Connection error. Please ensure Flask server is running.');
        }
    });

    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message user-message';
        msgDiv.innerHTML = `
            <div class="message-body">${escapeHtml(text)}</div>
            <div class="message-avatar"><i class="fa-solid fa-user"></i></div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendSimpleMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${sender}-message`;
        msgDiv.innerHTML = `
            <div class="message-avatar"><i class="fa-solid fa-earth-americas"></i></div>
            <div class="message-body">
                <div class="message-text">${escapeHtml(text)}</div>
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendProgressiveLoadingMessage() {
        const id = 'loading_' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.id = id;
        msgDiv.className = 'chat-message assistant-message';
        msgDiv.innerHTML = `
            <div class="message-avatar"><i class="fa-solid fa-earth-americas"></i></div>
            <div class="message-body">
                <div class="message-text" id="${id}_text">
                    <em><i class="fa-solid fa-spinner fa-spin"></i> 🔎 Searching Wikipedia & Wikivoyage...</em>
                </div>
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Progressive status animation
        setTimeout(() => {
            const el = document.getElementById(`${id}_text`);
            if (el) el.innerHTML = '<em><i class="fa-solid fa-book-open fa-spin"></i> 📚 Reading travel guides & historical facts...</em>';
        }, 1200);

        setTimeout(() => {
            const el = document.getElementById(`${id}_text`);
            if (el) el.innerHTML = '<em><i class="fa-solid fa-image fa-spin"></i> 🖼️ Finding high-res Wikimedia Commons media...</em>';
        }, 2600);

        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function appendAssistantMessage(data) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message assistant-message';

        const parsedAnswer = marked.parse(data.answer);

        let sourcesHtml = '';
        if (data.sources && data.sources.length > 0) {
            sourcesHtml = `
                <div class="sources-card">
                    <div class="sources-title"><i class="fa-solid fa-book-bookmark"></i> Wikimedia Sources (${data.sources.length}):</div>
                    ${data.sources.map(s => `
                        <div class="source-item">
                            📌 <strong>${escapeHtml(s.title)}</strong> 
                            ${s.url ? `<a href="${s.url}" target="_blank" class="source-link">[${escapeHtml(s.type || s.source)}]</a>` : `<em>(${escapeHtml(s.source)})</em>`}
                        </div>
                    `).join('')}
                </div>
            `;
        }

        msgDiv.innerHTML = `
            <div class="message-avatar"><i class="fa-solid fa-earth-americas"></i></div>
            <div class="message-body">
                <div class="message-meta">
                    <span class="agent-name">TravelMate AI</span>
                    <span class="badge badge-lang"><i class="fa-solid fa-globe"></i> ${data.detected_language} (${Math.round(data.confidence * 100)}%)</span>
                    ${data.is_grounded ? '<span class="badge badge-rag"><i class="fa-solid fa-shield-halved"></i> Wikimedia Grounded</span>' : ''}
                </div>
                <div class="message-text">${parsedAnswer}</div>
                ${sourcesHtml}
                <div class="message-actions">
                    <button class="action-btn" onclick="speakText(this)" data-text="${escapeHtml(stripMarkdown(data.answer))}">
                        <i class="fa-solid fa-volume-high"></i> Listen
                    </button>
                    <button class="action-btn" onclick="copyText(this)" data-text="${escapeHtml(stripMarkdown(data.answer))}">
                        <i class="fa-solid fa-copy"></i> Copy
                    </button>
                </div>
            </div>
        `;

        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // TTS & Copy Helpers
    window.speakText = function(btn) {
        const text = btn.getAttribute('data-text');
        if (!text || !('speechSynthesis' in window)) return;

        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        const selectedLang = uiLangSelect ? uiLangSelect.value : 'en';
        const bcp47Map = {
            'te': 'te-IN', 'hi': 'hi-IN', 'ta': 'ta-IN', 'kn': 'kn-IN',
            'ml': 'ml-IN', 'bn': 'bn-IN', 'mr': 'mr-IN', 'en': 'en-US',
            'es': 'es-ES', 'fr': 'fr-FR', 'de': 'de-DE', 'ja': 'ja-JP'
        };
        utterance.lang = bcp47Map[selectedLang] || 'en-US';

        btn.innerHTML = '<i class="fa-solid fa-pause"></i> Playing...';
        utterance.onend = () => {
            btn.innerHTML = '<i class="fa-solid fa-volume-high"></i> Listen';
        };

        window.speechSynthesis.speak(utterance);
    };

    window.copyText = function(btn) {
        const text = btn.getAttribute('data-text');
        if (!text) return;

        navigator.clipboard.writeText(text).then(() => {
            btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                btn.innerHTML = '<i class="fa-solid fa-copy"></i> Copy';
            }, 2000);
        });
    };

    // --- 8. Trip Planner Submission ---
    if (plannerForm) {
        plannerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const dest = document.getElementById('planDest').value;
            const days = document.getElementById('planDays').value;
            const budget = document.getElementById('planBudget').value;
            const currency = document.getElementById('planCurrency').value;
            const style = document.getElementById('planStyle').value;

            plannerEmptyState.style.display = 'none';
            plannerResults.classList.remove('hidden');
            plannerResults.innerHTML = '<p><i class="fa-solid fa-spinner fa-spin"></i> Generating travel itinerary from Wikivoyage data...</p>';

            try {
                const res = await fetch('/api/plan-trip', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ destination: dest, days: days, budget: budget, currency: currency, style: style })
                });

                const data = await res.json();
                if (data.status === 'success') {
                    renderPlannerResults(data);
                } else {
                    plannerResults.innerHTML = `<p class="error">⚠️ ${data.message}</p>`;
                }
            } catch (err) {
                console.error('Planner error:', err);
                plannerResults.innerHTML = '<p class="error">⚠️ Failed to generate itinerary.</p>';
            }
        });
    }

    function renderPlannerResults(data) {
        let html = `
            <div class="planner-results-header" style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.25rem;">
                <h2 style="font-size: 1.35rem; color: var(--accent-primary);">${escapeHtml(data.destination)} (${data.days}-Day ${data.style} Plan)</h2>
                <p style="font-size: 0.85rem; color: var(--text-secondary);">📍 Best Season: <strong>${escapeHtml(data.best_season)}</strong> | Visa: <strong>${escapeHtml(data.visa_info)}</strong></p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.75rem; margin-top: 1rem;">
                    <div style="padding: 0.6rem; background: var(--bg-input); border-radius: var(--radius-md);"><small style="font-size: 0.75rem; color: var(--text-muted);">Total Budget</small><div style="font-weight: 700; color: var(--accent-success);">${data.total_budget}</div></div>
                    <div style="padding: 0.6rem; background: var(--bg-input); border-radius: var(--radius-md);"><small style="font-size: 0.75rem; color: var(--text-muted);">Daily Spend</small><div style="font-weight: 700; color: var(--accent-success);">${data.daily_budget}</div></div>
                    <div style="padding: 0.6rem; background: var(--bg-input); border-radius: var(--radius-md);"><small style="font-size: 0.75rem; color: var(--text-muted);">Stays (40%)</small><div style="font-weight: 700; color: var(--text-primary);">${data.cost_breakdown.accommodations}</div></div>
                    <div style="padding: 0.6rem; background: var(--bg-input); border-radius: var(--radius-md);"><small style="font-size: 0.75rem; color: var(--text-muted);">Food (25%)</small><div style="font-weight: 700; color: var(--text-primary);">${data.cost_breakdown.food_and_dining}</div></div>
                </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 1rem;">
                ${data.itinerary.map(day => `
                    <div style="padding: 1rem; background: rgba(255,255,255,0.03); border-left: 4px solid var(--accent-blue); border-radius: var(--radius-md);">
                        <h4 style="color: var(--accent-primary); margin-bottom: 0.4rem;">${day.title}</h4>
                        <div style="font-size: 0.86rem; color: var(--text-secondary); margin-bottom: 0.3rem;">🌅 <strong>Morning:</strong> ${marked.parseInline(day.morning)}</div>
                        <div style="font-size: 0.86rem; color: var(--text-secondary); margin-bottom: 0.3rem;">☀️ <strong>Afternoon:</strong> ${marked.parseInline(day.afternoon)}</div>
                        <div style="font-size: 0.86rem; color: var(--text-secondary); margin-bottom: 0.3rem;">🌇 <strong>Evening:</strong> ${marked.parseInline(day.evening)}</div>
                        <div style="font-size: 0.86rem; color: var(--text-secondary);">🌙 <strong>Night:</strong> ${marked.parseInline(day.night)}</div>
                    </div>
                `).join('')}
            </div>
        `;
        plannerResults.innerHTML = html;
    }

    // --- 9. Global Destination Explorer Grid ---
    if (regionFilterTabs) {
        regionFilterTabs.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-pill')) {
                document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                activeRegion = e.target.getAttribute('data-region');
                loadDestinations();
            }
        });
    }

    if (destSearchInput) {
        destSearchInput.addEventListener('input', () => {
            loadDestinations();
        });
    }

    async function loadDestinations() {
        const search = destSearchInput ? destSearchInput.value.trim() : '';
        try {
            const res = await fetch(`/api/destinations?region=${encodeURIComponent(activeRegion)}&search=${encodeURIComponent(search)}`);
            const data = await res.json();

            if (data.status === 'success') {
                renderDestinationCards(data.destinations);
            }
        } catch (err) {
            console.error('Error loading destinations:', err);
        }
    }

    function renderDestinationCards(destinations) {
        if (!destinationGrid) return;
        if (!destinations || destinations.length === 0) {
            destinationGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No destinations found matching your criteria.</p>';
            return;
        }

        destinationGrid.innerHTML = destinations.map(d => `
            <div class="card" style="padding: 1.25rem;">
                <h3 style="font-size: 1.15rem; color: var(--text-primary);">${escapeHtml(d.destination)}</h3>
                <div style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.6rem;">📍 ${escapeHtml(d.country)} • ${escapeHtml(d.region)}</div>
                <div style="display: inline-block; padding: 0.15rem 0.6rem; background: rgba(6,182,212,0.15); color: var(--accent-primary); border-radius: var(--radius-pill); font-size: 0.75rem; margin-bottom: 0.75rem;">${escapeHtml(d.category)}</div>
                <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.85rem;">
                    <strong>Top Attractions:</strong><br>
                    ${d.attractions.slice(0, 3).map(a => `• ${escapeHtml(a)}`).join('<br>')}
                </div>
                <button class="action-btn" style="width: 100%; justify-content: center;" onclick="askAboutDestination('${escapeHtml(d.destination)}')">
                    <i class="fa-solid fa-message"></i> Ask Chatbot About ${escapeHtml(d.destination)}
                </button>
            </div>
        `).join('');
    }

    window.askAboutDestination = function(destName) {
        document.querySelector('.sidebar-nav-item[data-view="chatView"]').click();
        welcomeScreen.classList.add('hidden');
        chatMessages.classList.remove('hidden');
        userInput.value = `Tell me about ${destName}`;
        chatForm.dispatchEvent(new Event('submit'));
    };

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    function stripMarkdown(md) {
        return md.replace(/[#*`_~]/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').trim();
    }
});
