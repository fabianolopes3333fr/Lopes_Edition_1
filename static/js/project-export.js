function exportProjects(format = 'csv') {
  const projects = Array.from(
    document.querySelectorAll('.project-card:not([style*="display: none"])')
  );

  if (projects.length === 0) {
    showNotification('Aucun projet à exporter', 'error');
    return;
  }

  const projectData = projects.map((card) => {
    return {
      titre: card.querySelector('h3').textContent.trim(),
      statut: card.getAttribute('data-status'),
      type_service: card.getAttribute('data-service'),
      date_creation: card.querySelector('[data-date]')?.getAttribute('data-date') || '',
      budget: card.querySelector('[data-budget]')?.getAttribute('data-budget') || '',
      adresse: card.querySelector('[data-address]')?.textContent.trim() || '',
    };
  });

  if (format === 'csv') {
    exportToCSV(projectData);
  } else if (format === 'json') {
    exportToJSON(projectData);
  }
}

function exportToCSV(data) {
  const headers = ['Titre', 'Statut', 'Type de Service', 'Date de Création', 'Budget', 'Adresse'];
  const csvContent = [
    headers.join(','),
    ...data.map((row) =>
      [
        `"${row.titre}"`,
        `"${row.statut}"`,
        `"${row.type_service}"`,
        `"${row.date_creation}"`,
        `"${row.budget}"`,
        `"${row.adresse}"`,
      ].join(',')
    ),
  ].join('\n');

  downloadFile(csvContent, 'mes-projets.csv', 'text/csv');
}

function exportToJSON(data) {
  const jsonContent = JSON.stringify(data, null, 2);
  downloadFile(jsonContent, 'mes-projets.json', 'application/json');
}

function downloadFile(content, filename, contentType) {
  const blob = new Blob([content], { type: contentType });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);

  showNotification(`Fichier ${filename} téléchargé avec succès`, 'success');
}
