function showProjectsLoading() {
  const container = document.getElementById('projects-container');
  if (!container) return;

  const skeletonHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            ${Array(6)
              .fill()
              .map(
                () => `
                <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex-1">
                            <div class="skeleton-title w-3/4 mb-2"></div>
                            <div class="skeleton-text w-1/2"></div>
                        </div>
                        <div class="skeleton w-16 h-6 rounded-full"></div>
                    </div>
                    
                    <div class="mb-4">
                        <div class="skeleton-text w-full mb-2"></div>
                        <div class="skeleton-text w-4/5 mb-2"></div>
                        <div class="skeleton-text w-3/5"></div>
                    </div>
                    
                    <div class="space-y-2 mb-4">
                        <div class="skeleton-text w-2/3"></div>
                        <div class="skeleton-text w-1/2"></div>
                        <div class="skeleton-text w-3/4"></div>
                    </div>
                    
                    <div class="flex justify-between items-center pt-4 border-t border-gray-100">
                        <div class="skeleton w-8 h-8 rounded"></div>
                        <div class="flex gap-2">
                            <div class="skeleton w-8 h-8 rounded"></div>
                            <div class="skeleton w-8 h-8 rounded"></div>
                        </div>
                    </div>
                </div>
            `
              )
              .join('')}
        </div>
    `;

  container.innerHTML = skeletonHTML;
}

function hideProjectsLoading() {
  // O conteúdo real substituirá o skeleton automaticamente
}
