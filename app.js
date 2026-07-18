const form = document.querySelector('#chat-form');
const question = document.querySelector('#question');
const userId = document.querySelector('#user-id');
const messages = document.querySelector('#messages');
const send = document.querySelector('#send');

function addMessage(text, kind, route) {
  const article = document.createElement('article');
  article.className = `message ${kind}-message`;
  if (kind === 'assistant') article.innerHTML = '<span class="avatar" aria-hidden="true">S</span>';
  const content = document.createElement('div');
  const paragraph = document.createElement('p');
  paragraph.textContent = text;
  content.append(paragraph);
  if (route) { const tag = document.createElement('span'); tag.className = 'route-tag'; tag.textContent = route === 'escalate' ? 'Specialist support' : 'Sezzle assistant'; content.append(tag); }
  article.append(content); messages.append(article); messages.scrollTop = messages.scrollHeight;
  return article;
}

function addTyping() {
  const article = document.createElement('article');
  article.className = 'message assistant-message';
  article.innerHTML = '<span class="avatar" aria-hidden="true">S</span>';
  const content = document.createElement('div');
  const dots = document.createElement('div');
  dots.className = 'typing-dots';
  dots.setAttribute('role', 'status');
  dots.setAttribute('aria-label', 'Assistant is typing');
  dots.innerHTML = '<span></span><span></span><span></span>';
  content.append(dots);
  article.append(content); messages.append(article); messages.scrollTop = messages.scrollHeight;
  return article;
}

document.querySelectorAll('.suggestions button').forEach((button) => button.addEventListener('click', () => {
  question.value = button.textContent; question.focus();
}));

question.addEventListener('input', () => { question.style.height = 'auto'; question.style.height = `${Math.min(question.scrollHeight, 100)}px`; });

// Enter sends the message; Shift+Enter inserts a newline.
question.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); }
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const text = question.value.trim(); if (!text) return;
  addMessage(text, 'user'); question.value = ''; question.style.height = 'auto'; send.disabled = true;
  const pending = addTyping();
  try {
    const response = await fetch('/api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: text, user_id: userId.value }) });
    const result = await response.json();
    pending.remove();
    if (!response.ok) throw new Error(result.error || 'Something went wrong.');
    addMessage(result.answer, 'assistant', result.route);
  } catch (error) { pending.remove(); addMessage(error.message || 'Unable to reach support right now. Please try again.', 'assistant'); }
  finally { send.disabled = false; question.focus(); }
});
