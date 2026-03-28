const chatWindow = document.getElementById("chatWindow");

if (chatWindow) {
  const HISTORY_KEY = "libra-chat-history";
  const aiStatus = document.getElementById("aiStatus");
  const aiOrb = document.getElementById("aiOrb");
  const chatShell = document.getElementById("chatShell");
  const chatForm = document.getElementById("chatForm");
  const userInput = document.getElementById("userInput");
  const sendButton = document.getElementById("sendButton");
  const voiceToggle = document.getElementById("voiceToggle");
  const storeBackend = document.getElementById("storeBackend");
  const voiceState = document.getElementById("voiceState");
  const modeLabel = document.getElementById("modeLabel");
  const signalText = document.getElementById("signalText");
  const signalMode = document.getElementById("signalMode");
  const messageCount = document.getElementById("messageCount");
  const messageMirror = document.getElementById("messageMirror");
  const charCount = document.getElementById("charCount");
  const eventFeed = document.getElementById("eventFeed");
  const pulseState = document.getElementById("pulseState");
  const focusValue = document.getElementById("focusValue");
  const focusFill = document.getElementById("focusFill");
  const resonanceValue = document.getElementById("resonanceValue");
  const resonanceFill = document.getElementById("resonanceFill");
  const responseValue = document.getElementById("responseValue");
  const responseFill = document.getElementById("responseFill");
  const actionButtons = document.querySelectorAll("[data-command]");

  const state = {
    isSending: false,
    voiceEnabled: false,
    selectedVoice: null,
  };

  function formatTime(date = new Date()) {
    return date.toLocaleTimeString([], {
      hour: "numeric",
      minute: "2-digit",
    });
  }

  function setMeter(valueNode, fillNode, value) {
    if (!valueNode || !fillNode) {
      return;
    }

    const safeValue = Math.max(8, Math.min(100, Math.round(value)));
    valueNode.textContent = `${safeValue}%`;
    fillNode.style.width = `${safeValue}%`;
  }

  function logEvent(label, text) {
    if (!eventFeed) {
      return;
    }

    const item = document.createElement("div");
    item.className = "event-item";

    const badge = document.createElement("span");
    badge.textContent = label;

    const body = document.createElement("p");
    body.textContent = text;

    const time = document.createElement("small");
    time.textContent = formatTime();

    item.append(badge, body, time);
    eventFeed.prepend(item);

    while (eventFeed.children.length > 6) {
      eventFeed.removeChild(eventFeed.lastElementChild);
    }
  }

  function setStatus(text, status = "ready") {
    if (!aiStatus) {
      return;
    }

    aiStatus.textContent = text;
    aiStatus.dataset.state = status;

    if (signalText) {
      const signalCopy = {
        ready: "Systems stable. Ready for a new prompt.",
        thinking: "Processing your transmission through the relay.",
        offline: "Cloud AI is unavailable. Local fallback has the deck.",
        warning: "Signal dipped, but the interface is still responding.",
      };
      signalText.textContent = signalCopy[status] || signalCopy.ready;
    }

    if (pulseState) {
      const pulseCopy = {
        ready: "Nominal",
        thinking: "Charging",
        offline: "Fallback",
        warning: "Alert",
      };
      pulseState.textContent = pulseCopy[status] || "Nominal";
    }
  }

  function setSending(isSending) {
    state.isSending = isSending;
    userInput.disabled = isSending;
    sendButton.disabled = isSending;

    if (isSending) {
      sendButton.textContent = "Sending";
      setMeter(responseValue, responseFill, 88);
      return;
    }

    sendButton.textContent = "Send";
    userInput.focus();
  }

  function createMessageBubble(role, text, timestamp = new Date().toISOString()) {
    const bubble = document.createElement("article");
    bubble.className = `message ${role}`;
    bubble.dataset.role = role;
    bubble.dataset.timestamp = timestamp;

    const meta = document.createElement("div");
    meta.className = "message-meta";

    const author = document.createElement("span");
    author.textContent = role === "user" ? "You" : "LIBRA";

    const time = document.createElement("span");
    time.textContent = formatTime(new Date(timestamp));

    meta.append(author, time);

    const body = document.createElement("p");
    body.className = "message-body";
    body.textContent = text;

    bubble.append(meta, body);
    return bubble;
  }

  function renderBubble(role, text, timestamp) {
    const bubble = createMessageBubble(role, text, timestamp);
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    updateMessageCount();
  }

  function serializeHistory() {
    const items = Array.from(chatWindow.querySelectorAll(".message")).map((node) => ({
      role: node.dataset.role,
      text: node.querySelector(".message-body")?.textContent || "",
      timestamp: node.dataset.timestamp || new Date().toISOString(),
    }));
    sessionStorage.setItem(HISTORY_KEY, JSON.stringify(items));
  }

  function loadHistory() {
    const raw = sessionStorage.getItem(HISTORY_KEY);
    if (!raw) {
      return false;
    }

    try {
      const items = JSON.parse(raw);
      items.forEach((item) => {
        if (item.role && item.text) {
          renderBubble(item.role, item.text, item.timestamp);
        }
      });
      updateMessageCount();
      return items.length > 0;
    } catch (error) {
      sessionStorage.removeItem(HISTORY_KEY);
      return false;
    }
  }

  function addUserBubble(text) {
    renderBubble("user", text);
    serializeHistory();
  }

  function addAIBubble(text) {
    renderBubble("ai", text);
    serializeHistory();
  }

  function speak(text) {
    if (!state.voiceEnabled || !("speechSynthesis" in window)) {
      return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1.04;
    utterance.volume = 1;

    if (state.selectedVoice) {
      utterance.voice = state.selectedVoice;
    }

    window.speechSynthesis.speak(utterance);
  }

  function finish(text, status = "ready") {
    const statusText = {
      ready: "Ready to chat",
      offline: "Offline mode active",
      warning: "Attention needed",
      thinking: "Thinking...",
    };

    addAIBubble(text);
    setStatus(statusText[status] || "Ready to chat", status);
    updateMode(status === "offline" ? "Offline reply" : "Live response");
    updateSignalMetrics(text.length, status);
    speak(text);
    setSending(false);
  }

  function updateMode(label) {
    if (modeLabel) {
      modeLabel.textContent = label;
    }

    if (signalMode) {
      signalMode.textContent = label;
    }
  }

  function updateMessageCount() {
    const total = chatWindow.querySelectorAll(".message").length;

    if (messageCount) {
      messageCount.textContent = String(total);
    }

    if (messageMirror) {
      messageMirror.textContent = String(total);
    }
  }

  function updateInputCount() {
    if (!charCount) {
      return;
    }

    charCount.textContent = String(userInput.value.trim().length);
  }

  function updateSignalMetrics(length, status = "ready", latency = 320) {
    const focusScore = 34 + Math.min(length * 2.4, 58);
    const resonanceScore =
      status === "offline"
        ? 54
        : status === "warning"
          ? 48
          : status === "thinking"
            ? 72
            : 65 + Math.min(length * 0.45, 22);
    const responseScore = Math.max(24, 100 - latency / 16);

    setMeter(focusValue, focusFill, focusScore);
    setMeter(resonanceValue, resonanceFill, resonanceScore);
    setMeter(responseValue, responseFill, responseScore);
  }

  function loadVoices() {
    if (!("speechSynthesis" in window)) {
      return;
    }

    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find((voice) => voice.lang.toLowerCase().startsWith("en"));
    state.selectedVoice = englishVoice || voices[0] || null;
  }

  function toggleVoice() {
    state.voiceEnabled = !state.voiceEnabled;
    voiceToggle.textContent = state.voiceEnabled ? "Voice on" : "Voice off";
    voiceToggle.setAttribute("aria-pressed", String(state.voiceEnabled));
    aiOrb.classList.toggle("voice-active", state.voiceEnabled);

    if (voiceState) {
      voiceState.textContent = state.voiceEnabled ? "On" : "Off";
    }

    logEvent("VOICE", state.voiceEnabled ? "Voice output engaged." : "Voice output disengaged.");
    setMeter(resonanceValue, resonanceFill, state.voiceEnabled ? 83 : 58);

    if (!state.voiceEnabled && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
  }

  function openSearch(url, message) {
    window.open(url, "_blank", "noopener");
    return message;
  }

  function handleLocalCommand(message) {
    const normalized = message.toLowerCase();

    if (normalized === "libra") {
      return "I am here and listening.";
    }

    if (normalized === "help") {
      return "Try a question, describe your mood, or use commands like time, date, clear chat, open example.com, or search futuristic UI ideas.";
    }

    if (normalized === "time") {
      return `The current time is ${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}.`;
    }

    if (normalized === "date") {
      return `Today is ${new Date().toDateString()}.`;
    }

    if (normalized === "clear chat") {
      chatWindow.innerHTML = "";
      sessionStorage.removeItem(HISTORY_KEY);
      updateMessageCount();
      logEvent("CLEAR", "Conversation history cleared from this browser session.");
      return "Chat cleared.";
    }

    if (normalized.startsWith("open ")) {
      const site = normalized.replace("open ", "").trim();
      const url = site.includes(".") ? `https://${site}` : `https://${site}.com`;
      logEvent("OPEN", `Launching ${site}.`);
      return openSearch(url, `Opening ${site}.`);
    }

    if (normalized.startsWith("search ")) {
      const query = normalized.replace("search ", "").trim();
      if (!query) {
        return "Tell me what you want to search for.";
      }

      logEvent("SEARCH", `External search requested for "${query}".`);
      return openSearch(
        `https://www.google.com/search?q=${encodeURIComponent(query)}`,
        `Searching for ${query}.`
      );
    }

    if (["exit", "quit", "bye", "stop"].includes(normalized)) {
      return "Session paused. You can message me again any time.";
    }

    return null;
  }

  async function sendToAI(message) {
    const typingBubble = createMessageBubble("ai", "LIBRA is thinking");
    typingBubble.classList.add("typing");
    chatWindow.appendChild(typingBubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    const startedAt = performance.now();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const latency = performance.now() - startedAt;
      const data = await response.json();
      typingBubble.remove();

      if (!response.ok) {
        finish(data.reply || "Something went wrong.", "warning");
        updateSignalMetrics(message.length, "warning", latency);
        logEvent("WARN", "Backend responded with a recoverable warning.");
        return;
      }

      if (storeBackend && data.store) {
        storeBackend.textContent = data.store;
      }

      finish(
        data.reply || "I could not generate a response.",
        data.mode === "offline" ? "offline" : "ready"
      );
      updateMode(data.mode === "offline" ? "Offline reply" : "Gemini live");
      updateSignalMetrics(message.length, data.mode === "offline" ? "offline" : "ready", latency);
      logEvent(
        data.mode === "offline" ? "LOCAL" : "CLOUD",
        data.mode === "offline"
          ? "Fallback mode generated the latest reply."
          : `Gemini responded in ${Math.round(latency)} ms.`
      );
    } catch (error) {
      typingBubble.remove();
      finish("Backend not responding. Check the Flask console when you can.", "warning");
      updateMode("Signal lost");
      updateSignalMetrics(message.length, "warning", 1200);
      logEvent("ERROR", "Lost connection to the backend while requesting a reply.");
    }
  }

  function markActionButton(button) {
    actionButtons.forEach((node) => node.classList.remove("is-active"));
    if (!button) {
      return;
    }

    button.classList.add("is-active");
    window.setTimeout(() => button.classList.remove("is-active"), 1200);
  }

  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (state.isSending) {
      return;
    }

    const message = userInput.value.trim();
    if (!message) {
      return;
    }

    userInput.value = "";
    updateInputCount();
    addUserBubble(message);
    setSending(true);
    setStatus("Thinking...", "thinking");
    updateMode("Processing");
    updateSignalMetrics(message.length, "thinking", 260);
    logEvent("SEND", `Transmitting ${message.length} characters to the relay.`);

    const commandReply = handleLocalCommand(message);
    if (commandReply) {
      finish(commandReply, "ready");
      updateMode("Local shortcut");
      return;
    }

    await sendToAI(message);
  });

  actionButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      const command = button.dataset.command;
      if (!command || state.isSending) {
        return;
      }

      markActionButton(button);
      userInput.value = command;
      updateInputCount();
      logEvent("DECK", `Loaded shortcut: ${command}.`);
      chatForm.requestSubmit();
    });
  });

  function attachPointerGlow() {
    if (!chatShell) {
      return;
    }

    chatShell.addEventListener("pointermove", (event) => {
      const rect = chatShell.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      const xOffset = (x / 100 - 0.5) * 18;
      const yOffset = (y / 100 - 0.5) * 18;
      const rotateX = (50 - y) * 0.08;
      const rotateY = (x - 50) * 0.08;

      chatShell.style.setProperty("--pointer-x", `${x}%`);
      chatShell.style.setProperty("--pointer-y", `${y}%`);
      aiOrb.style.transform =
        `translate(${xOffset}px, ${yOffset}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });

    chatShell.addEventListener("pointerleave", () => {
      chatShell.style.setProperty("--pointer-x", "50%");
      chatShell.style.setProperty("--pointer-y", "50%");
      aiOrb.style.transform = "translate(0, 0) rotateX(0deg) rotateY(0deg)";
    });
  }

  async function bootstrapConnection() {
    try {
      const response = await fetch("/api/ping");
      const data = await response.json();

      if (storeBackend && data.store) {
        storeBackend.textContent = data.store;
      }

      if (data.aiMode === "online") {
        updateMode("Gemini live");
        logEvent("SYNC", "Cloud AI connection ready.");
      } else {
        updateMode("Offline standby");
        logEvent("SYNC", "Cloud AI unavailable. Local fallback armed.");
      }

      setStatus("Ready to chat", "ready");
      updateSignalMetrics(16, data.aiMode === "online" ? "ready" : "offline", 240);
    } catch (error) {
      updateMode("Standby");
      setStatus("Ready to chat", "ready");
      logEvent("SYNC", "Booted locally without live connection details.");
      updateSignalMetrics(10, "warning", 950);
    }
  }

  voiceToggle.addEventListener("click", toggleVoice);
  userInput.addEventListener("input", updateInputCount);

  const hasHistory = loadHistory();
  loadVoices();
  attachPointerGlow();
  bootstrapConnection();
  updateMessageCount();
  updateInputCount();
  updateMode("Standby");

  if (!hasHistory) {
    addAIBubble("Neural relay online. Send a message or launch a quick action to begin.");
    logEvent("BOOT", "Seeded the conversation chamber with a ready-state greeting.");
  }

  if ("speechSynthesis" in window) {
    window.speechSynthesis.onvoiceschanged = loadVoices;
  } else {
    voiceToggle.disabled = true;
    voiceToggle.textContent = "Voice n/a";
    if (voiceState) {
      voiceState.textContent = "Unavailable";
    }
  }

  userInput.focus();
}
