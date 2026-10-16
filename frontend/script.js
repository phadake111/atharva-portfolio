/* ==========================================================================
   Atharva Phadake — Portfolio
   script.js
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  initMobileNav();
//   initContactForm();
});

/**
 * Mobile navbar: toggles the hamburger menu open/closed and keeps
 * aria-expanded in sync for screen readers. Closes automatically on
 * link click or on resize back to desktop width.
 */
function initMobileNav() {
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");

  if (!navToggle || !navLinks) return;

  const closeMenu = () => {
    navToggle.classList.remove("open");
    navLinks.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
  };

  const toggleMenu = () => {
    const isOpen = navLinks.classList.toggle("open");
    navToggle.classList.toggle("open", isOpen);
    navToggle.setAttribute("aria-expanded", String(isOpen));
  };

  navToggle.addEventListener("click", toggleMenu);

  navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 720) closeMenu();
  });
}

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements ko select karna
    const chatOpenBtn = document.getElementById('chat-open-btn');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatBox = document.getElementById('chat-box');

    // ==========================================
    // 1. CHATBOX OPEN / CLOSE LOGIC
    // ==========================================
    if (chatOpenBtn && chatCloseBtn && chatBox) {
        chatOpenBtn.addEventListener('click', () => {
            chatBox.classList.remove('chat-hidden');
        });

        chatCloseBtn.addEventListener('click', () => {
            chatBox.classList.add('chat-hidden');
        });
    }

    // ==========================================
    // 2. REDIRECT HANDLING (From other pages)
    // ==========================================
    if (window.location.hash === '#chat-widget-container') {
        if (chatBox) {
            chatBox.classList.remove('chat-hidden');
            history.replaceState(null, null, window.location.pathname);
        }
    }
});

// ==========================================
// CONTACT FORM API INTEGRATION
// ==========================================
// =========================================================
// AI CHATBOT API INTEGRATION (FastAPI)
// =========================================================
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById("chat-input");
    const chatSendBtn = document.getElementById("chat-send-btn");
    const chatMessages = document.getElementById("chat-messages");

    let messageIdCounter = 0;

    if (chatInput && chatSendBtn && chatMessages) {
        chatSendBtn.addEventListener("click", handleChatSubmit);
        chatInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                handleChatSubmit();
            }
        });

        async function handleChatSubmit() {
            const questionText = chatInput.value.trim();
            if (questionText === "") return; 

            chatInput.value = ""; 

            appendMessage("User", questionText, "user-msg");
            const loadingId = appendMessage("AI", "Thinking...", "bot-msg");

            try {
                const response = await fetch("http://127.0.0.1:8000/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: questionText }) 
                });

                const data = await response.json(); 
                const aiReply = data.answer || data.response || "No response received.";
                
                // AI response ko Markdown parse karke update karenge
                updateMessage(loadingId, aiReply);

            } catch (error) {
                console.error("Chat API Error:", error);
                updateMessage(loadingId, "Sorry, my backend is currently offline. Please try again later.");
            }
        }

        function appendMessage(sender, text, className) {
            messageIdCounter++;
            const uniqueId = "msg-" + messageIdCounter;
            
            const messageDiv = document.createElement("div");
            messageDiv.id = uniqueId;
            messageDiv.className = className; 
            messageDiv.innerHTML = `<strong>${sender}:</strong> <span></span>`;
            
            // Agar 'Thinking...' ya plain text hai toh safe render, warna marked.parse
            const textSpan = messageDiv.querySelector("span");
            if (typeof marked !== 'undefined' && text !== "Thinking...") {
                textSpan.innerHTML = marked.parse(text);
            } else {
                textSpan.innerText = text;
            }
            
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight; 
            return uniqueId;
        }

        function updateMessage(messageId, newText) {
            const messageDiv = document.getElementById(messageId);
            if (messageDiv) {
                const textSpan = messageDiv.querySelector("span");
                if (textSpan) {
                    // Yahan marked.parse use kiya taaki AI ke bold text aur lists ekdum clean render ho
                    if (typeof marked !== 'undefined') {
                        textSpan.innerHTML = marked.parse(newText);
                    } else {
                        textSpan.innerText = newText;
                    }
                }
            }
        }
    }
});
// ==========================================
// AI RECRUITER MATCHER MODAL UI LOGIC
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    const openMatcherBtn = document.getElementById('openMatcherBtn');
    const closeMatcherBtn = document.getElementById('closeMatcherBtn');
    const matcherModal = document.getElementById('matcherModal');

    if (openMatcherBtn && closeMatcherBtn && matcherModal) {
        openMatcherBtn.addEventListener('click', () => {
            matcherModal.classList.remove('chat-hidden');
        });

        closeMatcherBtn.addEventListener('click', () => {
            matcherModal.classList.add('chat-hidden');
        });

        matcherModal.addEventListener('click', (event) => {
            if (event.target === matcherModal) {
                matcherModal.classList.add('chat-hidden');
            }
        });
    }
});

