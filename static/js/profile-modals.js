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
    document.querySelectorAll('.modal-overlay, .modal-backdrop').forEach((overlay) => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          this.closeAllModals();
        }
      });
    });
  }

  // Modal para criar projeto (delegado)
  openProjetModal() {
    if (typeof openCreateProjectModal === 'function') {
      openCreateProjectModal();
    } else if (typeof window.createProject === 'function') {
      window.createProject();
    } else {
      console.warn('Função de abertura do modal de projeto não encontrada');
    }
  }

  // Modal para editar projeto (delegado)
  async openEditProjetModal(projetId) {
    if (typeof editProject === 'function') {
      editProject(projetId);
    } else {
      console.warn('Função editProject não encontrada');
    }
  }

  // Modal para visualizar projeto (delegado)
  async openViewProjetModal(projetId) {
    if (typeof viewProject === 'function') {
      viewProject(projetId);
    } else {
      console.warn('Função viewProject não encontrada');
    }
  }

  // Modal para deletar projeto (delegado)
  openDeleteProjetModal(projetId, projectTitle = '') {
    if (typeof confirmDelete === 'function') {
      confirmDelete(projetId, projectTitle);
    } else if (typeof deleteProject === 'function') {
      deleteProject(projetId);
    } else {
      console.warn('Função deleteProject/confirmDelete não encontrada');
    }
  }

  closeAllModals() {
    // Esconde modais conhecidos do contexto de projetos
    const ids = ['projectModal', 'viewProjectModal', 'delete-projet-modal'];
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el && !el.classList.contains('hidden')) el.classList.add('hidden');
    });
    document.body.style.overflow = 'auto';
  }

  showNotification(message, type = 'info') {
    // Implementar sistema de notificações ou usar console como fallback
    console.log(`${type.toUpperCase()}: ${message}`);
  }

  showFormErrors(errors) {
    // Limpar erros anteriores
    document.querySelectorAll('.form-error').forEach((error) => {
      error.remove();
    });

    // Mostrar novos erros (espera { field: [msgs] })
    for (const [field, messages] of Object.entries(errors || {})) {
      const fieldElement = document.getElementById(`id_${field}`) || document.getElementById(field);
      if (fieldElement) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error text-red-500 text-sm mt-1';
        errorDiv.textContent = Array.isArray(messages) ? messages.join(', ') : String(messages);
        fieldElement.parentNode.appendChild(errorDiv);
      }
    }
  }

  getCSRFToken() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  window.profileModals = new ProfileModals();
});
