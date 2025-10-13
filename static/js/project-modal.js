// Adicione esta função de debug no início do arquivo
function debugModal() {
  console.log('=== DEBUG MODAL ===');

  const modal = document.getElementById('projectModal');
  console.log('Modal encontrado:', modal);

  const form = document.getElementById('projectForm');
  console.log('Form encontrado:', form);

  const modalTitle = document.getElementById('modal-title');
  console.log('Modal title encontrado:', modalTitle);

  const submitText = document.getElementById('submit-text');
  console.log('Submit text encontrado:', submitText);

  const projectId = document.getElementById('project-id');
  console.log('Project ID input encontrado:', projectId);

  console.log('==================');
}

// Helpers de mapeamento
function buildProjectPayloadFromForm(formEl) {
  const fd = new FormData(formEl);
  return {
    titre: fd.get('titre') || '',
    description: fd.get('description') || '',
    type_projet: fd.get('type_projet') || fd.get('type_service') || '',
    adresse: fd.get('adresse') || '',
    ville: fd.get('ville') || '',
    prix_estime: (fd.get('prix_estime') || fd.get('budget_estime')) ? parseFloat(fd.get('prix_estime') || fd.get('budget_estime')) : null,
    date_debut: fd.get('date_debut') || fd.get('date_souhaite') || fd.get('date_souhaitee') || undefined,
  };
}

// Função para criar novo projeto (abrir modal)
// Modifique a função createProject para incluir debug
function createProject() {
  console.log('createProject() chamada');
  debugModal();

  // Resetar o formulário
  resetProjectForm();

  // Configurar modal para criação
  const modalTitle = document.getElementById('modal-title');
  const submitText = document.getElementById('submit-text');
  const projectIdInput = document.getElementById('project-id');

  if (modalTitle) {
    modalTitle.textContent = 'Nouveau Projet';
    console.log('Título configurado');
  } else {
    console.error('Elemento modal-title não encontrado!');
  }

  if (submitText) {
    submitText.textContent = 'Créer le projet';
    console.log('Texto do botão configurado');
  } else {
    console.error('Elemento submit-text não encontrado!');
  }

  if (projectIdInput) {
    projectIdInput.value = '';
    console.log('Project ID limpo');
  } else {
    console.error('Elemento project-id não encontrado!');
  }

  // Mostrar o modal
  showProjectModal();
}

// Função para mostrar o modal
function showProjectModal() {
  console.log('showProjectModal() chamada');

  const modal = document.getElementById('projectModal');

  if (!modal) {
    console.error('ERRO: Modal projectModal não encontrado no DOM!');
    console.log(
      'Elementos disponíveis com ID:',
      Array.from(document.querySelectorAll('[id]')).map((el) => el.id)
    );
    return;
  }

  console.log('Modal encontrado, removendo classe hidden...');
  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';

  // Verificar se o modal está visível
  setTimeout(() => {
    const isVisible = !modal.classList.contains('hidden');
    console.log('Modal visível após timeout:', isVisible);
    console.log('Classes do modal:', modal.className);
  }, 100);

  // Focar no primeiro campo
  setTimeout(() => {
    const firstInput = document.getElementById('titre');
    if (firstInput) {
      firstInput.focus();
      console.log('Foco definido no primeiro input');
    } else {
      console.error('Input titre não encontrado');
    }
  }, 100);
}

// Função para fechar o modal
function closeProjectModal() {
  const modal = document.getElementById('projectModal');
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto'; // Restaurar scroll da página
    resetProjectForm();
  }
}

// Função para resetar o formulário
function resetProjectForm() {
  const form = document.getElementById('projectForm');
  if (form) {
    form.reset();

    // Limpar mensagens de erro
    const errorMessages = form.querySelectorAll('.error-message');
    errorMessages.forEach((error) => {
      error.classList.add('hidden');
      error.textContent = '';
    });

    // Resetar estado do botão de submit
    const submitBtn = document.getElementById('submit-btn');
    const submitText = document.getElementById('submit-text');
    const submitLoading = document.getElementById('submit-loading');

    if (submitBtn && submitText && submitLoading) {
      submitBtn.disabled = false;
      submitText.classList.remove('hidden');
      submitLoading.classList.add('hidden');
    }
  }
}

// Função para editar projeto existente
function editProject(projectId) {
  // Fazer requisição para buscar dados do projeto
  fetch(`/projects/${projectId}/`)
    .then((response) => response.json())
    .then((project) => {
      if (project && project.id) {
        populateProjectForm(project);

        // Configurar modal para edição
        document.getElementById('modal-title').textContent = 'Modifier le Projet';
        document.getElementById('submit-text').textContent = 'Mettre à jour';
        document.getElementById('project-id').value = projectId;

        showProjectModal();
      } else {
        showNotification('Erreur lors du chargement du projet', 'error');
      }
    })
    .catch((error) => {
      console.error('Erreur:', error);
      showNotification('Erreur lors du chargement du projet', 'error');
    });
}

// Função para popular o formulário com dados existentes
function populateProjectForm(project) {
  document.getElementById('titre').value = project.titre || '';
  (document.getElementById('type_projet') || document.getElementById('type_service')).value = project.type_projet || '';
  document.getElementById('description').value = project.description || '';
  document.getElementById('budget_estime').value = project.prix_estime ?? '';
  (document.getElementById('date_souhaite') || document.getElementById('date_souhaitee')).value = project.date_debut || '';
  document.getElementById('adresse').value = project.adresse || '';
  if (document.getElementById('ville')) document.getElementById('ville').value = project.ville || '';
  if (document.getElementById('code_postal')) document.getElementById('code_postal').value = '';
  if (document.getElementById('surface')) document.getElementById('surface').value = '';
  if (document.getElementById('urgent')) document.getElementById('urgent').checked = false;
}

