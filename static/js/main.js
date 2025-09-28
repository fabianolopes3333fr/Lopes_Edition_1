document.addEventListener('DOMContentLoaded', function () {
  // Mobile menu toggle
  const mobileMenuButton = document.getElementById('mobile-menu-button');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener('click', function () {
      mobileMenu.classList.toggle('hidden');
    });
  }

  // Smooth scrolling para links internos
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }
    });
  });

  // Formulário de contato via AJAX
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();

      // Mostrar loading
      const submitButton = this.querySelector('button[type="submit"]');
      const originalText = submitButton.innerHTML;
      submitButton.innerHTML = '<div class="spinner mx-auto"></div>';
      submitButton.disabled = true;

      const formData = new FormData(this);

      fetch(this.action || window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            showNotification('Mensagem enviada com sucesso!', 'success');
            this.reset();
          } else {
            showNotification('Erro ao enviar mensagem. Tente novamente.', 'error');
          }
        })
        .catch((error) => {
          console.error('Erro:', error);
          showNotification('Erro ao enviar mensagem. Tente novamente.', 'error');
        })
        .finally(() => {
          // Restaurar botão
          submitButton.innerHTML = originalText;
          submitButton.disabled = false;
        });
    });
  }

  // Animação de entrada para elementos
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
  };

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in-up');
      }
    });
  }, observerOptions);

  // Observar elementos com a classe 'animate-on-scroll'
  document.querySelectorAll('.animate-on-scroll').forEach((el) => {
    observer.observe(el);
  });

  // Validação de senha em tempo real
  const password1 = document.getElementById('id_password1');
  const password2 = document.getElementById('id_password2');

  if (password1) {
    password1.addEventListener('input', function () {
      validatePassword(this.value);
    });
  }

  if (password2) {
    password2.addEventListener('input', function () {
      const password1Value = document.getElementById('id_password1').value;
      const password2Value = this.value;

      if (password2Value && password1Value !== password2Value) {
        this.classList.add('border-red-500');
      } else {
        this.classList.remove('border-red-500');
      }
    });
  }

  // Gerenciar mensagens do Django (com verificação de existência)
  const messagesElement = document.getElementById('messages-json');
  if (messagesElement) {
    try {
      const messages = JSON.parse(messagesElement.textContent);
      messages.forEach((message) => {
        showToast(message.text, message.tags);
      });
    } catch (e) {
      console.warn('Erro ao processar mensagens:', e);
    }
  }

  // Animações de input
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach((input) => {
    input.addEventListener('focus', function () {
      this.classList.add('ring-2', 'ring-blue-500');
    });
    input.addEventListener('blur', function () {
      this.classList.remove('ring-2', 'ring-blue-500');
    });
  });

  // Inicializar funcionalidades do perfil
  initializeProfileFunctions();
});

