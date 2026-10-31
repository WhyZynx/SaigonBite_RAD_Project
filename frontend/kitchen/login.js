const $ = id => document.getElementById(id);
const form = $('login-form');
const alertBox = $('form-alert');

function showError(message) {
  alertBox.textContent = message;
  alertBox.hidden = false;
}

function clearErrors() {
  alertBox.hidden = true;
  $('email-error').hidden = true;
  $('password-error').hidden = true;
}

async function createSession(url, payload, button, pendingText) {
  clearErrors();
  const originalText = button.innerHTML;
  button.disabled = true;
  button.textContent = pendingText;
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      credentials: 'same-origin',
      body: payload ? JSON.stringify(payload) : undefined,
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || 'Unable to sign in. Please try again.');
    window.location.assign(result.redirect_url || '/');
  } catch (error) {
    showError(error.message || 'Unable to connect. Check your connection and try again.');
    button.disabled = false;
    button.innerHTML = originalText;
  }
}

form.addEventListener('submit', event => {
  event.preventDefault();
  clearErrors();
  const email = $('email').value.trim();
  const password = $('password').value;
  let valid = true;
  if (!email || !$('email').validity.valid) {
    $('email-error').hidden = false;
    valid = false;
  }
  if (!password) {
    $('password-error').hidden = false;
    valid = false;
  }
  if (valid) createSession('/api/auth/login', {email, password}, $('sign-in'), 'Signing in…');
});

$('toggle-password').addEventListener('click', event => {
  const password = $('password');
  const visible = password.type === 'password';
  password.type = visible ? 'text' : 'password';
  event.currentTarget.textContent = visible ? 'Hide' : 'Show';
  event.currentTarget.setAttribute('aria-label', visible ? 'Hide password' : 'Show password');
});
form.addEventListener('input', () => { if (!alertBox.hidden) clearErrors(); });
