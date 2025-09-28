(function ($) {
  'use strict';

  function calculateTotal(row) {
    var quantite = parseFloat(row.find('input[name$="-quantite"]').val()) || 0;
    var prixUnitaire = parseFloat(row.find('input[name$="-prix_unitaire"]').val()) || 0;
    var total = quantite * prixUnitaire;

    row.find('input[name$="-total"]').val(total.toFixed(2));
  }

  function bindCalculation() {
    $('.dynamic-itemorcamento_set').on(
      'input',
      'input[name$="-quantite"], input[name$="-prix_unitaire"]',
      function () {
        var row = $(this).closest('tr');
        calculateTotal(row);
      }
    );
  }

  $(document).ready(function () {
    bindCalculation();

    // Rebind when new rows are added
    $('.add-row a').click(function () {
      setTimeout(bindCalculation, 100);
    });
  });
})(django.jQuery);
