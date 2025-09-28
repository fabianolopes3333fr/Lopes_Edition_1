class ProjectFilters {
  constructor() {
    this.searchInput = document.getElementById('search-projects');
    this.statusFilter = document.getElementById('filter-status');
    this.serviceFilter = document.getElementById('filter-service');
    this.projectCards = document.querySelectorAll('.project-card');
    this.noResultsElement = document.getElementById('no-results');

    this.initializeEventListeners();
  }

  initializeEventListeners() {
    // Debounce para busca
    let searchTimeout;
    this.searchInput?.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => this.applyFilters(), 300);
    });

    this.statusFilter?.addEventListener('change', () => this.applyFilters());
    this.serviceFilter?.addEventListener('change', () => this.applyFilters());
  }

  applyFilters() {
    const filters = this.getActiveFilters();
    let visibleCount = 0;

    this.projectCards.forEach((card) => {
      if (this.cardMatchesFilters(card, filters)) {
        this.showCard(card);
        visibleCount++;
      } else {
        this.hideCard(card);
      }
    });

    this.toggleNoResultsMessage(visibleCount === 0 && this.projectCards.length > 0);
    this.updateResultsCount(visibleCount);
  }

  getActiveFilters() {
    return {
      search: this.searchInput?.value.toLowerCase().trim() || '',
      status: this.statusFilter?.value || '',
      service: this.serviceFilter?.value || '',
    };
  }

  cardMatchesFilters(card, filters) {
    const cardData = {
      title: card.getAttribute('data-title') || '',
      status: card.getAttribute('data-status') || '',
      service: card.getAttribute('data-service') || '',
    };

    // Verificar busca por texto
    if (filters.search && !cardData.title.includes(filters.search)) {
      return false;
    }

    // Verificar filtro de status
    if (filters.status && cardData.status !== filters.status) {
      return false;
    }

    // Verificar filtro de serviço
    if (filters.service && cardData.service !== filters.service) {
      return false;
    }

    return true;
  }

  showCard(card) {
    card.style.display = 'block';
    card.style.opacity = '1';
    card.style.transform = 'scale(1)';
  }

  hideCard(card) {
    card.style.display = 'none';
  }

  toggleNoResultsMessage(show) {
    if (this.noResultsElement) {
      this.noResultsElement.classList.toggle('hidden', !show);
    }
  }

  updateResultsCount(count) {
    const countElement = document.getElementById('results-count');
    if (countElement) {
      const total = this.projectCards.length;
      countElement.textContent = `${count} sur ${total} projet${total > 1 ? 's' : ''}`;
    }
  }

  clearFilters() {
    if (this.searchInput) this.searchInput.value = '';
    if (this.statusFilter) this.statusFilter.value = '';
    if (this.serviceFilter) this.serviceFilter.value = '';
    this.applyFilters();
  }
}

// Inicializar filtros quando a seção for carregada
document.addEventListener('DOMContentLoaded', function () {
  // Aguardar carregamento da seção de projetos
  const observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      if (mutation.addedNodes.length > 0) {
        const projectsContainer = document.getElementById('projects-container');
        if (projectsContainer && !window.projectFilters) {
          window.projectFilters = new ProjectFilters();
        }
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
});
