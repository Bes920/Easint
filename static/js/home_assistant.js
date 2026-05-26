(function () {
  const form = document.getElementById('guideChatForm');
  const input = document.getElementById('guideChatInput');
  const sendBtn = document.getElementById('guideChatSend');
  const messages = document.getElementById('guideChatMessages');
  const chips = document.querySelectorAll('.starter-chip');
  const SESSION_KEY = 'easint_guide_chat_history_v1';
  const TOOL_LINKS = {
    'file-upload': '/tools?tool=file-upload',
    'hash-checker': '/tools?tool=hash-checker',
    'ip-checker': '/tools?tool=ip-checker',
    'exif-extraction': '/tools?tool=exif-extraction',
    'google-dork': '/tools?tool=google-dork',
    'shodan-search': '/tools?tool=shodan-search',
    'reverse-ip': '/tools?tool=reverse-ip',
    'email-osint': '/tools?tool=email-osint',
    'wayback-machine': '/tools?tool=wayback-machine',
    'crypto-tracker': '/tools?tool=crypto-tracker',
    'mac-lookup': '/tools?tool=mac-lookup',
    'whois-lookup': '/tools?tool=whois-lookup',
    'email-breach': '/tools?tool=email-breach',
    'username-search': '/tools?tool=username-search',
    'subdomain-enum': '/tools?tool=subdomain-enum',
    'dns-lookup': '/tools?tool=dns-lookup',
    'ssl-info': '/tools?tool=ssl-info',
    'geolocate-ip': '/tools?tool=geolocate-ip',
    'phone-lookup': '/tools?tool=phone-lookup'
  };

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

  function getHistory() {
    try {
      return JSON.parse(sessionStorage.getItem(SESSION_KEY) || '[]');
    } catch (e) {
      return [];
    }
  }

  function setHistory(history) {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(history.slice(-8)));
  }

  function extractSection(text, sectionName, nextSectionNames) {
    const next = nextSectionNames.join('|');
    const regex = new RegExp(`${sectionName}:\\s*([\\s\\S]*?)(?=\\n(?:${next}):|$)`, 'i');
    const match = text.match(regex);
    return match ? match[1].trim() : '';
  }

  function getSuggestedTools(text) {
    const found = [];
    Object.keys(TOOL_LINKS).forEach((tool) => {
      if (text.toLowerCase().includes(tool)) found.push(tool);
    });
    return found.slice(0, 4);
  }

  function addStructuredAssistantMessage(rawText) {
    const supported = extractSection(rawText, 'Supported', ['Steps', 'Required Inputs', 'Expected Result', 'If Not Supported']);
    const steps = extractSection(rawText, 'Steps', ['Required Inputs', 'Expected Result', 'If Not Supported']);
    const inputs = extractSection(rawText, 'Required Inputs', ['Expected Result', 'If Not Supported']);
    const expected = extractSection(rawText, 'Expected Result', ['If Not Supported']);
    const notSupported = extractSection(rawText, 'If Not Supported', []);
    const tools = getSuggestedTools(rawText);

    const wrap = document.createElement('div');
    wrap.className = 'guide-message assistant';
    const card = document.createElement('div');
    card.className = 'guide-bubble guide-structured';

    const blocks = [
      ['Supported', supported || 'Not specified'],
      ['Steps', steps || 'No steps provided'],
      ['Required Inputs', inputs || 'No inputs specified'],
      ['Expected Result', expected || 'No expected result specified'],
      ['If Not Supported', notSupported || 'Not applicable']
    ];

    blocks.forEach(([title, body]) => {
      const block = document.createElement('div');
      block.className = 'guide-block';
      block.innerHTML = `<strong>${title}</strong><p>${body.replace(/\n/g, '<br>')}</p>`;
      card.appendChild(block);
    });

    if (tools.length) {
      const actions = document.createElement('div');
      actions.className = 'guide-actions';
      tools.forEach((tool) => {
        const link = document.createElement('a');
        link.href = TOOL_LINKS[tool];
        link.className = 'guide-action-link';
        link.textContent = `Open ${tool}`;
        actions.appendChild(link);
      });
      card.appendChild(actions);
    }

    const copyBtn = document.createElement('button');
    copyBtn.type = 'button';
    copyBtn.className = 'guide-copy-btn';
    copyBtn.textContent = 'Copy Steps';
    copyBtn.addEventListener('click', async () => {
      await navigator.clipboard.writeText(rawText);
      copyBtn.textContent = 'Copied';
      setTimeout(() => { copyBtn.textContent = 'Copy Steps'; }, 1200);
    });
    card.appendChild(copyBtn);

    wrap.appendChild(card);
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
      const history = getHistory();
      const response = await fetch('/ai/guide-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText, chat_history: history })
      });
      const data = await response.json();
      if (!data.success) {
        addMessage(data.error || 'Assistant is unavailable right now.', 'assistant');
      } else {
        addStructuredAssistantMessage(data.response);
        const newHistory = [...history, { role: 'user', content: userText }, { role: 'assistant', content: data.response }];
        setHistory(newHistory);
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
