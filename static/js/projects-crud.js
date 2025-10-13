let currentProjectId = null;
// Sinaliza que este módulo gerencia o submit do formulário de projetos
window.PROJECTS_CRUD_HANDLES_SUBMIT = true;

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

    fetch(`/projects/${projectId}/`, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(project => {
        applyProjetoToForm(project);
        document.getElementById('modal-title').textContent = 'Modifier Projet';
        document.getElementById('projectModal').classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    })
    .catch(error => {
        console.error('Erro ao carregar projeto:', error);
        showNotification('Erreur lors du chargement du projet', 'error');
    });
}

// Visualizar projeto
function viewProject(projectId) {
    fetch(`/projects/${projectId}/`, { headers: { 'X-Requested-With': 'XMLHttpRequest' }})
    .then(response => response.json())
    .then(project => {
        currentProjectId = project.id;
        const titleEl = document.getElementById('view-project-title');
        if (titleEl) titleEl.textContent = project.titre;
        const detailsHtml = `
            <div class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">Informations générales</h4>
                        <div class="space-y-2 text-sm">
                            <div><span class="font-medium">Type:</span> ${TYPE_LABELS[project.type_projet] || project.type_projet || '—'}</div>
                            <div><span class="font-medium">Statut:</span>
                                <span class="status-badge">${STATUS_LABELS[project.status] || project.status || '—'}</span>
                            </div>
                            <div><span class="font-medium">Date de création:</span> ${new Date(project.date_creation).toLocaleDateString('fr-FR')}</div>
                        </div>
                    </div>
                    <div>
                        <h4 class="font-semibold text-gray-900 mb-2">Détails financiers</h4>
                        <div class="space-y-2 text-sm">
                            ${project.prix_estime ? `<div><span class="font-medium">Budget estimé:</span> ${project.prix_estime} €</div>` : '<div class="text-gray-500">Budget non spécifié</div>'}
                        </div>
                    </div>
                </div>
                ${project.description ? `<div><h4 class="font-semibold text-gray-900 mb-2">Description</h4><p class="text-gray-700 text-sm leading-relaxed">${project.description}</p></div>` : ''}
                ${project.adresse ? `<div><h4 class="font-semibold text-gray-900 mb-2">Adresse du projet</h4><p class="text-gray-700 text-sm">${project.adresse}</p></div>` : ''}
            </div>`;
        const container = document.getElementById('project-details') || document.getElementById('projectDetails');
        if (container) container.innerHTML = detailsHtml;
        const modal = document.getElementById('viewProjectModal');
        if (modal) {
            modal.classList.remove('hidden');
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
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce projet ?')) return;
    fetch(`/projects/${projectId}/`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(resp => {
        if (resp.status === 204 || resp.status === 200) {
            showNotification('Projet supprimé avec succès', 'success');
            if (typeof loadSectionContent === 'function') loadSectionContent('mes-projets');
            else window.location.reload();
        } else {
            showNotification('Erreur lors de la suppression', 'error');
        }
    })
    .catch(error => {
        console.error('Erro ao deletar projeto:', error);
        showNotification('Erreur lors de la suppression', 'error');
    });
}

// Validação do formulário
function validateProjectForm() {
    const titreEl = document.getElementById('titre');
    const typeEl = document.getElementById('type_projet') || document.getElementById('type_service');
    const villeEl = document.getElementById('ville');

    if (!titreEl || !titreEl.value.trim()) {
        showNotification('Le titre du projet est obligatoire', 'error');
        if (titreEl) titreEl.focus();
        return false;
    }
    if (!typeEl || !typeEl.value) {
        showNotification('Le type de projet est obligatoire', 'error');
        if (typeEl) typeEl.focus();
        return false;
    }
    if (!villeEl || !villeEl.value.trim()) {
        showNotification('La ville est obligatoire', 'error');
        if (villeEl) villeEl.focus();
        return false;
    }
    return true;
}

// Submeter formulário (JSON)
document.getElementById('projectForm').addEventListener('submit', function(e) {
    e.preventDefault();

    if (!validateProjectForm()) return;

    const projectId = document.getElementById('project-id').value;
    const url = projectId ? `/projects/${projectId}/` : '/projects/';
    const method = projectId ? 'PATCH' : 'POST';
    const payload = buildProjetoPayloadFromForm(this);

    // Mostrar loading
    const submitBtn = this.querySelector('button[type="submit"]') || document.querySelector('.btn-primary[form="projectForm"]');
    const originalText = submitBtn ? submitBtn.innerHTML : '';
    if (submitBtn) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Enregistrement...';
        submitBtn.disabled = true;
    }

    fetch(url, {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data && (data.id || data.titre)) {
            showNotification('Projet enregistré avec succès', 'success');
            closeProjectModal();
            if (typeof loadSectionContent === 'function') loadSectionContent('mes-projets');
            else window.location.reload();
        } else {
            showNotification("Erreur lors de l'enregistrement", 'error');
        }
    })
    .catch(err => {
        console.error('Erro ao salvar projeto:', err);
        showNotification("Erreur lors de l'enregistrement", 'error');
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
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

// Preencher formulário com dados do projeto (alinhado ao serializer)
function populateProjectForm(project) {
    document.getElementById('project-id').value = project.id;
    document.getElementById('titre').value = project.titre || '';
    document.getElementById('description').value = project.description || '';
    const typeSelect = document.getElementById('type_projet') || document.getElementById('type_service');
    if (typeSelect) typeSelect.value = project.type_projet || '';
    const statusSelect = document.getElementById('status') || document.getElementById('statut');
    if (statusSelect) statusSelect.value = project.status || '';
    const budgetField = document.getElementById('budget_estime') || document.getElementById('prix_estime');
    if (budgetField) budgetField.value = project.prix_estime ?? '';
    const dateField = document.getElementById('date_debut') || document.getElementById('date_souhaite') || document.getElementById('date_souhaitee');
    if (dateField) dateField.value = project.date_debut || '';
    const villeField = document.getElementById('ville');
    if (villeField) villeField.value = project.ville || '';
    document.getElementById('adresse').value = project.adresse || '';
}

// Mapeamentos helper para campos UI <-> API
const STATUS_LABELS = {
    nouveau: 'Nouveau',
    en_cours: 'En cours',
    termine: 'Terminé',
    suspendu: 'Suspendu'
};
const TYPE_LABELS = {
    interieur: 'Peinture Intérieure',
    exterieur: 'Peinture Extérieure',
    renovation: 'Rénovation',
    decoration: 'Décoration'
};

function normalizeStatusFromUI(val) {
    // Converte valores herdados da UI para os válidos do modelo
    const map = {
        en_attente: 'nouveau',
        en_cours: 'en_cours',
        termine: 'termine',
        annule: 'suspendu',
        nouveau: 'nouveau',
        suspendu: 'suspendu'
    };
    return map[val] || 'nouveau';
}

function normalizeTypeFromUI(val) {
    // Mapeia 'autre' para uma opção válida
    const allowed = ['interieur', 'exterieur', 'renovation', 'decoration'];
    if (allowed.includes(val)) return val;
    if (val === 'autre' || !val) return 'decoration';
    return 'decoration';
}

function buildProjetoPayloadFromForm(formEl) {
    const fd = new FormData(formEl);
    const titre = fd.get('titre') || '';
    const description = fd.get('description') || '';
    const type_projet = normalizeTypeFromUI(fd.get('type_projet') || fd.get('type_service') || '');
    const status = normalizeStatusFromUI(fd.get('status') || fd.get('statut') || 'nouveau');
    const adresse = fd.get('adresse') || '';
    const ville = fd.get('ville') || '';
    const prix_estime_raw = fd.get('prix_estime') || fd.get('budget_estime') || '';
    const date_debut = fd.get('date_debut') || fd.get('date_souhaite') || fd.get('date_souhaitee') || '';

    // Parsing robusto para valores monetários: aceita vírgula decimal e remove separadores
    let prix_estime = null;
    if (prix_estime_raw) {
        const norm = String(prix_estime_raw)
            .replace(/\s/g, '')
            .replace(/\.(?=\d{3}(\D|$))/g, '')
            .replace(',', '.');
        const parsed = parseFloat(norm);
        prix_estime = isNaN(parsed) ? null : parsed;
    }

    const payload = {
        titre,
        description,
        type_projet: type_projet || null,
        status,
        adresse,
        ville,
        prix_estime,
    };
    if (date_debut) payload.date_debut = date_debut;
    return payload;
}

// Exibir detalhes do projeto
function displayProjectDetails(project) {
    currentProjectId = project.id;
    const titleEl = document.getElementById('view-project-title');
    if (titleEl) titleEl.textContent = project.titre;

    const detailsHtml = `
        <div class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Informations générales</h4>
                    <div class="space-y-2 text-sm">
                        <div><span class="font-medium">Type:</span> ${TYPE_LABELS[project.type_projet] || 'Non spécifié'}</div>
                        <div><span class="font-medium">Statut:</span>
                            <span class="status-badge status-${project.status}">${STATUS_LABELS[project.status] || project.status}</span>
                        </div>
                        <div><span class="font-medium">Date de création:</span> ${formatDate(project.date_creation)}</div>
                        ${project.date_debut ? `<div><span class="font-medium">Date de début:</span> ${formatDate(project.date_debut)}</div>` : ''}
                    </div>
                </div>
                
                <div>
                    <h4 class="font-semibold text-gray-900 mb-2">Détails financiers</h4>
                    <div class="space-y-2 text-sm">
                        ${project.prix_estime ? `<div><span class="font-medium">Budget estimé:</span> ${project.prix_estime} €</div>` : '<div class="text-gray-500">Budget non spécifié</div>'}
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

    const container = document.getElementById('project-details') || document.getElementById('projectDetails');
    if (container) container.innerHTML = detailsHtml;
}

// Filtros e busca
(function attachFilters() {
    const searchEl = document.getElementById('search-projects') || document.getElementById('searchProjects');
    const statusEl = document.getElementById('filter-status') || document.getElementById('statusFilter');
    if (searchEl) searchEl.addEventListener('input', filterProjects);
    if (statusEl) statusEl.addEventListener('change', filterProjects);
})();

function filterProjects() {
    const searchEl = document.getElementById('search-projects') || document.getElementById('searchProjects');
    const statusEl = document.getElementById('filter-status') || document.getElementById('statusFilter');
    const searchTerm = (searchEl && searchEl.value || '').toLowerCase();
    const statusFilter = statusEl ? statusEl.value : '';
    const projectCards = document.querySelectorAll('.project-card');

    projectCards.forEach(card => {
        const titleEl = card.querySelector('h3');
        const descEl = card.querySelector('p');
        const title = titleEl ? titleEl.textContent.toLowerCase() : '';
        const description = descEl ? descEl.textContent.toLowerCase() : '';
        const statusClass = (card.querySelector('.status-badge') || { classList: { toString: () => '' } }).classList.toString();
        const dataStatus = card.dataset.status || '';

        const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
        const matchesStatus = !statusFilter || statusClass.includes(`status-${statusFilter}`) || dataStatus === statusFilter;

        card.style.display = (matchesSearch && matchesStatus) ? 'block' : 'none';
    });
}

function resetFilters() {
    const searchEl = document.getElementById('search-projects') || document.getElementById('searchProjects');
    const statusEl = document.getElementById('filter-status') || document.getElementById('statusFilter');
    if (searchEl) searchEl.value = '';
    if (statusEl) statusEl.value = '';
    filterProjects();
}

// Utilitários
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}

function getCsrfToken() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
}

function showNotification(message, type = 'info') {
    // Implementar sistema de notificações real ou usar console
    console.log(`${type.toUpperCase()}: ${message}`);
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
