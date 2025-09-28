function loadSectionContent(section) {
  const contentArea = document.getElementById('content-area');
  if (!contentArea) return;

  // Mostrar loading específico para projetos
  if (section === 'mes-projets') {
    showProjectsLoading();
  } else {
    contentArea.innerHTML =
      '<div class="flex justify-center items-center h-64"><div class="loading-spinner"></div></div>';
  }

  fetch(`/accounts/section/${section}/`, {
    method: 'GET',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': getCsrfToken(),
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.text();
    })
    .then((html) => {
      contentArea.innerHTML = html;

      // Reinicializar filtros se for seção de projetos
      if (section === 'mes-projets') {
        setTimeout(() => {
          window.projectFilters = new ProjectFilters();
        }, 100);
      }

      // Executar scripts inline se houver
      const scripts = contentArea.querySelectorAll('script');
      scripts.forEach((script) => {
        const newScript = document.createElement('script');
        newScript.textContent = script.textContent;
        document.head.appendChild(newScript);
        document.head.removeChild(newScript);
      });
    })
    .catch((error) => {
      console.error('Erro ao carregar seção:', error);
      contentArea.innerHTML = `
            <div class="text-center py-12">
                <div class="mx-auto w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mb-4">
                    <i class="fas fa-exclamation-triangle text-3xl text-red-500"></i>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">Erreur de chargement</h3>
                <p class="text-gray-500 mb-4">Impossible de charger le contenu demandé.</p>
                <button onclick="loadSectionContent('${section}')" class="btn-primary">
                    <i class="fas fa-redo mr-2"></i>
                    Réessayer
                </button>
            </div>
        `;
    });
}
