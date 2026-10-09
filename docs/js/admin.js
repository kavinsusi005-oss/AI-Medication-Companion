const apiBase = '/api';

function initAdmin() {
    setupTabs();
    setupForms();
    
    loadMedications();
    loadTodaySchedule();
    loadHistory(new Date().toISOString().split('T')[0]);
    loadInteractions();
    
    setInterval(loadTodaySchedule, 30000);
}

function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    const activeBtn = document.querySelector(`[data-tab="${tabId}"]`);
    const activeContent = document.getElementById(`tab-${tabId}`);
    if (activeBtn) activeBtn.classList.add('active');
    if (activeContent) activeContent.classList.add('active');
}

function setupForms() {
    const medForm = document.getElementById('medication-form');
    if (medForm) {
        medForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const id = document.getElementById('med-id').value;
            const data = {
                name: document.getElementById('med-name').value,
                schedule_time: document.getElementById('med-time').value,
                frequency: document.getElementById('med-frequency').value,
                instruction: document.getElementById('med-instruction').value,
                dosage: document.getElementById('med-dosage').value,
                notes: document.getElementById('med-notes').value
            };
            
            const url = id ? `${apiBase}/medications/${id}` : `${apiBase}/medications`;
            const method = id ? 'PUT' : 'POST';
            
            try {
                const res = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (res.ok) {
                    medForm.reset();
                    document.getElementById('med-id').value = '';
                    document.getElementById('save-med-btn').textContent = 'Add Medication';
                    document.getElementById('cancel-med-btn').style.display = 'none';
                    loadMedications();
                    loadTodaySchedule();
                }
            } catch (error) {
                console.error('Error saving medication:', error);
                alert('Failed to save medication');
            }
        });
    }

    const cancelBtn = document.getElementById('cancel-med-btn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            document.getElementById('medication-form').reset();
            document.getElementById('med-id').value = '';
            document.getElementById('save-med-btn').textContent = 'Add Medication';
            cancelBtn.style.display = 'none';
        });
    }

    const refreshBtn = document.getElementById('refresh-schedule-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadTodaySchedule);
    }
    
    const historyDate = document.getElementById('history-date');
    if (historyDate) {
        historyDate.value = new Date().toISOString().split('T')[0];
        historyDate.addEventListener('change', (e) => {
            loadHistory(e.target.value);
        });
    }

    const triggerBtn = document.getElementById('trigger-reminder-btn');
    if (triggerBtn) {
        triggerBtn.addEventListener('click', async () => {
            try {
                const res = await fetch(`${apiBase}/trigger-reminder`, { method: 'POST' });
                const data = await res.json();
                document.getElementById('demo-result').textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('demo-result').textContent = 'Error triggering reminder';
            }
        });
    }

    const seedBtn = document.getElementById('seed-data-btn');
    if (seedBtn) {
        seedBtn.addEventListener('click', async () => {
            if (!confirm('This will wipe existing data and add sample medications. Proceed?')) return;
            try {
                const res = await fetch(`${apiBase}/admin/seed`, { method: 'POST' });
                if (res.ok) {
                    loadMedications();
                    loadTodaySchedule();
                    loadHistory(new Date().toISOString().split('T')[0]);
                    document.getElementById('demo-result').textContent = 'Data seeded successfully!';
                }
            } catch (error) {
                document.getElementById('demo-result').textContent = 'Error seeding data';
            }
        });
    }
}

async function loadMedications() {
    try {
        const res = await fetch(`${apiBase}/medications`);
        if (!res.ok) return;
        const data = await res.json();
        
        const tbody = document.querySelector('#medications-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        window.medicationsList = data;
        
        data.forEach(med => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${med.name}</td>
                <td>${med.schedule_time}</td>
                <td>${med.frequency}</td>
                <td>${med.instruction}</td>
                <td>${med.dosage || '-'}</td>
                <td>${med.notes || '-'}</td>
                <td>
                    <button class="btn btn-small btn-primary" onclick="editMedication(${med.id})">Edit</button>
                    <button class="btn btn-small btn-danger" onclick="deleteMedication(${med.id})">Del</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading medications', error);
    }
}

window.editMedication = function(id) {
    const med = window.medicationsList.find(m => m.id === id);
    if (!med) return;
    
    document.getElementById('med-id').value = med.id;
    document.getElementById('med-name').value = med.name;
    document.getElementById('med-time').value = med.schedule_time;
    document.getElementById('med-frequency').value = med.frequency;
    document.getElementById('med-instruction').value = med.instruction;
    document.getElementById('med-dosage').value = med.dosage || '';
    document.getElementById('med-notes').value = med.notes || '';
    
    document.getElementById('save-med-btn').textContent = 'Update Medication';
    document.getElementById('cancel-med-btn').style.display = 'inline-block';
    
    window.scrollTo(0, 0);
};

window.deleteMedication = async function(id) {
    if (!confirm('Are you sure you want to delete this medication?')) return;
    
    try {
        await fetch(`${apiBase}/medications/${id}`, { method: 'DELETE' });
        loadMedications();
        loadTodaySchedule();
    } catch (error) {
        console.error('Error deleting medication', error);
    }
};

async function loadTodaySchedule() {
    try {
        const res = await fetch(`${apiBase}/admin/schedule/today`);
        if (!res.ok) return;
        const data = await res.json();
        
        const tbody = document.querySelector('#schedule-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.schedule_time || '-'}</td>
                <td>${item.name || '-'}</td>
                <td>${item.instruction || '-'}</td>
                <td>${getStatusBadge(item.status)}</td>
                <td>${item.action_time || '-'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading schedule', error);
    }
}

async function loadHistory(date) {
    try {
        let url = `${apiBase}/admin/history`;
        if (date) url += `?date=${date}`;
        const res = await fetch(url);
        if (!res.ok) return;
        const data = await res.json();
        
        const tbody = document.querySelector('#history-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.scheduled_date || '-'}</td>
                <td>${item.medication_name || '-'}</td>
                <td>${item.scheduled_time || '-'}</td>
                <td>${getStatusBadge(item.status)}</td>
                <td>${item.user_response || '-'}</td>
                <td>${item.detected_language || '-'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading history', error);
    }
}

async function loadInteractions() {
    try {
        const res = await fetch(`${apiBase}/admin/interactions`);
        if (!res.ok) return;
        const data = await res.json();
        
        const tbody = document.querySelector('#interactions-table tbody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${formatDateTime(item.created_at)}</td>
                <td>${item.user_message || '-'}</td>
                <td>${item.system_response || '-'}</td>
                <td><span class="badge bg-unknown">${item.detected_intent || 'UNKNOWN'}</span></td>
                <td>${item.detected_language || '-'}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading interactions', error);
    }
}

function getStatusBadge(status) {
    const s = status ? status.toUpperCase() : 'UNKNOWN';
    const colors = {
        'PENDING': '#f59e0b',
        'TAKEN': '#22c55e',
        'DELAYED': '#ea580c',
        'MISSED': '#ef4444',
        'NEEDS_ATTENTION': '#dc2626',
        'UNKNOWN': '#64748b'
    };
    const color = colors[s] || colors['UNKNOWN'];
    return `<span class="badge" style="background:${color};">${s}</span>`;
}

function formatDateTime(isoString) {
    if (!isoString) return '';
    return new Date(isoString).toLocaleString([], { 
        month: 'short', day: 'numeric', 
        hour: '2-digit', minute: '2-digit' 
    });
}

document.addEventListener('DOMContentLoaded', initAdmin);
