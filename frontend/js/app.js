// CONFIGURATION
const USE_MOCK_API = true;

// Managed Azure Functions API Base URL
const API_BASE_URL = window.location.origin.includes('localhost')
  ? 'http://localhost:7071/api'
  : '/api';

// DOM ELEMENTS
const ticketForm = document.getElementById('ticketForm');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const titleInput = document.getElementById('title');
const descInput = document.getElementById('description');
const priorityInput = document.getElementById('priority');
const categoryInput = document.getElementById('category');
const submitBtn = document.getElementById('submitBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const btnSuggestCategory = document.getElementById('btnSuggestCategory');
const categoryHint = document.getElementById('categoryHint');
const statusMessage = document.getElementById('statusMessage');

// FORM VALIDATION
function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function clearValidationErrors() {
  document.querySelectorAll('.error-text').forEach((el) => (el.textContent = ''));
  document.querySelectorAll('.is-invalid').forEach((el) => el.classList.remove('is-invalid'));
}

function setError(inputElement, errorElementId, message) {
  inputElement.classList.add('is-invalid');
  document.getElementById(errorElementId).textContent = message;
}

function validateForm() {
  clearValidationErrors();
  let isValid = true;

  // Validate Name
  if (!nameInput.value.trim()) {
    setError(nameInput, 'nameError', 'Full name is required.');
    isValid = false;
  }

  // Validate Email
  if (!emailInput.value.trim()) {
    setError(emailInput, 'emailError', 'Email address is required.');
    isValid = false;
  } else if (!validateEmail(emailInput.value.trim())) {
    setError(emailInput, 'emailError', 'Please enter a valid email address.');
    isValid = false;
  }

  // Validate Title
  if (!titleInput.value.trim()) {
    setError(titleInput, 'titleError', 'Subject title is required.');
    isValid = false;
  }

  // Validate Description
  if (!descInput.value.trim()) {
    setError(descInput, 'descriptionError', 'Please provide a detailed description.');
    isValid = false;
  } else if (descInput.value.trim().length < 10) {
    setError(descInput, 'descriptionError', 'Description must be at least 10 characters.');
    isValid = false;
  }

  return isValid;
}

// UI FEEDBACK HELPERS
function showMessage(type, text) {
  statusMessage.className = `message-banner ${type}`;
  statusMessage.textContent = text;
  statusMessage.classList.remove('hidden');
  statusMessage.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function toggleLoading(isLoading) {
  submitBtn.disabled = isLoading;
  const label = submitBtn.querySelector('.btn-text-label');
  if (isLoading) {
    loadingSpinner.classList.remove('hidden');
    label.textContent = 'Submitting...';
  } else {
    loadingSpinner.classList.add('hidden');
    label.textContent = 'Submit Ticket';
  }
}

// AI suggestion
async function suggestCategory() {
  const text = (titleInput.value + ' ' + descInput.value).toLowerCase();

  if (text.trim().length < 5) {
    categoryHint.textContent = 'Please enter a title or description first.';
    return;
  }

  categoryHint.textContent = 'Analyzing text...';

  // AI Classification MOCK
  if (USE_MOCK_API) {
    setTimeout(() => {
      let suggested = 'General Enquiry';
      if (text.includes('wifi') || text.includes('laptop') || text.includes('password') || text.includes('login')) {
        suggested = 'IT Support';
      } else if (text.includes('aircond') || text.includes('light') || text.includes('toilet') || text.includes('door')) {
        suggested = 'Facilities';
      } else if (text.includes('course') || text.includes('module') || text.includes('enroll') || text.includes('class')) {
        suggested = 'Course Registration';
      } else if (text.includes('fee') || text.includes('refund') || text.includes('scholarship') || text.includes('payment')) {
        suggested = 'Student Finance';
      } else if (text.includes('book') || text.includes('borrow') || text.includes('journal')) {
        suggested = 'Library Services';
      }
      categoryInput.value = suggested;
      categoryHint.textContent = ``;
    }, 400);
    return;
  }

  // Call Azure Function for AI Classification 
  try {
    const response = await fetch(`${API_BASE_URL}/classify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });

    if (response.ok) {
      const data = await response.json();
      if (data.category) {
        categoryInput.value = data.category;
        categoryHint.textContent = `AI Suggested: ${data.category}`;
      }
    }
  } catch (err) {
    categoryHint.textContent = 'Manual selection available.';
  }
}

btnSuggestCategory.addEventListener('click', suggestCategory);

// Auto-trigger suggestion after description
descInput.addEventListener('blur', () => {
  if (descInput.value.length > 10 && categoryInput.value === 'General Enquiry') {
    suggestCategory();
  }
});

// FORM SUBMISSION HANDLER
ticketForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (!validateForm()) return;

  // Build ticket payload
  const ticketData = {
    name: nameInput.value.trim(),
    email: emailInput.value.trim(),
    title: titleInput.value.trim(),
    description: descInput.value.trim(),
    priority: priorityInput.value,
    category: categoryInput.value,
    status: 'New',
    createdAt: new Date().toISOString()
  };

  toggleLoading(true);
  statusMessage.classList.add('hidden');

  try {
    if (USE_MOCK_API) {
      // Simulating network delay for mock API - 1s
      await new Promise((res) => setTimeout(res, 1000));
      console.log('Mock Payload Saved:', ticketData);
    } else {
      // Send to Azure Functions API
      const res = await fetch(`${API_BASE_URL}/tickets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ticketData)
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}: ${res.statusText}`);
      }
    }

    showMessage('success', 'Your ticket has been submitted successfully. A helpdesk agent will review it shortly.');
    ticketForm.reset();
    categoryHint.textContent = '';
  } catch (error) {
    console.error('Submission failed:', error);
    showMessage('error', 'Failed to submit ticket. Please check your network and try again.');
  } finally {
    toggleLoading(false);
  }
});