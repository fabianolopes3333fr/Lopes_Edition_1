class NotificationSystem {
  constructor() {
    this.container = this.createContainer();
    this.notifications = [];
  }

  createContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.className = 'fixed top-4 right-4 z-50 space-y-2';
    document.body.appendChild(container);
    return container;
  }

  show(message, type = 'info', duration = 5000) {
    const notification = this.createNotification(message, type);
    this.container.appendChild(notification);
    this.notifications.push(notification);

    // Animação de entrada
    setTimeout(() => {
      notification.classList.add('opacity-100', 'translate-x-0');
      notification.classList.remove('opacity-0', 'translate-x-full');
    }, 10);

    // Auto-remover
    if (duration > 0) {
      setTimeout(() => {
        this.remove(notification);
      }, duration);
    }

    return notification;
  }

  createNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} opacity-0 translate-x-full transform transition-all duration-300 ease-in-out`;

    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-exclamation-circle',
      warning: 'fas fa-exclamation-triangle',
      info: 'fas fa-info-circle',
    };

    notification.innerHTML = `
            <div class="flex items-center">
                <i class="${icons[type] || icons.info} mr-3"></i>
                <span class="flex-1">${message}</span>
                <button onclick="notificationSystem.remove(this.parentElement.parentElement)" class="ml-3 text-current opacity-70 hover:opacity-100">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

    return notification;
  }

  remove(notification) {
    if (notification && notification.parentElement) {
      notification.classList.add('opacity-0', 'translate-x-full');
      notification.classList.remove('opacity-100', 'translate-x-0');

      setTimeout(() => {
        if (notification.parentElement) {
          notification.parentElement.removeChild(notification);
        }
        const index = this.notifications.indexOf(notification);
        if (index > -1) {
          this.notifications.splice(index, 1);
        }
      }, 300);
    }
  }

  clear() {
    this.notifications.forEach((notification) => {
      this.remove(notification);
    });
  }
}

// Instância global
const notificationSystem = new NotificationSystem();

// Função global para compatibilidade
function showNotification(message, type = 'info', duration = 5000) {
  return notificationSystem.show(message, type, duration);
}