// Sistema de notificações
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 transition-all duration-300 ${
    type === 'success'
      ? 'bg-green-500 text-white'
      : type === 'error'
      ? 'bg-red-500 text-white'
      : 'bg-blue-500 text-white'
  }`;
  notification.textContent = message;

  document.body.appendChild(notification);

  // Remover após 5 segundos
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => {
      if (document.body.contains(notification)) {
        document.body.removeChild(notification);
      }
    }, 300);
  }, 5000);
}

// Função para alternar a visibilidade da senha
function togglePassword(fieldId) {
  const passwordField = document.getElementById(fieldId);
  const passwordIcon = document.getElementById(fieldId + '-icon');

  if (passwordField && passwordIcon) {
    if (passwordField.type === 'password') {
      passwordField.type = 'text';
      passwordIcon.classList.remove('fa-eye');
      passwordIcon.classList.add('fa-eye-slash');
    } else {
      passwordField.type = 'password';
      passwordIcon.classList.remove('fa-eye-slash');
      passwordIcon.classList.add('fa-eye');
    }
  }
}

// Validação de senha em tempo real
function validatePassword(password) {
  const checks = {
    'length-check': password.length >= 8,
    'uppercase-check': /[A-Z]/.test(password),
    'lowercase-check': /[a-z]/.test(password),
    'number-check': /\d/.test(password),
  };

  Object.keys(checks).forEach((checkId) => {
    const element = document.getElementById(checkId);
    if (element) {
      if (checks[checkId]) {
        element.classList.remove('text-red-500');
        element.classList.add('text-green-500');
      } else {
        element.classList.remove('text-green-500');
        element.classList.add('text-red-500');
      }
    }
  });
}

// Função para exibir mensagens de notificação (toasts)
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `fixed bottom-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white transform transition-all duration-300 translate-x-full ${
    type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'
  }`;
  toast.textContent = message;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove('translate-x-full');
    toast.classList.add('translate-x-0');
  }, 100);

  setTimeout(() => {
    toast.classList.remove('translate-x-0');
    toast.classList.add('translate-x-full');
    setTimeout(() => {
      if (document.body.contains(toast)) {
        document.body.removeChild(toast);
      }
    }, 300);
  }, 5000);
}

// Preview de imagem melhorado
function previewImage(input) {
  if (input.files && input.files[0]) {
    const file = input.files[0];

    // Validar tipo de arquivo
    if (!file.type.startsWith('image/')) {
      showToast('Veuillez sélectionner un fichier image valide.', 'error');
      input.value = '';
      return;
    }

    // Validar tamanho (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      showToast("L'image ne doit pas dépasser 5MB.", 'error');
      input.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = function (e) {
      // Múltiplos seletores para encontrar a imagem de preview
      const selectors = [
        '.profile-avatar img',
        '.h-16.w-16 img',
        '#avatar-preview',
        '[data-avatar-preview]',
      ];

      let preview = null;
      for (const selector of selectors) {
        preview = document.querySelector(selector);
        if (preview) break;
      }

      if (preview) {
        preview.src = e.target.result;
        showToast('Image mise à jour avec succès!', 'success');
      } else {
        console.warn("Élément de preview d'image non trouvé");
      }
    };

    reader.onerror = function () {
      showToast("Erreur lors du chargement de l'image.", 'error');
    };

    reader.readAsDataURL(file);
  }
}

// Funções específicas do perfil
function initializeProfileFunctions() {
  // Gerenciar campos condicionais (empresa/particular)
  const typeClientField = document.getElementById('id_type_client');
  if (typeClientField) {
    typeClientField.addEventListener('change', function () {
      toggleCompanyFields(this.value);
    });
    // Inicializar estado
    toggleCompanyFields(typeClientField.value);
  }
}

// Mostrar/ocultar campos de empresa
function toggleCompanyFields(typeClient) {
  const companyFields = document.querySelectorAll('[data-company-field]');
  const isCompany = typeClient === 'entreprise';

  companyFields.forEach((field) => {
    const container = field.closest('.form-group') || field.parentElement;
    if (container) {
      container.style.display = isCompany ? 'block' : 'none';
      // Tornar obrigatório ou não
      field.required = isCompany;
    }
  });
}

// Função para salvar o perfil via AJAX (opcional)
function saveProfile() {
    const form = document.querySelector('#edit-tab form');
    const formData = new FormData(form);

    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar mensagem de sucesso
            showNotification(data.message, 'success');
            // Voltar para a aba overview
            openTab('overview');
        } else {
            // Mostrar erros
            showNotification(data.message, 'error');
            if (data.errors) {
                displayFormErrors(data.errors);
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Une erreur est survenue', 'error');
    });
}

// Função para mostrar notificações
function showNotification(message, type) {
    // Implementar notificação toast ou alert
    if (type === 'success') {
        alert('Succès: ' + message);
    } else {
        alert('Erreur: ' + message);
    }
}

// Função para exibir erros do formulário
function displayFormErrors(errors) {
    // Limpar erros anteriores
    document.querySelectorAll('.error-message').forEach(el => el.remove());

    // Adicionar novos erros
    for (const [field, messages] of Object.entries(errors)) {
        const fieldElement = document.querySelector(`[name="${field}"]`);
        if (fieldElement) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message text-red-600 text-sm mt-1';
            errorDiv.textContent = messages.join(', ');
            fieldElement.parentNode.appendChild(errorDiv);
        }
    }
}

// Modificar o botão de salvar para usar AJAX (opcional)
document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.querySelector('#edit-tab button[type="submit"]');
    if (saveButton) {
        saveButton.addEventListener('click', function(e) {
            e.preventDefault();
            saveProfile();
        });
    }
});

