document.addEventListener('DOMContentLoaded', function () {
  // Aguardar carregamento da seção de projetos
  const observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.addedNodes.length > 0) {
        const projectsContainer = document.getElementById('projects-container');
        if (projectsContainer && !window.projectsInitialized) {
          initializeProjectsSection();
          window.projectsInitialized = true;
        }
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
});

function initializeProjectsSection() {
  // Inicializar filtros
  if (typeof ProjectFilters !== 'undefined') {
    window.projectFilters = new ProjectFilters();
  }

  // Inicializar ordenação
  if (typeof ProjectSorter !== 'undefined') {
    window.projectSorter = new ProjectSorter();
  }

  // Adicionar data attributes necessários para ordenação
  addDataAttributesToCards();

  console.log('Seção de projetos inicializada com sucesso');
}

function addDataAttributesToCards() {
  document.querySelectorAll('.project-card').forEach((card) => {
    // Adicionar data-date se não existir
    if (!card.hasAttribute('data-date')) {
      const dateElement =
        card.querySelector('[data-date]') || card.querySelector('span:contains("Créé le")');
      if (dateElement) {
        const dateText = dateElement.textContent;
        const dateMatch = dateText.match(/(\d{2}\/\d{2}\/\d{4})/);
        if (dateMatch) {
          const [day, month, year] = dateMatch[1].split('/');
          card.setAttribute('data-date', `${year}-${month}-${day}`);
        }
      }
    }

    // Adicionar data-budget se não existir
    if (!card.hasAttribute('data-budget')) {
      const budgetElement = card.querySelector('span:contains("Budget:")');
      if (budgetElement) {
        const budgetMatch = budgetElement.textContent.match(/(\d+(?:\.\d+)?)/);
        if (budgetMatch) {
          card.setAttribute('data-budget', budgetMatch[1]);
        }
      }
    }
  });
}
