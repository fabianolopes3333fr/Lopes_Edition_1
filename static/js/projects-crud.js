let currentProjectId = null;

// Criar projeto
function openCreateProjectModal() {
    document.getElementById('modal-title').textContent = 'Nouveau Projet';
    document.getElementById('project-id').value = '';
    document.getElementById('projectForm').reset();
    document.getElementById('projectModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// Editar projeto
function editProject(projectId) {
    currentProjectId = projectId;

    fetch(`/accounts/projects/${projectId}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            populateProjectForm(data.project);
            document.getElementById('modal-title').textContent = 'Modifier Projet';
            document.getElementById('projectModal').classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
    })
    .catch(error => {
        console.error('Erro ao carregar projeto:', error);
        showNotification('Erreur lors du chargement du projet', 'error');
    });
}

// Visualizar projeto
function viewProject(projectId) {
    fetch(`/accounts/projects/${projectId}/view/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayProjectDetails(data.project);
                        document.getElementById('viewProjectModal').classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
    })
    .catch(error => {
        console.error('Erro ao visualizar projeto:', error);
        showNotification('Erreur lors du chargement des détails', 'error');
    });
}

// Deletar projeto
function deleteProject(projectId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce projet ?')) {
        fetch(`/accounts/projects/${projectId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCsrfToken(),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Projet supprimé avec succès', 'success');
                loadSectionContent('mes-projets');
            } else {
                showNotification(data.message || 'Erreur lors de la suppression', 'error');
            }
        })
        .catch(error => {
            console.error('Erro ao deletar projeto:', error);
            showNotification('Erreur lors de la suppression', 'error');
        });
    }
}

// Submeter formulário
document.getElementById('projectForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const projectId = document.getElementById('project-id').value;
    const url = projectId ? `/accounts/projects/${projectId}/update/` : '/accounts/projects/create/';
    const method = projectId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message || 'Projet enregistré avec succès', 'success');
            closeProjectModal();
            loadSectionContent('mes-projets');
        } else {
            showNotification(data.message || 'Erreur lors de l\'enregistrement', 'error');
        }
    })
    .catch(error => {
        console.error('Erro ao salvar projeto:', error);
        showNotification('Erreur lors de l\'enregistrement', 'error');
    });
});

// Fechar modais
function closeProjectModal() {
    document.getElementById('projectModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
    currentProjectId = null;
}

function closeViewProjectModal() {
    document.getElementById('viewProjectModal').classList.add('hidden');
    document.body.style.overflow = 'auto';
}

// Editar a partir da visualização
function editProjectFromView() {
    closeViewProjectModal();
    if (currentProjectId) {
        editProject(currentProjectId);
    }
}

// Preencher formulário com dados do projeto
function populateProjectForm(project) {
    document.getElementById('project-id').value = project.id;
    document.getElementById('titre').value = project.titre || '';
    document.getElementById('description').value = project.description || '';
    document.getElementById('type_service').value = project.type_service || '';
    document.getElementById('statut').value = project.statut || '';
    document.getElementById('budget_estime').value = project.budget_estime || '';
    document.getElementById('date_souhaite').value = project.date_souhaite || '';
    document.getElementById('adresse').value = project.adresse || '';
}

// Exibir detalhes do projeto
function displayProjectDetails(project) {
    currentProjectId = project.id;
    document.getElementById('view-project-title').textContent = project.titre;

    const detailsHtml = `
        <div class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Informations générales</h4>
                    <div class="space-y-2 text-sm">
                        <div><span class="font-medium">Type:</span> ${project.type_service_display || 'Non spécifié'}</div>
                        <div><span class="font-medium">Statut:</span> 
                            <span class="status-badge status-${project.statut}">${project.statut_display}</span>
                        </div>
                        <div><span class="font-medium">Date de création:</span> ${formatDate(project.date_creation)}</div>
                        ${project.date_souhaite ? `<div><span class="font-medium">Date souhaitée:</span> ${formatDate(project.date_souhaite)}</div>` : ''}
                    </div>
                </div>
                
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Détails financiers</h4>
                    <div class="space-y-2 text-sm">
                        ${project.budget_estime ? `<div><span class="font-medium">Budget estimé:</span> ${project.budget_estime} €</div>` : '<div class="text-gray-500">Budget non spécifié</div>'}
                    </div>
                </div>
            </div>
            
            ${project.description ? `
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Description</h4>
                    <p class="text-gray-700 text-sm leading-relaxed">${project.description}</p>
                </div>
            ` : ''}
            
            ${project.adresse ? `
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Adresse du projet</h4>
                    <p class="text-gray-700 text-sm">${project.adresse}</p>
                </div>
            ` : ''}
        </div>
    `;

    document.getElementById('project-details').innerHTML = detailsHtml;
}

// Filtros e busca
document.getElementById('search-projects').addEventListener('input', function() {
    filterProjects();
});

document.getElementById('filter-status').addEventListener('change', function() {
    filterProjects();
});

function filterProjects() {
    const searchTerm = document.getElementById('search-projects').value.toLowerCase();
    const statusFilter = document.getElementById('filter-status').value;
    const projectCards = document.querySelectorAll('.project-card');

    projectCards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        const description = card.querySelector('p').textContent.toLowerCase();
        const status = card.querySelector('.status-badge').classList.toString();

        const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
        const matchesStatus = !statusFilter || status.includes(`status-${statusFilter}`);

        if (matchesSearch && matchesStatus) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function resetFilters() {
    document.getElementById('search-projects').value = '';
    document.getElementById('filter-status').value = '';
    filterProjects();
}

// Utilitários
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

function showNotification(message, type = 'info') {
    // Implementar sistema de notificações
    console.log(`${type.toUpperCase()}: ${message}`);
}

function displayProjectDetails(project) {
    const detailsContainer = document.getElementById('project-details');
    const title = document.getElementById('view-project-title');

    title.textContent = project.titre;

    const statusColors = {
        'en_attente': 'bg-yellow-100 text-yellow-800',
        'en_cours': 'bg-blue-100 text-blue-800',
        'termine': 'bg-green-100 text-green-800',
        'annule': 'bg-red-100 text-red-800'
    };

    const statusColor = statusColors[project.statut] || 'bg-gray-100 text-gray-800';

    detailsContainer.innerHTML = `
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Informações Principais -->
            <div class="space-y-4">
                <div>
                    <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Informations générales</h4>
                    <div class="mt-2 space-y-3">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Statut:</span>
                            <span class="px-2 py-1 text-xs font-medium rounded-full ${statusColor}">
                                ${project.statut_display || project.statut}
                            </span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">Type de service:</span>
                            <span class="font-medium">${project.type_service_display || project.type_service}</span>
                        </div>
                        ${project.budget_estime ? `
                        <div class="flex justify-between">
                            <span class="text-gray-600">Budget estimé:</span>
                            <span class="font-medium">${formatCurrency(project.budget_estime)}</span>
                        </div>
                        ` : ''}
                        <div class="flex justify-between">
                            <span class="text-gray-600">Date de création:</span>
                            <span class="font-medium">${formatDate(project.date_creation)}</span>
                        </div>
                        ${project.date_souhaite ? `
                        <div class="flex justify-between">
                            <span class="text-gray-600">Date souhaitée:</span>
                            <span class="font-medium">${formatDate(project.date_souhaite)}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                ${project.adresse ? `
                <div>
                    <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Localisation</h4>
                    <div class="mt-2">
                        <div class="flex items-start">
                            <i class="fas fa-map-marker-alt text-gray-400 mt-1 mr-2"></i>
                            <span class="text-gray-900">${project.adresse}</span>
                        </div>
                    </div>
                </div>
                ` : ''}
            </div>
            
            <!-- Descrição -->
            <div>
                <h4 class="text-sm font-medium text-gray-500 uppercase tracking-wide">Description du projet</h4>
                <div class="mt-2">
                    <div class="bg-gray-50 rounded-lg p-4">
                        <p class="text-gray-900 whitespace-pre-wrap">${project.description || 'Aucune description fournie.'}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Actions rapides -->
        <div class="mt-6 pt-6 border-t border-gray-200">
            <div class="flex flex-wrap gap-3">
                <button onclick="editProjectFromView()" class="btn-primary">
                    <i class="fas fa-edit mr-2"></i>
                    Modifier
                </button>
                <button onclick="generateQuote(${project.id})" class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors duration-200 font-medium">
                    <i class="fas fa-file-invoice-dollar mr-2"></i>
                    Demander un devis
                </button>
                <button onclick="deleteProject(${project.id})" class="btn-danger">
                    <i class="fas fa-trash mr-2"></i>
                    Supprimer
                </button>
            </div>
        </div>
    `;
}

// Funções auxiliares para formatação
function formatCurrency(amount) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

// Função para gerar orçamento (placeholder)
function generateQuote(projectId) {
    showNotification('Redirection vers la demande de devis...', 'info');
    // Implementar redirecionamento para página de orçamento
    // window.location.href = `/orcamentos/solicitar/${projectId}/`;
}

// Função para validar formulário
function validateProjectForm() {
    const titre = document.getElementById('titre').value.trim();
    const typeService = document.getElementById('type_service').value;

    if (!titre) {
        showNotification('Le titre du projet est obligatoire', 'error');
        document.getElementById('titre').focus();
        return false;
    }

    if (!typeService) {
        showNotification('Le type de service est obligatoire', 'error');
        document.getElementById('type_service').focus();
        return false;
    }

    return true;
}

// Atualizar o event listener do formulário para incluir validação
document.getElementById('projectForm').addEventListener('submit', function(e) {
    e.preventDefault();

    if (!validateProjectForm()) {
        return;
    }

    const formData = new FormData(this);
    const projectId = document.getElementById('project-id').value;
    const url = projectId ? `/accounts/projects/${projectId}/update/` : '/accounts/projects/create/';
    const method = projectId ? 'PUT' : 'POST';

    // Mostrar loading
    const submitBtn = this.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Enregistrement...';
    submitBtn.disabled = true;

    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message || 'Projet enregistré avec succès', 'success');
            closeProjectModal();
            loadSectionContent('mes-projets');
        } else {
            showNotification(data.message || 'Erreur lors de l\'enregistrement', 'error');
        }
    })
    .catch(error => {
        console.error('Erro ao salvar projeto:', error);
        showNotification('Erreur lors de l\'enregistrement', 'error');
    })
    .finally(() => {
        // Restaurar botão
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
});

// Função para limpar formulário
function clearProjectForm() {
    document.getElementById('projectForm').reset();
    document.getElementById('project-id').value = '';
    document.getElementById('modal-title').textContent = 'Nouveau Projet';
}

// Event listeners para fechar modais com ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        if (!document.getElementById('projectModal').classList.contains('hidden')) {
            closeProjectModal();
        }
        if (!document.getElementById('viewProjectModal').classList.contains('hidden')) {
            closeViewProjectModal();
        }
    }
});

// Função para confirmar exclusão com modal personalizado
function confirmDelete(projectId, projectTitle) {
    const confirmed = confirm(`Êtes-vous sûr de vouloir supprimer le projet "${projectTitle}" ?\n\nCette action est irréversible.`);
    if (confirmed) {
        deleteProject(projectId);
    }
}