// ==========================================
// AI RECRUITER MATCHER API LOGIC
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    const modalAnalyzeBtn = document.getElementById('modalAnalyzeBtn');
    const modalJdInput = document.getElementById('modalJdInput');
    const modalResultArea = document.getElementById('modalResultArea');
    const modalFooterAction = document.getElementById('modalFooterAction');

    if (modalAnalyzeBtn && modalJdInput && modalResultArea) {
        
        modalAnalyzeBtn.addEventListener('click', async () => {
            const jdText = modalJdInput.value.trim();
            if (jdText === "") {
                alert("Please paste a Job Description first!");
                return;
            }

            const originalBtnText = modalAnalyzeBtn.innerText;
            modalAnalyzeBtn.innerText = "Analyzing Match...";
            modalAnalyzeBtn.disabled = true;
            
            modalResultArea.style.display = "block";
            modalResultArea.innerText = "AI is analyzing your resume against the Job Description... Please wait.";
            if (modalFooterAction) modalFooterAction.style.display = "none";

            const payload = { job_description: jdText };

            try {
                const response = await fetch('http://127.0.0.1:8000/api/match-job', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok && data.status === "success") {
                    modalResultArea.style.display = "block";
                    
                    // Marked library ka use karke Markdown ko clean HTML formatting mein render karna
                    if (typeof marked !== 'undefined') {
                        modalResultArea.innerHTML = marked.parse(data.match_analysis);
                    } else {
                        modalResultArea.innerText = data.match_analysis;
                    }
                    
                    if (modalFooterAction) modalFooterAction.style.display = "flex";
                
                } else {
                    modalResultArea.style.display = "block";
                    modalResultArea.innerText = "Error: Could not analyze the job description.";
                    if (modalFooterAction) modalFooterAction.style.display = "none";
                }

            } catch (error) {
                console.error("Backend Connection Error:", error);
                modalResultArea.style.display = "block";
                modalResultArea.innerText = "Failed to connect to backend server. Is FastAPI running?";
                if (modalFooterAction) modalFooterAction.style.display = "none";
            } finally {
                modalAnalyzeBtn.innerText = originalBtnText;
                modalAnalyzeBtn.disabled = false;
            }
        });
    }
});

// speech recognition logic for chat input
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById("chat-input");
    const chatMicBtn = document.getElementById("chat-mic-btn");

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition && chatMicBtn && chatInput) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-IN';
        recognition.interimResults = false;

        chatMicBtn.addEventListener('click', () => {
            try {
                chatMicBtn.style.color = "#ff6b6b"; // Recording ke dauran mic icon ka color change hoga
                recognition.start();
            } catch (e) {
                if (e.name === 'InvalidStateError') {
                    recognition.stop();
                    chatMicBtn.style.color = "var(--accent)";
                } else {
                    console.error("Speech recognition start error:", e);
                    alert("Microphone error or permission denied.");
                    chatMicBtn.style.color = "var(--accent)";
                }
            }
        });

        recognition.onresult = (event) => {
            const speechToText = event.results[0][0].transcript;
            chatInput.value = speechToText;
            chatMicBtn.style.color = "var(--accent)";
        };

        recognition.onerror = (event) => {
            // 'no-speech' error ko silently handle karenge taaki user ko unnecessary alert na aaye
            if (event.error === 'no-speech') {
                chatMicBtn.style.color = "var(--accent)";
                return;
            }
            if (event.error === 'not-allowed') {
                alert("Microphone permission is blocked by your browser. Please enable it from address bar settings.");
            }
            chatMicBtn.style.color = "var(--accent)";
        };

        recognition.onend = () => {
            chatMicBtn.style.color = "var(--accent)";
        };

    } else if (chatMicBtn) {
        chatMicBtn.style.display = "none"; // Agar browser support nahi karta toh mic button hide ho jayega
    }
});

// Quick Chips Toggle & Selection Logic
document.addEventListener('DOMContentLoaded', () => {
    const chipsToggleBtn = document.getElementById('chat-chips-toggle-btn');
    const chatChips = document.getElementById('chat-chips');
    const chatInput = document.getElementById("chat-input");

    if (chipsToggleBtn && chatChips) {
        // Toggle button click par menu open/close hoga
        chipsToggleBtn.addEventListener('click', () => {
            chatChips.classList.toggle('chips-hidden');
        });

        // Chip click karne par query input mein jayegi, menu band hoga aur message send hoga
        chatChips.addEventListener('click', (event) => {
            if (event.target.classList.contains('chat-chip')) {
                const chipText = event.target.innerText;
                chatChips.classList.add('chips-hidden'); // Menu close kar do

                // Agar user ne Contact Info chip par click kiya hai, toh direct page redirect kar do
                if (chipText.includes("Contact")) {
                    window.location.href = "contact.html";
                    return; // Yahin rok do, API call karne ki zaroorat nahi hai
                }

                // Baaki chips ke liye normal query set karke send kar do
                if (chipText.includes("Tech Stack")) query = "What is Atharva's tech stack and core skills?";
                else if (chipText.includes("Education")) query = "Tell me about Atharva's education and CGPA.";
                else if (chipText.includes("Projects")) query = "Tell me about Atharva's projects and experience.";
                else if (chipText.includes("Research")) query = "Tell me about Atharva's research paper publication.";

                chatInput.value = query;
                const chatSendBtn = document.getElementById('chat-send-btn');
                if (chatSendBtn) chatSendBtn.click();
            }
        });
    }
});