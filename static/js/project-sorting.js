class ProjectSorter {
  constructor() {
    this.currentSort = { field: 'date_creation', direction: 'desc' };
    this.initializeSortButtons();
  }

  initializeSortButtons() {
    document.querySelectorAll('[data-sort]').forEach((button) => {
      button.addEventListener('click', (e) => {
        const field = e.currentTarget.getAttribute('data-sort');
        this.sortProjects(field);
      });
    });
  }

  sortProjects(field) {
    const container = document.getElementById('projects-grid');
    if (!container) return;

    const cards = Array.from(container.querySelectorAll('.project-card'));

    // Alternar direção se for o mesmo campo
    if (this.currentSort.field === field) {
      this.currentSort.direction = this.currentSort.direction === 'asc' ? 'desc' : 'asc';
    } else {
      this.currentSort.field = field;
      this.currentSort.direction = 'asc';
    }

    // Ordenar cards
    cards.sort((a, b) => {
      const valueA = this.getCardValue(a, field);
      const valueB = this.getCardValue(b, field);

      let comparison = 0;
      if (valueA < valueB) comparison = -1;
      if (valueA > valueB) comparison = 1;

      return this.currentSort.direction === 'desc' ? -comparison : comparison;
    });

    // Reordenar no DOM
    cards.forEach((card) => container.appendChild(card));

    // Atualizar indicadores visuais
    this.updateSortIndicators();
  }

  getCardValue(card, field) {
    switch (field) {
      case 'title':
        return card.querySelector('h3').textContent.toLowerCase();
      case 'status':
        return card.getAttribute('data-status');
      case 'service':
        return card.getAttribute('data-service');
      case 'date_creation':
        return new Date(card.getAttribute('data-date') || 0);
      case 'budget':
        return parseFloat(card.getAttribute('data-budget') || 0);
      default:
        return '';
    }
  }

  updateSortIndicators() {
    // Remover indicadores existentes
    document.querySelectorAll('[data-sort]').forEach((button) => {
      button.classList.remove('sort-active', 'sort-asc', 'sort-desc');
      const icon = button.querySelector('.sort-icon');
      if (icon) icon.remove();
    });

    // Adicionar indicador ao botão ativo
    const activeButton = document.querySelector(`[data-sort="${this.currentSort.field}"]`);
    if (activeButton) {
      activeButton.classList.add('sort-active', `sort-${this.currentSort.direction}`);

      const icon = document.createElement('i');
      icon.className = `fas fa-chevron-${
        this.currentSort.direction === 'asc' ? 'up' : 'down'
      } ml-1 sort-icon`;
      activeButton.appendChild(icon);
    }
  }
}
