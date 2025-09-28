(function ($) {
  'use strict';

  // Aguardar o DOM estar pronto
  $(document).ready(function () {
    console.log('Newsletter Admin JS carregado');

    // Inicializar funcionalidades
    initNewsletterStats();
    initBulkActions();
    initEmailValidation();
    initTooltips();
    initConfirmationDialogs();
    initAutoRefresh();
  });

  // Estatísticas no topo da página
  function initNewsletterStats() {
    // Adicionar estatísticas se não existirem
    if ($('.newsletter-stats').length === 0 && $('.results').length > 0) {
      const statsHtml = `
                <div class="newsletter-stats">
                    <div class="stat-item">
                        <span class="stat-number" id="total-count">-</span>
                        <span class="stat-label">Total</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number" id="active-count">-</span>
                        <span class="stat-label">Ativos</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number" id="confirmed-count">-</span>
                        <span class="stat-label">Confirmados</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number" id="rgpd-count">-</span>
                        <span class="stat-label">RGPD OK</span>
                    </div>
                </div>
            `;
      $('.results').before(statsHtml);
      updateStats();
    }
  }

  // Atualizar estatísticas
  function updateStats() {
    const rows = $('#result_list tbody tr');
    let totalCount = rows.length;
    let activeCount = 0;
    let confirmedCount = 0;
    let rgpdCount = 0;

    rows.each(function () {
      const statusCell = $(this).find('.field-status_display');
      const statusHtml = statusCell.html();

      if (statusHtml && statusHtml.includes('✓ Ativo')) {
        activeCount++;
      }
      if (statusHtml && statusHtml.includes('✓ Confirmado')) {
        confirmedCount++;
      }
      if (statusHtml && statusHtml.includes('✓ RGPD')) {
        rgpdCount++;
      }
    });

    $('#total-count').text(totalCount);
    $('#active-count').text(activeCount);
    $('#confirmed-count').text(confirmedCount);
    $('#rgpd-count').text(rgpdCount);
  }

  // Melhorar ações em massa
  function initBulkActions() {
    const actionSelect = $('select[name="action"]');
    const goButton = $('.actions input[type="submit"]');

    if (actionSelect.length && goButton.length) {
      // Adicionar confirmação para ações destrutivas
      actionSelect.on('change', function () {
        const selectedAction = $(this).val();
        const destructiveActions = ['deactivate_subscribers', 'delete_selected'];

        if (destructiveActions.includes(selectedAction)) {
          goButton.addClass('destructive-action');
          goButton.css({
            'background-color': '#dc3545',
            'border-color': '#dc3545',
          });
        } else {
          goButton.removeClass('destructive-action');
          goButton.css({
            'background-color': '',
            'border-color': '',
          });
        }
      });

      // Interceptar submit para confirmação
      $('.actions form').on('submit', function (e) {
        const selectedAction = actionSelect.val();
        const checkedItems = $('input[name="_selected_action"]:checked');

        if (checkedItems.length === 0) {
          e.preventDefault();
          alert('Por favor, selecione pelo menos um item.');
          return false;
        }

        const destructiveActions = ['deactivate_subscribers', 'delete_selected'];

        if (destructiveActions.includes(selectedAction)) {
          const actionText = actionSelect.find('option:selected').text();
          const confirmMessage = `Tem certeza que deseja executar "${actionText}" em ${checkedItems.length} item(ns)?`;

          if (!confirm(confirmMessage)) {
            e.preventDefault();
            return false;
          }
        }

        // Mostrar loading
        showLoading(goButton);
      });
    }
  }

  // Validação de email em tempo real
  function initEmailValidation() {
    const emailFields = $('input[type="email"], input[name*="email"]');

    emailFields.on('blur', function () {
      const email = $(this).val();
      const field = $(this);

      if (email && !isValidEmail(email)) {
        field.addClass('error');
        showFieldError(field, 'Email inválido');
      } else {
        field.removeClass('error');
        hideFieldError(field);
      }
    });

    emailFields.on('input', function () {
      $(this).removeClass('error');
      hideFieldError($(this));
    });
  }

  // Validar formato de email
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Mostrar erro no campo
  function showFieldError(field, message) {
    hideFieldError(field);
    const errorHtml = `<div class="field-error" style="color: #dc3545; font-size: 12px; margin-top: 5px;">${message}</div>`;
    field.parent().append(errorHtml);
  }

  // Esconder erro do campo
  function hideFieldError(field) {
    field.parent().find('.field-error').remove();
  }

  // Inicializar tooltips
  function initTooltips() {
    // Adicionar tooltips para badges
    $('.interest-badge, .list-badge').each(function () {
      const text = $(this).text();
      $(this).attr('title', text);
    });

    // Tooltip para status
    $('.field-status_display').each(function () {
      const statusText = $(this).text().replace(/\s+/g, ' ').trim();
      $(this).attr('title', 'Status: ' + statusText);
    });

    // Tooltip para datas
    $('[class*="date"]').each(function () {
      const dateText = $(this).text();
      if (dateText && dateText.match(/\d{2}\/\d{2}\/\d{4}/)) {
        $(this).attr('title', 'Data: ' + dateText);
      }
    });
  }

  // Diálogos de confirmação melhorados
  function initConfirmationDialogs() {
    // Interceptar links de delete
    $('a[href*="delete"]').on('click', function (e) {
      const confirmMessage =
        'Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.';
      if (!confirm(confirmMessage)) {
        e.preventDefault();
        return false;
      }
    });

    // Confirmação para mudanças de status importantes
    $('input[name*="active"], input[name*="confirmed"]').on('change', function () {
      const field = $(this);
      const isChecked = field.is(':checked');
      const fieldName = field.attr('name');

      if (fieldName.includes('active') && !isChecked) {
        if (!confirm('Desativar este assinante? Ele não receberá mais emails.')) {
          field.prop('checked', true);
          return false;
        }
      }
    });
  }

  // Auto-refresh para estatísticas
  function initAutoRefresh() {
    // Atualizar estatísticas a cada 30 segundos se a página estiver ativa
    let refreshInterval;

    function startAutoRefresh() {
      refreshInterval = setInterval(function () {
        if (document.visibilityState === 'visible') {
          updateStats();
        }
      }, 30000);
    }

    function stopAutoRefresh() {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    }

    // Iniciar auto-refresh
    startAutoRefresh();

    // Parar quando a página não estiver visível
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'visible') {
        startAutoRefresh();
      } else {
        stopAutoRefresh();
      }
    });

    // Limpar ao sair da página
    $(window).on('beforeunload', function () {
      stopAutoRefresh();
    });
  }

  // Mostrar loading
  function showLoading(button) {
    const originalText = button.val();
    button.data('original-text', originalText);
    button.val('Processando...');
    button.prop('disabled', true);

    // Adicionar spinner
    if (!button.prev('.loading-spinner').length) {
      button.before('<span class="loading-spinner"></span>');
    }
  }

  // Esconder loading
  function hideLoading(button) {
    const originalText = button.data('original-text');
    if (originalText) {
      button.val(originalText);
    }
    button.prop('disabled', false);
    button.prev('.loading-spinner').remove();
  }

  // Melhorar filtros
  function initFilters() {
    // Adicionar contador nos filtros
    $('#changelist-filter a').each(function () {
      const link = $(this);
      const text = link.text();
      const match = text.match(/\((\d+)\)/);

      if (match) {
        const count = match[1];
        const newText = text.replace(/\s*\(\d+\)/, '');
        link.html(`${newText} <span class="filter-count">(${count})</span>`);
      }
    });

    // Destacar filtro ativo
    $('#changelist-filter .selected a').css({
      'font-weight': 'bold',
      'background-color': '#007cba',
      color: 'white',
    });
  }

  // Melhorar busca
  function initSearch() {
    const searchInput = $('#searchbar');

    if (searchInput.length) {
      // Adicionar placeholder melhorado
      searchInput.attr('placeholder', 'Buscar por email, nome ou interesses...');

      // Adicionar ícone de busca
      if (!searchInput.next('.search-icon').length) {
        searchInput.after('<span class="search-icon">🔍</span>');
      }

      // Busca em tempo real (debounced)
      let searchTimeout;
      searchInput.on('input', function () {
        clearTimeout(searchTimeout);
        const query = $(this).val();

        if (query.length >= 3) {
          searchTimeout = setTimeout(function () {
            // Aqui você pode implementar busca AJAX se necessário
            console.log('Buscando por:', query);
          }, 500);
        }
      });
    }
  }

  // Melhorar tabela responsiva
  function initResponsiveTable() {
    const table = $('#result_list');

    if (table.length && $(window).width() < 768) {
      // Adicionar classe para mobile
      table.addClass('mobile-table');

      // Esconder colunas menos importantes em mobile
      const hiddenColumns = [
        '.field-last_activity',
        '.field-date_joined',
        '.field-formatted_interests',
      ];

      hiddenColumns.forEach(function (column) {
        table.find(column).hide();
      });
    }
  }

  // Exportação melhorada
  function initExport() {
    // Adicionar botão de exportação rápida
    if ($('.actions').length && !$('.quick-export').length) {
      const exportButton = `
                                <button type="button" class="quick-export" style="margin-left: 10px;">
                                    📊 Exportar Visíveis
                                </button>
                            `;
      $('.actions').append(exportButton);

      $('.quick-export').on('click', function () {
        exportVisibleRows();
      });
    }
  }

  // Exportar linhas visíveis
  function exportVisibleRows() {
    const rows = $('#result_list tbody tr:visible');
    const data = [];

    // Cabeçalhos
    const headers = [];
    $('#result_list thead th').each(function () {
      const text = $(this).text().trim();
      if (text && text !== 'Ação') {
        headers.push(text);
      }
    });
    data.push(headers);

    // Dados
    rows.each(function () {
      const row = [];
      $(this)
        .find('td')
        .each(function (index) {
          if (index === 0) return; // Pular checkbox
          const text = $(this).text().trim();
          row.push(text);
        });
      data.push(row);
    });

    // Criar e baixar CSV
    const csv = data.map((row) => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `newsletter_export_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  // Inicializar todas as funcionalidades quando a página carregar
  $(window).on('load', function () {
    initFilters();
    initSearch();
    initResponsiveTable();
    initExport();
  });

  // Utilitários globais
  window.NewsletterAdmin = {
    updateStats: updateStats,
    showLoading: showLoading,
    hideLoading: hideLoading,
    exportVisibleRows: exportVisibleRows,
  };
})(django.jQuery);
