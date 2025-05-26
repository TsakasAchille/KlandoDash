// Fonction pour afficher une notification
function showNotification(message, type = 'info') {
    // Utiliser uniquement notre conteneur de notifications dédié à l'admin
    const notifContainer = document.getElementById('admin-notification-container');
    if (!notifContainer) return; // Protection contre les erreurs
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    notifContainer.innerHTML = '';
    notifContainer.appendChild(alertDiv);
    
    // Auto-fermer après 5 secondes
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => notifContainer.innerHTML = '', 500);
    }, 5000);
}

// Fonction pour activer/désactiver un utilisateur
function toggleUserStatus(email) {
    // Désactiver le bouton pendant l'action
    const btn = document.getElementById(`toggle-${email}`);
    if (btn) btn.disabled = true;
    
    // Récupérer l'état actuel (actif/inactif)
    const isCurrentlyActive = btn.textContent.trim() === 'Désactiver';
    
    fetch('/api/admin/toggle-user-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            active: isCurrentlyActive
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Statut de l'utilisateur ${email} mis à jour avec succès.`, 'success');
            // Rafraichir la liste après 1 seconde
            setTimeout(() => {
                document.getElementById('refresh-users-btn').click();
            }, 1000);
        } else {
            showNotification(`Erreur: ${data.message}`, 'danger');
            if (btn) btn.disabled = false;
        }
    })
    .catch(error => {
        showNotification(`Erreur de connexion: ${error.message}`, 'danger');
        if (btn) btn.disabled = false;
    });
}

// Fonction pour changer le rôle d'un utilisateur
function changeUserRole(email) {
    // Ouvrir une boîte de dialogue pour sélectionner le nouveau rôle
    const newRole = prompt('Choisissez le nouveau rôle pour ' + email + ':\n- admin: Administrateur\n- user: Utilisateur standard\n- viewer: Utilisateur en lecture seule', 'user');
    
    if (!newRole) return; // Annulé par l'utilisateur
    
    // Désactiver le bouton pendant l'action
    const btn = document.getElementById(`role-${email}`);
    if (btn) btn.disabled = true;
    
    fetch('/api/admin/change-user-role', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email,
            role: newRole
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Rôle de l'utilisateur ${email} changé pour ${newRole}.`, 'success');
            // Rafraichir la liste après 1 seconde
            setTimeout(() => {
                document.getElementById('refresh-users-btn').click();
            }, 1000);
        } else {
            showNotification(`Erreur: ${data.message}`, 'danger');
            if (btn) btn.disabled = false;
        }
    })
    .catch(error => {
        showNotification(`Erreur de connexion: ${error.message}`, 'danger');
        if (btn) btn.disabled = false;
    });
}

// Fonction pour supprimer un utilisateur
function deleteUser(email) {
    // Demander confirmation avant suppression
    if (!confirm(`Êtes-vous sûr de vouloir supprimer l'utilisateur ${email} ? Cette action est irréversible.`)) {
        return; // L'utilisateur a annulé
    }
    
    // Désactiver le bouton pendant l'action
    const btn = document.getElementById(`delete-${email}`);
    if (btn) btn.disabled = true;
    
    fetch('/api/admin/delete-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`Utilisateur ${email} supprimé avec succès.`, 'success');
            // Rafraichir la liste après 1 seconde
            setTimeout(() => {
                document.getElementById('refresh-users-btn').click();
            }, 1000);
        } else {
            showNotification(`Erreur: ${data.message}`, 'danger');
            if (btn) btn.disabled = false;
        }
    })
    .catch(error => {
        showNotification(`Erreur de connexion: ${error.message}`, 'danger');
        if (btn) btn.disabled = false;
    });
}

// Fonction pour ajouter un nouvel utilisateur
function addUser() {
    const emailInput = document.getElementById('new-email');
    const roleInput = document.getElementById('new-role');
    const notesInput = document.getElementById('new-notes');
    const resultSpan = document.getElementById('add-user-result');
    
    // Vérification de base
    if (!emailInput.value) {
        resultSpan.innerHTML = '<span style="color: red;">Veuillez saisir un email valide</span>';
        return;
    }
    
    // Désactiver le bouton pendant l'action
    const btn = document.getElementById('add-user-btn');
    if (btn) btn.disabled = true;
    
    fetch('/api/admin/add-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: emailInput.value,
            role: roleInput.value,
            notes: notesInput.value || ''
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            resultSpan.innerHTML = `<span style="color: green;">${data.message}</span>`;
            emailInput.value = '';
            notesInput.value = '';
            roleInput.value = 'user';
            
            // Rafraichir la liste après 1 seconde
            setTimeout(() => {
                document.getElementById('refresh-users-btn').click();
            }, 1000);
        } else {
            resultSpan.innerHTML = `<span style="color: red;">${data.message}</span>`;
        }
        if (btn) btn.disabled = false;
    })
    .catch(error => {
        resultSpan.innerHTML = `<span style="color: red;">Erreur de connexion: ${error.message}</span>`;
        if (btn) btn.disabled = false;
    });
}

// Initialiser les événements au chargement du document
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le formulaire d'ajout d'utilisateur
    const addButton = document.getElementById('add-user-btn');
    if (addButton) {
        addButton.addEventListener('click', addUser);
    }
    
    // Initialiser le bouton de rafraîchissement
    const refreshButton = document.getElementById('refresh-users-btn');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            // Vous pouvez ajouter une animation de chargement ici si nécessaire
            // La page se rafraîchira automatiquement via le callback Dash
        });
    }
});
