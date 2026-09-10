// CONFIGURATION
const USE_MOCK_API = true;

// Managed Azure Functions API Base URL
const API_BASE_URL = window.location.origin.includes('localhost')
  ? 'http://localhost:7071/api'
  : '/api';

// Initial Mock Dataset for testing without Azure connection
let tickets = [
  {
    id: "TCK-1001",
    email: "aiman@example.com",
    title: "Cannot access campus Wi-Fi",
    description: "I cannot connect to the campus Wi-Fi from my laptop in Block B.",
    category: "IT Support",
    priority: "Medium",
    status: "New",
    createdAt: "2026-08-30T10:15:00Z"
  },
  {
    id: "TCK-1002",
    email: "sarah.lee@example.com",
    title: "Air conditioning leaking in Lab 3",
    description: "Water is dripping directly over computer terminal #12.",
    category: "Facilities",
    priority: "High",
    status: "In Progress",
    createdAt: "2026-08-31T08:30:00Z"
  },
  {
    id: "TCK-1003",
    email: "danial@example.com",
    title: "Cannot enroll in AZ-200 elective",
    description: "Portal says prerequisite missing, but I already passed it.",
    category: "Course Registration",
    priority: "High",
    status: "Categorised",
    createdAt: "2026-09-01T02:00:00Z"
  }
];

// DOM ELEMENTS
const ticketTableBody = document.getElementById('ticketTableBody');
const searchQuery = document.getElementById('searchQuery');
const statusFilter = document.getElementById('statusFilter');
const categoryFilter = document.getElementById('categoryFilter');
const btnRefresh = document.getElementById('btnRefresh');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const adminMessage = document.getElementById('adminMessage');

// FETCH TICKETS
async function fetchTickets() {
  setLoading(true);
  adminMessage.classList.add('hidden');

  try {
    if (USE_MOCK_API) {
      await new Promise(res => setTimeout(res, 500));
    } else {
      const res = await fetch(`${API_BASE_URL}/tickets`);
      if (!res.ok) throw new Error('Failed to retrieve tickets.');
      tickets = await res.json();
    }
    renderTickets();
  } catch (err) {
    showAdminMessage('error', 'Error loading tickets from server.');
    console.error(err);
  } finally {
    setLoading(false);
  }
}

// UPDATE TICKET STATUS
async function updateTicketStatus(ticketId, newStatus) {
  try {
    if (USE_MOCK_API) {
      // Local state update
      const target = tickets.find(t => t.id === ticketId);
      if (target) target.status = newStatus;
      showAdminMessage('success', `Ticket ${ticketId} updated to "${newStatus}".`);
      renderTickets();
    } else {
      const res = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (!res.ok) throw new Error('Failed to update status on server.');

      const target = tickets.find(t => t.id === ticketId);
      if (target) target.status = newStatus;
      showAdminMessage('success', `Ticket ${ticketId} updated successfully.`);
      renderTickets();
    }
  } catch (err) {
    showAdminMessage('error', 'Could not update ticket status. Try again.');
    console.error(err);
  }
}

// RENDER TICKETS & FILTERING
function renderTickets() {
  ticketTableBody.innerHTML = '';

  const q = searchQuery.value.toLowerCase().trim();
  const selectedStatus = statusFilter.value;
  const selectedCat = categoryFilter.value;

  // Filter conditions
  const filtered = tickets.filter(ticket => {
    const matchesSearch = 
      ticket.email.toLowerCase().includes(q) ||
      ticket.title.toLowerCase().includes(q) ||
      ticket.description.toLowerCase().includes(q) ||
      (ticket.id && ticket.id.toLowerCase().includes(q));

    const matchesStatus = selectedStatus === 'ALL' || ticket.status === selectedStatus;
    const matchesCategory = selectedCat === 'ALL' || ticket.category === selectedCat;

    return matchesSearch && matchesStatus && matchesCategory;
  });

  if (filtered.length === 0) {
    emptyState.classList.remove('hidden');
    return;
  } else {
    emptyState.classList.add('hidden');
  }

  // Generate Table Rows
  filtered.forEach(ticket => {
    const row = document.createElement('tr');
    
    // Format timestamp
    const dateFormatted = new Date(ticket.createdAt).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });

    const statusClass = `pill-status-${ticket.status.replace(/\s+/g, '-')}`;
    const priorityClass = `pill-priority-${ticket.priority || 'Medium'}`;

    row.innerHTML = `
      <td>
        <div class="ticket-meta-date">${dateFormatted}</div>
        <div class="ticket-meta-email">${escapeHtml(ticket.email)}</div>
      </td>
      <td>
        <div class="ticket-title">${escapeHtml(ticket.title)}</div>
        <div class="ticket-desc">${escapeHtml(ticket.description)}</div>
      </td>
      <td>
        <strong>${escapeHtml(ticket.category || 'General Enquiry')}</strong>
      </td>
      <td>
        <span class="pill ${priorityClass}">${ticket.priority || 'Medium'}</span>
      </td>
      <td>
        <span class="pill ${statusClass}">${ticket.status}</span>
      </td>
      <td>
        <select class="status-select" data-id="${ticket.id}">
          <option value="New" ${ticket.status === 'New' ? 'selected' : ''}>New</option>
          <option value="Categorised" ${ticket.status === 'Categorised' ? 'selected' : ''}>Categorised</option>
          <option value="In Progress" ${ticket.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
          <option value="Resolved" ${ticket.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
        </select>
      </td>
    `;

    // Bind inline status change event
    const select = row.querySelector('.status-select');
    select.addEventListener('change', (e) => {
      updateTicketStatus(ticket.id, e.target.value);
    });

    ticketTableBody.appendChild(row);
  });
}

// UTILITY FUNCTIONS
function setLoading(isLoading) {
  if (isLoading) {
    loadingState.classList.remove('hidden');
    ticketTableBody.innerHTML = '';
    emptyState.classList.add('hidden');
  } else {
    loadingState.classList.add('hidden');
  }
}

function showAdminMessage(type, msg) {
  adminMessage.className = `message-banner ${type}`;
  adminMessage.textContent = msg;
  adminMessage.classList.remove('hidden');
  setTimeout(() => adminMessage.classList.add('hidden'), 4000);
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// EVENT LISTENERS
searchQuery.addEventListener('input', renderTickets);
statusFilter.addEventListener('change', renderTickets);
categoryFilter.addEventListener('change', renderTickets);
btnRefresh.addEventListener('click', fetchTickets);

// Initial Page Load
document.addEventListener('DOMContentLoaded', fetchTickets);