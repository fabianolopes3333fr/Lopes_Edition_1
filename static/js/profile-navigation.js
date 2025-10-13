document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
});

function initializeNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');

    navButtons.forEach(button => {
        button.addEventListener('click', function() {
            const section = this.dataset.section;
            switchSection(section, this);
        });
    });

    // Ativar primeira seção por padrão
    const firstButton = document.querySelector('[data-section="mes-projets"]');
    switchSection('mes-projets', firstButton);
}

function switchSection(section, button) {
    // Remover classe ativa de todos os botões
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('border-blue-500', 'text-blue-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });

    // Ativar botão atual
    button.classList.remove('border-transparent', 'text-gray-500');
    button.classList.add('border-blue-500', 'text-blue-600');

    // Carregar conteúdo da seção
    loadSectionContent(section);
}

function loadSectionContent(section) {
    const contentContainer = document.getElementById('profile-content');

    // Mostrar loading
    contentContainer.innerHTML = `
        <div class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
    `;

    const base = (window.URLS && window.URLS.accountsPrefix) ? window.URLS.accountsPrefix : '/comptes/';

    // Carregar conteúdo via AJAX
    fetch(`${base}profile/${section}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.text())
    .then(html => {
        contentContainer.innerHTML = html;
    })
    .catch(error => {
        console.error('Erro ao carregar seção:', error);
        contentContainer.innerHTML = `
            <div class="text-center py-12">
                <p class="text-red-600">Erreur lors du chargement</p>
            </div>
        `;
    });
}