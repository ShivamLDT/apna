import React, { useState, useEffect, useRef, useCallback } from 'react';
import { nanoid } from 'nanoid';
import "./ChatBot.css";
import { useNavigate } from 'react-router-dom';
import CryptoJS from 'crypto-js';
import { useSyncData } from '../../Context/SyncDataContext';
import DOMPurify from 'dompurify';

function decryptData(encryptedData) {
    if (!encryptedData) return "";
    try {
        const bytes = CryptoJS.AES.decrypt(encryptedData, "1234567890");
        const decrypted = bytes.toString(CryptoJS.enc.Utf8);
        return decrypted || "";
    } catch (error) {
        console.error("Decryption error:", error);
        return "";
    }
}

const sanitizeBotHtml = (html) => {
    if (typeof html !== 'string') return "";
    return DOMPurify.sanitize(html, {
        ALLOWED_TAGS: [
            'b', 'strong', 'i', 'em', 'u', 'br',
            'ul', 'ol', 'li', 'p', 'span', 'div'
        ],

        ALLOWED_ATTR: ['class'],
        FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'input', 'form', 'textarea'],
        FORBID_ATTR: ['style', 'onerror', 'onload', 'onclick', 'onmouseover']
    });
};

// [SECURITY FIX] Strict Input Validation
const normalizeUserInput = (text) => {
    if (!text) return "";

    // 1. First, strip any looking like HTML tags immediately
    let cleanText = text.replace(/<[^>]*>/g, '');

    // 2. Decode HTML entities to prevent bypassing via encoding (e.g., &lt;script&gt;)
    const txt = document.createElement("textarea");
    txt.innerHTML = cleanText;
    cleanText = txt.value;

    // 3. Strict Allow-list Regex
    // Allows: Alphanumeric, Spaces, and specific safe punctuation (., ? ! @ - _ ' )
    // Removes: < > " ` % $ & ; (characters often used in XSS payloads)
    return cleanText.replace(/[^a-zA-Z0-9\s.,?!@\-_']/g, '');
};

function ChatBot() {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([]);
    const [userInput, setUserInput] = useState('');
    const [username, setUsername] = useState('Anonymous');
    const [sessionId, setSessionId] = useState(null);
    const [isUsernameSet, setIsUsernameSet] = useState(false);
    const { syncData, loading, error } = useSyncData();
    const [currentLanguage, setCurrentLanguage] = useState('english');
    const [showSuggestionsPanel, setShowSuggestionsPanel] = useState(true);
    const [cooldown, setCooldown] = useState(0);
    const [predictiveSuggestions, setPredictiveSuggestions] = useState([]);
    const [showPredictiveSuggestions, setShowPredictiveSuggestions] = useState(false);
    const {
        first_name,
        last_name,
        role,
        image_url,
        organization_details
    } = syncData || {};
    const admin_name = `${first_name || ''} ${last_name || ''}`;
    const first_name1 = decryptData(localStorage.getItem("first_name"));
    const last_name1 = decryptData(localStorage.getItem("last_name"));

    const getDisplayName = () => {
        if (admin_name.trim()) return admin_name;
        if (first_name1 && last_name1) return `${first_name1} ${last_name1}`;
        if (first_name1) return first_name1;
        return null;
    };

    const [speechState, setSpeechState] = useState({
        isSupported: false,
        isListening: false,
        statusMessage: '',
        activeMic: null // 'en-GB' or 'hi-IN'
    });
    const speechStatusTimeoutRef = useRef(null);
    const [showFeedbackModal, setShowFeedbackModal] = useState(false);
    const [feedbackData, setFeedbackData] = useState({ messageId: null, kbEntryId: null, rating: 0, hoverRating: 0, comment: '' });
    const chatContainerRef = useRef(null);
    const speechRecognitionRef = useRef(null);
    const predictiveSuggestTimeoutRef = useRef(null);
    const cooldownTimerIntervalRef = useRef(null);
    const followupClickCountsRef = useRef(JSON.parse(localStorage.getItem('followupClickCounts')) || {});

    const COOLDOWN_SECONDS = 3;
    const MAX_FOLLOWUP_CLICKS = 3;
    const PREDICTIVE_SUGGESTION_DELAY = 300;

    const showSpeechStatus = useCallback((message, duration = 3000) => {
        setSpeechState(prev => ({ ...prev, statusMessage: message }));
        if (speechStatusTimeoutRef.current) {
            clearTimeout(speechStatusTimeoutRef.current);
        }
        const timeout = setTimeout(() => {
            setSpeechState(prev => ({ ...prev, statusMessage: '' }));
        }, duration);
        speechStatusTimeoutRef.current = timeout;
    }, []);

    const addMessage = useCallback((content, type, data = {}) => {
        const newMessage = {
            id: nanoid(),
            content,
            type,
            ...data
        };
        setMessages(prev => [...prev, newMessage]);
    }, []);

    const sendMessage = useCallback(async (messageText = null, eventType = 'user_message', followupQuestionId = null) => {
        const rawMessage = messageText || userInput.trim();
        if (!rawMessage && eventType === 'user_message') return;

        // [SECURITY FIX] Apply strict normalization BEFORE using the message
        const userMessage = normalizeUserInput(rawMessage);

        // If message became empty after sanitization (e.g., user sent only "<script>"), don't send it.
        if (!userMessage) {
            setUserInput('');
            return;
        }

        setShowPredictiveSuggestions(false);

        if (cooldown > 0) {
            showSpeechStatus(`Please wait ${cooldown.toFixed(1)}s before sending another message.`);
            return;
        }

        addMessage(userMessage, 'user');
        if (eventType === 'user_message') {
            setUserInput('');
        }

        setCooldown(COOLDOWN_SECONDS);

        addMessage('<div class="loading-spinner"></div>🤔 Processing your query...', 'bot', { isLoading: true });

        try {
            const payload = {
                message: userMessage,
                session_id: sessionId,
                username: username,
                event_type: eventType
            };
            if (followupQuestionId) {
                payload.followup_question_id = followupQuestionId;
            }

            const response = await fetch('https://chatbot.apnabackup.com/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            setMessages(prev => prev.filter(m => !m.isLoading));

            if (data.success) {
                // sanitizeBotHtml is called during render, but data.response is stored raw
                addMessage(data.response, 'bot', data);
                if (data.cooldown_active && data.wait_time) {
                    setCooldown(data.wait_time);
                }
            } else {
                addMessage(data.response || data.message || 'An unknown error occurred.', 'bot warning', data);
                if (data.cooldown_active && data.wait_time) {
                    setCooldown(data.wait_time);
                } else {
                    setCooldown(0); // Reset cooldown on other errors
                }
            }
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => prev.filter(m => !m.isLoading));
            addMessage('❌ Sorry, I am currently unavailable. Please try again later. (Network Error)', 'bot warning', { message_id: String(Date.now()), kb_entry_id: null });
            setCooldown(0);
        }
    }, [userInput, cooldown, sessionId, username, addMessage, showSpeechStatus]);

    const handleSelectSuggestion = (text) => {
        // [SECURITY FIX] Normalize suggestion text too
        const cleanText = normalizeUserInput(text);
        setUserInput(cleanText);
        setShowSuggestionsPanel(false);
        sendMessage(cleanText);
    };

    const handleSendFollowup = useCallback((questionText, questionId) => {
        const currentClicks = followupClickCountsRef.current[questionId] || 0;
        if (currentClicks >= MAX_FOLLOWUP_CLICKS) return;

        followupClickCountsRef.current[questionId] = currentClicks + 1;
        localStorage.setItem('followupClickCounts', JSON.stringify(followupClickCountsRef.current));

        // [SECURITY FIX] Normalize followups
        const cleanText = normalizeUserInput(questionText);
        sendMessage(cleanText, 'followup_click', questionId);
        // Force update to show new click count
        setMessages(prev => [...prev]);
    }, [sendMessage]);

    const handleSendContextualQuery = (queryText) => {
        // [SECURITY FIX] Normalize contextual queries
        const cleanText = normalizeUserInput(queryText);
        setUserInput(cleanText);
        sendMessage(cleanText, 'user_message');
    };

    const handleClearChat = useCallback(async () => {
        setMessages([]);
        localStorage.removeItem('chatbotSessionId');
        localStorage.removeItem('chatbotUsername');
        localStorage.removeItem('followupClickCounts');

        const newSessionId = nanoid();
        setSessionId(newSessionId);
        localStorage.setItem('chatbotSessionId', newSessionId);

        setUsername('Anonymous');
        setIsUsernameSet(false);
        setUserInput('');
        setShowSuggestionsPanel(true);
        setCooldown(0);
        followupClickCountsRef.current = {};

        if (sessionId) {
            try {
                await fetch('https://chatbot.apnabackup.com/api/session/clear', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId }),
                });
                showSpeechStatus('Session cleared!', 2000);
            } catch (error) {
                console.error('Network error clearing session data:', error);
            }
        }
        addMessage('👋 Welcome! How can I help you today?', 'bot');
    }, [sessionId, addMessage, showSpeechStatus]);


    const handleFeedbackSubmit = async () => {
        if (feedbackData.rating === 0) {
            showSpeechStatus('Please select a star rating.', 2000);
            return;
        }

        try {
            // [SECURITY FIX] Sanitize comment before sending
            const cleanComment = normalizeUserInput(feedbackData.comment);

            const payload = {
                message_id: feedbackData.messageId,
                feedback_type: 'rating',
                kb_entry_id: feedbackData.kbEntryId,
                session_id: sessionId,
                rating: feedbackData.rating,
                comment: cleanComment
            };

            const response = await fetch('https://chatbot.apnabackup.com/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();

            if (data.success) {
                showSpeechStatus('Feedback recorded!', 'success');
                setMessages(prev => prev.map(msg =>
                    msg.message_id === feedbackData.messageId
                        ? { ...msg, feedbackSubmitted: true }
                        : msg
                ));
            } else {
                showSpeechStatus(`Error: ${data.message || 'Failed to record feedback'}`, 'error');
            }
        } catch (error) {
            console.error('Error sending feedback:', error);
            showSpeechStatus('Network error: Could not send feedback.', 'error');
        } finally {
            setShowFeedbackModal(false);
        }
    };

    const handleReportIncorrect = async (messageId, kbEntryId) => {
        try {
            const payload = {
                message_id: messageId,
                feedback_type: 'report_incorrect',
                kb_entry_id: kbEntryId,
                session_id: sessionId,
            };
            const response = await fetch('https://chatbot.apnabackup.com/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            if (data.success) {
                showSpeechStatus('Response reported as incorrect. Thank you.', 'success');
                setMessages(prev => prev.map(msg =>
                    msg.message_id === messageId
                        ? { ...msg, feedbackSubmitted: true }
                        : msg
                ));
            } else {
                showSpeechStatus(`Error: ${data.message || 'Failed to report.'}`, 'error');
            }
        } catch (error) {
            showSpeechStatus('Network error: Could not send report.', 'error');
        }
    };

    const stopSpeechRecognition = useCallback(() => {
        if (speechRecognitionRef.current && speechState.isListening) {
            speechRecognitionRef.current.stop();
        }
    }, [speechState.isListening]);

    const startSpeechRecognition = useCallback((lang) => {
        if (!speechState.isSupported) {
            showSpeechStatus('Speech recognition not supported in this browser.');
            return;
        }
        if (speechState.isListening) {
            stopSpeechRecognition();
        }
        speechRecognitionRef.current.lang = lang;
        speechRecognitionRef.current.start();
        setSpeechState(prev => ({ ...prev, isListening: true, activeMic: lang }));
    }, [speechState.isSupported, speechState.isListening, showSpeechStatus, stopSpeechRecognition]);

    const toggleSpeechRecognition = (lang) => {
        if (speechState.isListening && speechState.activeMic === lang) {
            stopSpeechRecognition();
        } else {
            startSpeechRecognition(lang);
        }
    };

    const fetchPredictiveSuggestions = useCallback(async (query) => {
        // [SECURITY FIX] Normalize query before sending to suggestions API
        const cleanQuery = normalizeUserInput(query);

        if (cleanQuery.length < 2) {
            setShowPredictiveSuggestions(false);
            return;
        }
        try {
            const langParam = currentLanguage === 'english' ? 'en' : 'hi';
            const response = await fetch(`https://chatbot.apnabackup.com/api/predictive_suggestions?query=${encodeURIComponent(cleanQuery)}&language=${langParam}`);
            const data = await response.json();
            if (data.success && data.suggestions.length > 0) {
                setPredictiveSuggestions(data.suggestions);
                setShowPredictiveSuggestions(true);
            } else {
                setShowPredictiveSuggestions(false);
            }
        } catch (error) {
            console.error('Error fetching predictive suggestions:', error);
            setShowPredictiveSuggestions(false);
        }
    }, [currentLanguage]);

    useEffect(() => {
        let currentSessionId = localStorage.getItem('chatbotSessionId');
        const decryptedDisplayName = getDisplayName();
        let currentUsername = decryptedDisplayName || localStorage.getItem('chatbotUsername');

        if (!currentSessionId) {
            currentSessionId = nanoid();
            localStorage.setItem('chatbotSessionId', currentSessionId);
        }
        setSessionId(currentSessionId);

        if (currentUsername) {
            setUsername(currentUsername);
            setIsUsernameSet(true);
            if (decryptedDisplayName) {
                localStorage.setItem('chatbotUsername', decryptedDisplayName);
            }
            if (messages.length === 0) {
                addMessage(`👋 Welcome back, ${currentUsername}! How can I help you today?`, 'bot');
            }
        } else {
            if (messages.length === 0) {
                addMessage('👋 Welcome! Please enter your name to start chatting. (Optional, defaults to Anonymous)', 'bot');
            }
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            setSpeechState(prev => ({ ...prev, isSupported: true }));
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.maxAlternatives = 1;

            recognition.onstart = () => {
                showSpeechStatus(`🎤 Listening in ${recognition.lang === 'hi-IN' ? 'Hindi' : 'English'}... Speak now!`);
            };

            recognition.onresult = (event) => {
                let transcript = '';
                let isFinal = false;
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                    if (event.results[i].isFinal) isFinal = true;
                }

                // [SECURITY FIX] Don't set raw transcript to state immediately if you want strict control, 
                // but generally, updating the UI input with raw text is fine, 
                // the sendMessage function will handle the sanitization.
                setUserInput(transcript);

                if (isFinal) {
                    showSpeechStatus('✅ Speech captured!', 1000);
                    sendMessage(transcript);
                }
            };

            recognition.onend = () => {
                setSpeechState(prev => ({ ...prev, isListening: false, activeMic: null }));
            };

            recognition.onerror = (event) => {
                let errorMessage = '❌ Speech recognition failed';
                if (event.error === 'no-speech') errorMessage = '🤫 No speech detected - try again';
                else if (event.error === 'not-allowed') errorMessage = '🚫 Microphone permission required';
                showSpeechStatus(errorMessage);
            };

            speechRecognitionRef.current = recognition;
        }
    }, [messages.length, addMessage, showSpeechStatus, sendMessage, first_name1, last_name1, admin_name]);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);

    useEffect(() => {
        if (cooldown > 0) {
            cooldownTimerIntervalRef.current = setInterval(() => {
                setCooldown(prev => prev - 0.1);
            }, 100);
        } else if (cooldown <= 0) {
            setCooldown(0);
            if (cooldownTimerIntervalRef.current) clearInterval(cooldownTimerIntervalRef.current);
        }
        return () => {
            if (cooldownTimerIntervalRef.current) clearInterval(cooldownTimerIntervalRef.current);
        };
    }, [cooldown]);

    useEffect(() => {
        if (userInput.trim() === '') {
            setShowPredictiveSuggestions(false);
            return;
        }
        if (predictiveSuggestTimeoutRef.current) {
            clearTimeout(predictiveSuggestTimeoutRef.current);
        }
        predictiveSuggestTimeoutRef.current = setTimeout(() => {
            fetchPredictiveSuggestions(userInput);
        }, PREDICTIVE_SUGGESTION_DELAY);

        return () => {
            if (predictiveSuggestTimeoutRef.current) {
                clearTimeout(predictiveSuggestTimeoutRef.current);
            }
        };
    }, [userInput, fetchPredictiveSuggestions]);


    const englishSuggestions = [
        { text: 'My backup failed', label: '❌ My backup failed' },
        { text: 'User cannot access backups', label: '🔐 Cannot access backups' },
        { text: 'My endpoint is offline how do i fix it', label: '📋 Endpoint is offline' },
        { text: 'Get endpoint report', label: '📊 Get endpoint report' },
        { text: 'Change backup time', label: '⏰ Change backup schedule' },
        { text: 'View failed backup jobs', label: '❌ View failed backup jobs' },
        { text: 'Restore did not work', label: '📥 Restore didn\'t work' },
        { text: 'Backup only .doc files', label: '📄 Backup specific file types' },
        { text: 'Add a new user', label: '👤 Add a new user' },
        { text: 'How to check logs?', label: '📝 Check logs' },
        { text: 'Email notification did not come', label: '📧 Email notification issues' },
        { text: 'How to check server health', label: '💻 Monitor Server health' },
    ];

    const hindiSuggestions = [
        { text: 'मेरा बैकअप फेल हुआ', label: '❌ मेरा बैकअप फेल हुआ' },
        { text: 'यूजर बैकअप एक्सेस नहीं कर सकता', label: '🔐 यूजर बैकअप एक्सेस नहीं कर सकता' },
        { text: 'एंडपॉइंट ऑफ़लाइन है।', label: '📋 एंडपॉइंट ऑफ़लाइन है।' },
        { text: 'एंडपॉइंट रिपोर्ट चाहिए', label: '📊 एंडपॉइंट रिपोर्ट चाहिए' },
        { text: 'बैकअप का समय बदलना है', label: '⏰ बैकअप का समय बदलना है' },
        { text: 'फेल हुए बैकअप jobs देखने हैं', label: '❌ फेल बैकअप jobs देखें' },
        { text: 'रिस्टोर काम नहीं कर रहा है।', label: '📥रिस्टोर काम नहीं कर रहा है।' },
        { text: 'केवल .doc फाइलें बैकअप करनी हैं', label: '📄 विशिष्ट फाइल बैकअप करें' },
        { text: 'नया यूजर कैसे जोड़ें', label: '👤 नया यूजर जोड़ें' },
        { text: 'बैकअप लॉग्स कैसे चेक करें?', label: '📝 लॉग्स चेक करें' },
        { text: 'ईमेल नोटिफिकेशन नहीं आया।', label: '📧 ईमेल नोटिफिकेशन की समस्याएं' },
        { text: 'एंडपॉइंट या सर्वर का हेल्थ मॉनिटर करें।', label: '💻सर्वर का हेल्थ मॉनिटर करें।' },
    ];

    return (
        <>
            {speechState.statusMessage && <div className="speech-status">{speechState.statusMessage}</div>}

            <div className="container">
                <div className="header"></div>

                {showSuggestionsPanel && (
                    <div className="suggestions-panel">
                        <div className="suggestions-title">⚡ Quick Help - Click on a common issue:</div>
                        <div className="language-tabs">
                            <button className={`language-tab ${currentLanguage === 'english' ? 'active' : ''}`} onClick={() => setCurrentLanguage('english')}>English</button>
                            <button className={`language-tab ${currentLanguage === 'hindi' ? 'active' : ''}`} onClick={() => setCurrentLanguage('hindi')}>हिंदी</button>
                            <button className="tutorial-button" onClick={() => window.open('https://www.youtube.com/watch?v=7nt3G8LWCPM', '_blank')}>▶️ Tutorial</button>
                            <button className="documentation-button" onClick={() => window.open('https://docs.google.com/document/d/1Kb_UBazvixgGvwbqWrt_Nrh9gi22z8eEJraoZbhcyzI/edit?usp=sharing', '_blank')}>📄 Documentation</button>
                        </div>
                        <div className="suggestions-grid">
                            {(currentLanguage === 'english' ? englishSuggestions : hindiSuggestions).map(s => (
                                <div key={s.text} className="suggestion-btn" onClick={() => handleSelectSuggestion(s.text)}>{s.label}</div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="chat-container" ref={chatContainerRef}>
                    {messages.map(msg => (
                        <div
                            key={msg.id}
                            className={`message ${msg.type} ${msg.status === 'validation_failed' || msg.error_type ? 'warning' : ''
                                } ${msg.show_ticket_options ||
                                    (msg.did_you_mean_suggestions && msg.did_you_mean_suggestions.length > 0)
                                    ? 'low-confidence'
                                    : ''
                                }`}
                        >
                            {/* CONTENT RENDERING */}
                            {msg.type === 'user' && !msg.isLoading ? (
                                // USER MESSAGE: render as plain text
                                <div className="user-message-text">
                                    {msg.content}
                                </div>
                            ) : (
                                // BOT MESSAGE: sanitized HTML
                                <div
                                    dangerouslySetInnerHTML={{
                                        __html: msg.isLoading
                                            ? sanitizeBotHtml(msg.content)
                                            : sanitizeBotHtml(msg.content.replace(/\n/g, '<br>'))
                                    }}
                                />
                            )}

                            {msg.type === 'bot' && !msg.isLoading && (
                                <>
                                    {msg.language && msg.language !== 'unknown' && (
                                        <span className="language-badge">
                                            {msg.language === 'en' ? 'English' : 'Hindi'}
                                        </span>
                                    )}

                                    {msg.show_ticket_options && (
                                        <div className="ticket-options">
                                            <p>Would you like to raise a support ticket?</p>
                                            <div className="ticket-buttons">
                                                <button
                                                    className="ticket-btn yes"
                                                    onClick={() => navigate("/support")}
                                                >
                                                    Yes, Create Ticket
                                                </button>
                                                <button
                                                    className="ticket-btn no"
                                                    onClick={() =>
                                                        addMessage(
                                                            '💡 No problem! Feel free to ask something else.',
                                                            'bot'
                                                        )
                                                    }
                                                >
                                                    No, I'll Try Again
                                                </button>
                                            </div>
                                        </div>
                                    )}

                                    {msg.did_you_mean_suggestions?.length > 0 && (
                                        <div className="did-you-mean-section">
                                            <p className="did-you-mean-prompt">
                                                {msg.language === 'hi'
                                                    ? 'क्या आपका मतलब यह था:'
                                                    : 'Did you mean:'}
                                            </p>
                                            <div className="did-you-mean-options">
                                                {msg.did_you_mean_suggestions.map(s => (
                                                    <button
                                                        key={s.text}
                                                        className="did-you-mean-button"
                                                        onClick={() => handleSendContextualQuery(s.text)}
                                                    >
                                                        {s.text}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {msg.followup_questions?.length > 0 && (
                                        <div className="followup-questions">
                                            <p className="followup-prompt">Follow ups:</p>
                                            <div className="followup-options">
                                                {msg.followup_questions.map(q => {
                                                    const clicks = followupClickCountsRef.current[q.id] || 0;
                                                    const isDisabled = clicks >= MAX_FOLLOWUP_CLICKS;
                                                    return (
                                                        <button
                                                            key={q.id}
                                                            className="followup-option-button"
                                                            onClick={() =>
                                                                handleSendFollowup(q.question, q.id)
                                                            }
                                                            disabled={isDisabled}
                                                        >
                                                            {q.question}{' '}
                                                            {clicks > 0
                                                                ? `(${clicks}/${MAX_FOLLOWUP_CLICKS})`
                                                                : ''}
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

                                    {msg.contextual_buttons?.length > 0 && (
                                        <div className="contextual-buttons-section">
                                            <p className="contextual-prompt">Quick Actions:</p>
                                            <div className="contextual-options">
                                                {msg.contextual_buttons.map(btn => (
                                                    <button
                                                        key={btn.query}
                                                        className="contextual-button"
                                                        onClick={() => handleSendContextualQuery(btn.query)}
                                                    >
                                                        {btn.text}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {msg.youtube_links?.length > 0 && (
                                        <div className="youtube-links-section">
                                            <h4>📺 Relevant Video Tutorials:</h4>
                                            <ul>
                                                {msg.youtube_links.map((link, index) => {
                                                    try {
                                                        const url = new URL(link.youtube_url);
                                                        const videoId =
                                                            url.hostname === 'youtu.be'
                                                                ? url.pathname.substring(1)
                                                                : url.searchParams.get('v');
                                                        const startTime = url.searchParams.get('t');
                                                        if (!videoId) return null;
                                                        const embedUrl = `https://www.youtube.com/embed/${videoId}${startTime ? `?start=${startTime}` : ''
                                                            }`;
                                                        return (
                                                            <li key={index}>
                                                                <div
                                                                    style={{
                                                                        marginBottom: '6px',
                                                                        fontWeight: '500'
                                                                    }}
                                                                >
                                                                    {link.description}
                                                                </div>
                                                                <iframe
                                                                    width="320"
                                                                    height="180"
                                                                    style={{
                                                                        maxWidth: '100%',
                                                                        borderRadius: '6px'
                                                                    }}
                                                                    src={embedUrl}
                                                                    title={link.description}
                                                                    frameBorder="0"
                                                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                                                                    allowFullScreen
                                                                ></iframe>
                                                            </li>
                                                        );
                                                    } catch {
                                                        return null;
                                                    }
                                                })}
                                            </ul>
                                        </div>
                                    )}

                                    {msg.message_id && !msg.error_type && !msg.feedbackSubmitted && (
                                        <div className="feedback-buttons">
                                            <button
                                                className="feedback-button"
                                                onClick={() => {
                                                    setFeedbackData({
                                                        ...feedbackData,
                                                        messageId: msg.message_id,
                                                        kbEntryId: msg.kb_entry_id
                                                    });
                                                    setShowFeedbackModal(true);
                                                }}
                                            >
                                                Rate Response
                                            </button>
                                            <button
                                                className="feedback-button report-incorrect-btn"
                                                onClick={() =>
                                                    handleReportIncorrect(msg.message_id, msg.kb_entry_id)
                                                }
                                            >
                                                Report Incorrect
                                            </button>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    ))}

                </div>

                <div className="input-section">
                    <input
                        type="text"
                        id="usernameInput"
                        defaultValue={username === 'Anonymous' ? '' : username}
                        readOnly={true}
                        maxLength="50"
                        style={{ marginBottom: '10px' }}
                    />

                    {showPredictiveSuggestions && predictiveSuggestions.length > 0 && (
                        <div id="predictiveSuggestionsContainer">
                            {predictiveSuggestions.map(s => (
                                <div key={s} className="predictive-suggestion-item" onClick={() => {
                                    const cleanText = normalizeUserInput(s);
                                    setUserInput(cleanText);
                                    sendMessage(cleanText);
                                    setShowPredictiveSuggestions(false);
                                }}>{s}</div>
                            ))}
                        </div>
                    )}

                    <div className="input-row">
                        <input
                            type="text"
                            id="userInput"
                            placeholder="Type your query here in English or हिन्दी..."
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            disabled={cooldown > 0}
                            maxLength="500"
                        />
                        {cooldown > 0 && <span id="cooldownTimerDisplay">⚠️Wait: {cooldown.toFixed(1)}s</span>}
                        <button onClick={() => sendMessage()} className="send-button" disabled={cooldown > 0 || !userInput.trim()}>➤</button>
                        <button onClick={handleClearChat} className="secondary">🗑️</button>

                        <button
                            title="Speak in English"
                            onClick={() => toggleSpeechRecognition('en-GB')}
                            className={`mic-button ${speechState.isListening && speechState.activeMic === 'en-GB' ? 'listening' : ''}`}
                            disabled={!speechState.isSupported}
                        >
                            🎤Eng
                        </button>
                        <button
                            title="Speak in Hindi"
                            onClick={() => toggleSpeechRecognition('hi-IN')}
                            className={`mic-button ${speechState.isListening && speechState.activeMic === 'hi-IN' ? 'listening' : ''}`}
                            disabled={!speechState.isSupported}
                        >
                            🎤हिन्दी
                        </button>
                    </div>
                </div>
            </div>

            {showFeedbackModal && (
                <div className="modal show">
                    <div className="modal-content">
                        <span className="close-button" onClick={() => setShowFeedbackModal(false)}>&times;</span>
                        <h3>How helpful was this response?</h3>
                        <div className="modal-body">
                            <div className="star-rating"
                                onMouseOut={() => setFeedbackData(prev => ({ ...prev, hoverRating: 0 }))}
                            >
                                {[1, 2, 3, 4, 5].map(star => (
                                    <span
                                        key={star}
                                        className={`star ${(feedbackData.hoverRating || feedbackData.rating) >= star ? 'filled' : ''}`}
                                        onClick={() => setFeedbackData(prev => ({ ...prev, rating: star }))}
                                        onMouseOver={() => setFeedbackData(prev => ({ ...prev, hoverRating: star }))}
                                    >★</span>
                                ))}
                            </div>
                            <label htmlFor="feedbackComment">Optional: Add a comment</label>
                            <textarea
                                id="feedbackComment"
                                placeholder="e.g., This helped me find the solution, but it was a bit wordy."
                                value={feedbackData.comment}
                                onChange={(e) => setFeedbackData(prev => ({ ...prev, comment: e.target.value }))}
                            ></textarea>
                        </div>
                        <div className="modal-actions">
                            <button className="cancel-btn" onClick={() => setShowFeedbackModal(false)}>Cancel</button>
                            <button className="submit-btn" onClick={handleFeedbackSubmit}>Submit Feedback</button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}

export default ChatBot;