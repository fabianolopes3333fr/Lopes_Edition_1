class ProfileModals {
  constructor() {
    this.init();
  }

  init() {
    this.bindModalEvents();
  }

  bindModalEvents() {
    // Fechar modais
    document.querySelectorAll('.modal-close').forEach((btn) => {
      btn.addEventListener('click', () => {
        this.closeAllModals();
      });
    });

    // Fechar modal clicando fora
    document.querySelectorAll('.modal-overlay').forEach((overlay) => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          this.closeAllModals();
        }
      });
    });
  }

  // Modal para criar projeto
  openProjetModal() {
    const modal = document.getElementById('projet-modal');
    const form = document.getElementById('projet-form');

    // Limpar formulário
    form.reset();
    form.dataset.mode = 'create';

    // Mostrar modal
    modal.classList.remove('hidden');

    // Bind do formulário
    this.bindProjetForm();
  }

  // Modal para editar projeto
  async openEditProjetModal(projetId) {
    try {
      const response = await fetch(`/accounts/api/projet/${projetId}/edit/`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCSRFToken(),
        },
      });

      if (response.ok) {
        const data = await response.json();
        const modal = document.getElementById('projet-modal');
        const form = document.getElementById('projet-form');

        // Preencher formulário
        form.dataset.mode = 'edit';
        form.dataset.projetId = projetId;

        document.getElementById('id_title').value = data.projet.title;
        document.getElementById('id_description').value = data.projet.description;
        document.getElementById('id_statut').value = data.projet.statut;
        document.getElementById('id_budget_estime').value = data.projet.budget_estime;
        document.getElementById('id_adresse').value = data.projet.adresse;
        document.getElementById('id_ville').value = data.projet.ville;

        // Mostrar modal
        modal.classList.remove('hidden');

        // Bind do formulário
        this.bindProjetForm();
      }
    } catch (error) {
      console.error('Erro ao carregar projeto:', error);
    }
  }

  // Modal para visualizar projeto
  async openViewProjetModal(projetId) {
    try {
      const response = await fetch(`/accounts/api/projet/${projetId}/view/`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCSRFToken(),
        },
      });

      if (response.ok) {
        const data = await response.json();
        const modal = document.getElementById('view-projet-modal');

        // Preencher dados
        document.getElementById('view-projet-title').textContent = data.projet.title;
        document.getElementById('view-projet-description').textContent = data.projet.description;
        document.getElementById('view-projet-statut').textContent = data.projet.statut;
        document.getElementById('view-projet-budget').textContent = `${data.projet.budget_estime}€`;
        document.getElementById('view-projet-adresse').textContent = data.projet.adresse;
        document.getElementById('view-projet-ville').textContent = data.projet.ville;
        document.getElementById('view-projet-created').textContent = data.projet.date_creation;

        // Mostrar modal
        modal.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Erro ao visualizar projeto:', error);
    }
  }

  // Modal para deletar projeto
  openDeleteProjetModal(projetId) {
    const modal = document.getElementById('delete-projet-modal');
    const confirmBtn = document.getElementById('confirm-delete-btn');

    // Configurar botão de confirmação
    confirmBtn.onclick = () => this.deleteProjet(projetId);

    // Mostrar modal
    modal.classList.remove('hidden');
  }

  // Modal para visualizar devis
  async openViewDevisModal(devisId) {
    try {
      const response = await fetch(`/accounts/api/devis/${devisId}/view/`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': this.getCSRFToken(),
        },
      });

      if (response.ok) {
        const data = await response.json();
        const modal = document.getElementById('view-devis-modal');

        // Preencher dados
        document.getElementById('view-devis-numero').textContent = data.devis.numero;
        document.getElementById('view-devis-titre').textContent = data.devis.titre;
        document.getElementById('view-devis-status').textContent = data.devis.status;
        document.getElementById('view-devis-total').textContent = `${data.devis.total}€`;
        document.getElementById('view-devis-created').textContent = data.devis.date_creation;
        document.getElementById('view-devis-expiration').textContent = data.devis.date_expiration;

        // Configurar link público
        const publicLink = document.getElementById('view-devis-link');
        publicLink.href = data.devis.url_publica;

        // Mostrar modal
        modal.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Erro ao visualizar devis:', error);
    }
  }

  bindProjetForm() {
    const form = document.getElementById('projet-form');

    form.onsubmit = async (e) => {
      e.preventDefault();

      const formData = new FormData(form);
      const mode = form.dataset.mode;
      const projetId = form.dataset.projetId;

      let url = '/accounts/api/projet/create/';
      if (mode === 'edit') {
        url = `/accounts/api/projet/${projetId}/edit/`;
      }

      try {
        const response = await fetch(url, {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': this.getCSRFToken(),
          },
        });

        const data = await response.json();

        if (data.success) {
          this.showNotification(data.message, 'success');
          this.closeAllModals();

          // Recarregar seção atual
          window.profileNavigation.loadSection(window.profileNavigation.currentSection);
        } else {
          this.showFormErrors(data.errors);
        }
      } catch (error) {
        console.error('Erro ao salvar projeto:', error);
        this.showNotification('Erro ao salvar projeto', 'error');
      }
    };
  }

  async deleteProjet(projetId) {
    try {
      const response = await fetch(`/accounts/api/projet/${projetId}/delete/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': this.getCSRFToken(),
        },
      });

      const data = await response.json();

      if (data.success) {
        this.showNotification(data.message, 'success');
        this.closeAllModals();

        // Recarregar seção atual
        window.profileNavigation.loadSection(window.profileNavigation.currentSection);
      } else {
        this.showNotification('Erro ao deletar projeto', 'error');
      }
    } catch (error) {
      console.error('Erro ao deletar projeto:', error);
      this.showNotification('Erro ao deletar projeto', 'error');
    }
  }

  closeAllModals() {
    document.querySelectorAll('.modal').forEach((modal) => {
      modal.classList.add('hidden');
    });
  }

  showNotification(message, type = 'info') {
    // Implementar sistema de notificações
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
      type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    } text-white`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  showFormErrors(errors) {
    // Limpar erros anteriores
    document.querySelectorAll('.form-error').forEach((error) => {
      error.remove();
    });

    // Mostrar novos erros
    for (const [field, messages] of Object.entries(errors)) {
      const fieldElement = document.getElementById(`id_${field}`);
      if (fieldElement) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error text-red-500 text-sm mt-1';
        errorDiv.textContent = messages.join(', ');
        fieldElement.parentNode.appendChild(errorDiv);
      }
    }
  }

  getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  window.profileModals = new ProfileModals();
});
