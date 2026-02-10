document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication using the central Auth module
    if (!Auth.requireAuth()) {
        return;
    }

    // DOM Elements
    const usernameInput = document.getElementById('username');
    const fullNameInput = document.getElementById('fullName');
    const avatarImage = document.getElementById('avatarImage');
    const avatarInput = document.getElementById('avatarInput');
    const uploadAvatarBtn = document.getElementById('uploadAvatarBtn');
    const profileForm = document.getElementById('profileForm');
    const passwordForm = document.getElementById('passwordForm');

    // Toast function
    const showToast = (message, isError = false) => {
        const toastEl = document.getElementById('liveToast');
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');
        
        toastTitle.textContent = isError ? 'Hata' : 'Başarılı';
        toastTitle.className = isError ? 'me-auto text-danger' : 'me-auto text-success';
        toastMessage.textContent = message;
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    };

    // Load User Data
    try {
        const response = await fetch('/auth/me', { 
            headers: Auth.getHeaders()
        });
        
        if (response.status === 401) {
            Auth.handleUnauthorized();
            return;
        }

        if (!response.ok) throw new Error('Kullanıcı bilgileri alınamadı');
        
        const user = await response.json();
        usernameInput.value = user.username;
        fullNameInput.value = user.full_name || '';
        if (user.avatar_url) {
            // Force cache refresh
            avatarImage.src = user.avatar_url + '?t=' + new Date().getTime();
        }

    } catch (error) {
        console.error(error);
        showToast('Kullanıcı bilgileri yüklenirken hata oluştu', true);
    }

    // Update Profile Info
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            const response = await fetch('/auth/me', {
                method: 'PUT',
                headers: Auth.getHeaders(),
                body: JSON.stringify({
                    full_name: fullNameInput.value
                })
            });

            if (response.status === 401) {
                Auth.handleUnauthorized();
                return;
            }

            if (!response.ok) throw new Error('Güncelleme başarısız');
            
            showToast('Profil bilgileri güncellendi');
        } catch (error) {
            console.error(error);
            showToast('Güncelleme sırasında hata oluştu', true);
        }
    });

    // Avatar Selection & Preview
    avatarInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                avatarImage.src = e.target.result;
            };
            reader.readAsDataURL(file);
            uploadAvatarBtn.disabled = false;
        }
    });

    // Upload Avatar
    uploadAvatarBtn.addEventListener('click', async () => {
        const file = avatarInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const headers = Auth.getHeaders();
            delete headers['Content-Type']; // Let browser set Content-Type with boundary for FormData

            const response = await fetch('/auth/me/avatar', {
                method: 'POST',
                headers: headers,
                body: formData
            });

            if (response.status === 401) {
                Auth.handleUnauthorized();
                return;
            }

            if (!response.ok) throw new Error('Fotoğraf yüklenemedi');

            const updatedUser = await response.json();
            // Force cache refresh
            avatarImage.src = updatedUser.avatar_url + '?t=' + new Date().getTime();
            showToast('Profil fotoğrafı güncellendi');
            uploadAvatarBtn.disabled = true;
            avatarInput.value = '';
        } catch (error) {
            console.error(error);
            showToast('Fotoğraf yüklenirken hata oluştu', true);
        }
    });

    // Change Password
    passwordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (newPassword !== confirmPassword) {
            showToast('Yeni şifreler eşleşmiyor', true);
            return;
        }

        try {
            const response = await fetch('/auth/me/password', {
                method: 'POST',
                headers: Auth.getHeaders(),
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (response.status === 401) {
                Auth.handleUnauthorized();
                return;
            }

            if (!response.ok) {
                throw new Error(data.detail || 'Şifre değiştirilemedi');
            }

            showToast('Şifre başarıyla değiştirildi');
            passwordForm.reset();
        } catch (error) {
            console.error(error);
            showToast(error.message, true);
        }
    });
});
