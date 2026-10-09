const STORAGE_KEY = 'medmate-user-profile';

function initProfilePage() {
    loadProfileData();
    setupProfileForm();
}

function loadProfileData() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return;

    try {
        const data = JSON.parse(saved);
        if (data.name) {
            document.getElementById('profile-name').value = data.name;
            const topName = document.getElementById('patient-name-top');
            const displayName = document.getElementById('display-profile-name');
            if (topName) topName.textContent = data.name;
            if (displayName) displayName.textContent = data.name;
        }
        if (data.age) document.getElementById('profile-age').value = data.age;
        if (data.emergencyName) document.getElementById('emergency-name').value = data.emergencyName;
        if (data.emergencyPhone) document.getElementById('emergency-phone').value = data.emergencyPhone;
        if (data.doctorName) document.getElementById('doctor-name').value = data.doctorName;
        if (data.prefLanguage) document.getElementById('pref-language').value = data.prefLanguage;
    } catch (e) {
        console.error('Error parsing profile data', e);
    }
}

function setupProfileForm() {
    const form = document.getElementById('profile-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const profileData = {
            name: document.getElementById('profile-name').value.trim(),
            age: document.getElementById('profile-age').value,
            emergencyName: document.getElementById('emergency-name').value.trim(),
            emergencyPhone: document.getElementById('emergency-phone').value.trim(),
            doctorName: document.getElementById('doctor-name').value.trim(),
            prefLanguage: document.getElementById('pref-language').value,
            updatedAt: new Date().toISOString()
        };

        localStorage.setItem(STORAGE_KEY, JSON.stringify(profileData));

        const topName = document.getElementById('patient-name-top');
        const displayName = document.getElementById('display-profile-name');
        if (topName) topName.textContent = profileData.name;
        if (displayName) displayName.textContent = profileData.name;

        showToast('✓ Profile & Preferences saved successfully!');
    });
}

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
    }, 3000);
}

document.addEventListener('DOMContentLoaded', initProfilePage);
