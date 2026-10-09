let currentYear = 2026;
let currentMonth = 9; // October
let selectedDay = 19; // Monday Oct 19

const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function initSchedulePage() {
    loadPatientProfile();
    renderMiniCalendar();
    updateTimelineDateLabel();
    setupEventListeners();
}

function loadPatientProfile() {
    const savedProfile = localStorage.getItem('medmate-user-profile');
    const nameDisplay = document.getElementById('patient-name-display');
    if (savedProfile) {
        try {
            const data = JSON.parse(savedProfile);
            if (data.name && nameDisplay) {
                nameDisplay.textContent = `${data.name}'s Schedule`;
            }
        } catch (e) {
            console.error('Error loading patient profile', e);
        }
    }
}

function setupEventListeners() {
    const prevBtn = document.getElementById('prev-month-btn');
    const nextBtn = document.getElementById('next-month-btn');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            currentMonth--;
            if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            }
            updateMonthDisplay();
            renderMiniCalendar();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            currentMonth++;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            updateMonthDisplay();
            renderMiniCalendar();
        });
    }
}

function updateMonthDisplay() {
    const label = `${monthNames[currentMonth]} ${currentYear}`;
    const monthLabel = document.getElementById('current-month-label');
    const scheduleHeading = document.getElementById('schedule-heading');
    const miniCalTitle = document.getElementById('mini-cal-title');

    if (monthLabel) monthLabel.textContent = label;
    if (scheduleHeading) scheduleHeading.textContent = `Schedule: ${label}`;
    if (miniCalTitle) miniCalTitle.textContent = label;
}

function renderMiniCalendar() {
    updateMonthDisplay();

    const container = document.getElementById('mini-cal-cells-container');
    if (!container) return;
    container.innerHTML = '';

    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    for (let i = 0; i < firstDay; i++) {
        const empty = document.createElement('div');
        empty.className = 'cal-cell';
        empty.style.opacity = '0.15';
        empty.style.pointerEvents = 'none';
        container.appendChild(empty);
    }

    for (let day = 1; day <= daysInMonth; day++) {
        const cell = document.createElement('div');
        cell.className = 'cal-cell';
        if (day === selectedDay) {
            cell.classList.add('selected');
        }

        const num = document.createElement('span');
        num.className = 'cal-cell-num';
        num.textContent = day;
        cell.appendChild(num);

        const dots = document.createElement('div');
        dots.className = 'cal-cell-dots';

        if (day === 10 || day === 21) {
            dots.innerHTML = '<div class="micro-dot green"></div><div class="micro-dot green"></div><div class="micro-dot red"></div>';
        } else if (day === 3 || day === 17 || day === 24) {
            dots.innerHTML = '<div class="micro-dot yellow"></div><div class="micro-dot yellow"></div><div class="micro-dot yellow"></div>';
        } else {
            dots.innerHTML = '<div class="micro-dot green"></div><div class="micro-dot green"></div><div class="micro-dot green"></div>';
        }

        cell.appendChild(dots);

        cell.addEventListener('click', () => {
            selectedDay = day;
            document.querySelectorAll('.cal-cell').forEach(c => c.classList.remove('selected'));
            cell.classList.add('selected');
            updateTimelineDateLabel();
            showToast(`📅 Selected: ${monthNames[currentMonth]} ${day}, ${currentYear}`);
        });

        container.appendChild(cell);
    }
}

function updateTimelineDateLabel() {
    const d = new Date(currentYear, currentMonth, selectedDay);
    const dayOfWeek = dayNames[d.getDay()];
    const shortMonth = monthNames[currentMonth].substring(0, 3);
    const label = document.getElementById('timeline-date-label');
    if (label) {
        label.textContent = `${dayOfWeek}, ${shortMonth} ${selectedDay}, ${currentYear}`;
    }
}

window.markDoseTaken = function(cardId, medName) {
    const card = document.getElementById(`dose-card-${cardId}`);
    if (!card) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    card.classList.remove('pending-focus');
    card.classList.add('taken-verified');

    const headerBadge = card.querySelector('.dose-status-badge');
    if (headerBadge) {
        headerBadge.className = 'dose-status-badge verified';
        headerBadge.textContent = 'Taken (Locked)';
    }

    const btn = card.querySelector('.mark-taken-btn');
    if (btn) {
        const verifiedDiv = document.createElement('div');
        verifiedDiv.className = 'dose-verified-msg';
        verifiedDiv.innerHTML = `<span>✓</span> <span>Taken at ${timeStr}<br>(Verified by Caregiver)</span>`;
        btn.replaceWith(verifiedDiv);
    }

    if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100]);
    }

    showToast(`✓ ${medName} marked as taken!`);
};

function showToast(message) {
    let toast = document.getElementById('toast-msg');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast-msg';
        toast.className = 'toast-msg';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2800);
}

document.addEventListener('DOMContentLoaded', initSchedulePage);