// Fechar modal ao clicar fora dele
document.addEventListener('click', function (event) {
  const modal = document.getElementById('projectModal');
  const modalContent = modal?.querySelector('.relative');

  if (
    modal &&
    !modal.classList.contains('hidden') &&
    event.target === modal &&
    !modalContent?.contains(event.target)
  ) {
    closeProjectModal();
  }
});

// Fechar modal com tecla ESC
document.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
    const modal = document.getElementById('projectModal');
    if (modal && !modal.classList.contains('hidden')) {
      closeProjectModal();
    }
  }
});

// Função para submeter o formulário
document.getElementById('projectForm').addEventListener('submit', function (e) {
  e.preventDefault();

  // Mostrar loading no botão
  const submitBtn = document.getElementById('submit-btn');
  const submitText = document.getElementById('submit-text');
  const submitLoading = document.getElementById('submit-loading');

  if (submitText && submitLoading && submitBtn) {
    submitText.classList.add('hidden');
    submitLoading.classList.remove('hidden');
    submitBtn.disabled = true;
  }

  const projectId = document.getElementById('project-id').value;
  const url = projectId ? `/projects/${projectId}/` : '/projects/';
  const method = projectId ? 'PATCH' : 'POST';
  const payload = buildProjectPayloadFromForm(this);

  fetch(url, {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
    },
    body: JSON.stringify(payload),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data && data.id) {
        showNotification(
          projectId ? 'Projet mis à jour avec succès!' : 'Projet criado com sucesso!',
          'success'
        );
        closeProjectModal();
        setTimeout(() => {
          window.location.reload();
        }, 800);
      } else {
        showFormErrors(data.errors || {});
      }
    })
    .catch((error) => {
      console.error('Erreur:', error);
      showNotification('Erreur lors de la sauvegarde', 'error');
    })
    .finally(() => {
      if (submitText && submitLoading && submitBtn) {
        submitText.classList.remove('hidden');
        submitLoading.classList.add('hidden');
        submitBtn.disabled = false;
      }
    });
});

// Função para mostrar erros do formulário
function showFormErrors(errors) {
  // Limpar erros anteriores
  const errorMessages = document.querySelectorAll('.error-message');
  errorMessages.forEach((error) => {
    error.classList.add('hidden');
    error.textContent = '';
  });

  // Mostrar novos erros
  Object.keys(errors).forEach((field) => {
    const errorElement = document.getElementById(`${field}-error`);
    if (errorElement) {
      errorElement.textContent = errors[field][0];
      errorElement.classList.remove('hidden');
    }
  });
}

// Função para mostrar notificações
function showNotification(message, type = 'info') {
  // Criar elemento de notificação
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;

  // Definir cores baseadas no tipo
  const colors = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    info: 'bg-blue-500 text-white',
    warning: 'bg-yellow-500 text-black',
  };

  notification.className += ` ${colors[type] || colors.info}`;
  notification.innerHTML = `
        <div class="flex items-center">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-lg">&times;</button>
        </div>
    `;

  document.body.appendChild(notification);

  // Animar entrada
  setTimeout(() => {
    notification.classList.remove('translate-x-full');
  }, 100);

  // Remover automaticamente após 5 segundos
  setTimeout(() => {
    notification.classList.add('translate-x-full');
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 5000);
}

// Função para visualizar projeto
function viewProject(projectId) {
  window.location.href = `/projects/projetos/${projectId}/`;
}

// Função para confirmar exclusão
function confirmDelete(projectId, projectTitle) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le projet "${projectTitle}" ?`)) {
    deleteProject(projectId);
  }
}

// Função para deletar projeto
function deleteProject(projectId) {
  fetch(`/projects/${projectId}/`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
    },
  })
    .then((response) => {
      if (response.status === 204 || response.status === 200) {
        showNotification('Projet supprimé avec succès!', 'success');
        const projectCard = document.querySelector(`[data-project-id="${projectId}"]`);
        if (projectCard) {
          projectCard.remove();
        }
      } else {
        showNotification('Erreur lors de la suppression', 'error');
      }
    })
    .catch((error) => {
      console.error('Erreur:', error);
      showNotification('Erreur lors de la suppression', 'error');
    });
}

// Validação em tempo real
document.addEventListener('DOMContentLoaded', function () {
  // Validação do código postal francês
  const codePostalInput = document.getElementById('code_postal');
  if (codePostalInput) {
    codePostalInput.addEventListener('input', function () {
      const value = this.value;
      const isValid = /^[0-9]{5}$/.test(value);

      if (value && !isValid) {
        this.setCustomValidity('Le code postal doit contenir 5 chiffres');
      } else {
        this.setCustomValidity('');
      }
    });
  }

  // Validação da data (não pode ser no passado)
  const dateInput = document.getElementById('date_souhaite');
  if (dateInput) {
    dateInput.addEventListener('change', function () {
      const selectedDate = new Date(this.value);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (selectedDate < today) {
        this.setCustomValidity('La date ne peut pas être dans le passé');
      } else {
        this.setCustomValidity('');
      }
    });
  }

  // Validação do orçamento
  const budgetInput = document.getElementById('budget_estime');
  if (budgetInput) {
    budgetInput.addEventListener('input', function () {
      const value = parseFloat(this.value);

      if (value && value < 0) {
        this.setCustomValidity('Le budget doit être positif');
      } else {
        this.setCustomValidity('');
      }
    });
  }
});
