(function () {
  const form = document.getElementById('guideChatForm');
  const input = document.getElementById('guideChatInput');
  const sendBtn = document.getElementById('guideChatSend');
  const messages = document.getElementById('guideChatMessages');
  const chips = document.querySelectorAll('.starter-chip');

  if (!form || !input || !sendBtn || !messages) return;

  function addMessage(text, who) {
    const wrap = document.createElement('div');
    wrap.className = `guide-message ${who}`;
    const bubble = document.createElement('div');
    bubble.className = 'guide-bubble';
    bubble.textContent = text;
    wrap.appendChild(bubble);
    messages.appendChild(wrap);
    messages.scrollTop = messages.scrollHeight;
  }

  async function sendMessage(message) {
    const userText = (message || input.value || '').trim();
    if (!userText) return;

    addMessage(userText, 'user');
    input.value = '';
    input.disabled = true;
    sendBtn.disabled = true;

    try {
      const response = await fetch('/ai/guide-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText })
      });
      const data = await response.json();
      if (!data.success) {
        addMessage(data.error || 'Assistant is unavailable right now.', 'assistant');
      } else {
        addMessage(data.response, 'assistant');
      }
    } catch (err) {
      addMessage('Assistant is currently unavailable. Please try again shortly.', 'assistant');
    } finally {
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    sendMessage();
  });

  chips.forEach((chip) => {
    chip.addEventListener('click', function () {
      sendMessage(chip.dataset.question || chip.textContent);
    });
  });
})();
