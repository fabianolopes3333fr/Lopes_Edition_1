# Configurações de Auditoria para Django Settings

# Adicionar ao INSTALLED_APPS
AUDITORIA_APPS = [
    'orcamentos',
]

# Middleware de auditoria (adicionar ao MIDDLEWARE)
AUDITORIA_MIDDLEWARE = [
    'orcamentos.middleware.AuditoriaMiddleware',
]

# Configurações específicas da auditoria
AUDITORIA_CONFIG = {
    # Habilitar auditoria automática
    'AUDITORIA_HABILITADA': True,

    # Modelos a serem monitorados
    'MODELOS_MONITORADOS': [
        'orcamentos.Projeto',
        'orcamentos.SolicitacaoOrcamento',
        'orcamentos.Orcamento',
        'orcamentos.ItemOrcamento',
    ],

    # Ações a serem registradas
    'ACOES_REGISTRADAS': [
        'criacao',
        'edicao',
        'exclusao',
        'visualizacao',
        'envio',
        'aprovacao',
        'rejeicao'
    ],

    # Retenção de logs (em dias)
    'RETENCAO_LOGS_DIAS': 365,

    # Campos sensíveis que não devem ser logados
    'CAMPOS_SENSÍVEIS': [
        'password',
        'token',
        'secret'
    ],

    # Limites de performance
    'LIMITE_REGISTROS_CONSULTA': 1000,
    'TIMEOUT_CONSULTA_SEGUNDOS': 30,

    # Configurações de relatórios
    'RELATORIOS': {
        'DIARIO_AUTOMATICO': True,
        'SEMANAL_AUTOMATICO': True,
        'MENSAL_AUTOMATICO': True,
        'PASTA_RELATORIOS': 'logs/auditoria/',
        'FORMATO_ARQUIVO': 'json'  # json, csv, xlsx
    },

    # Notificações
    'NOTIFICACOES': {
        'EMAIL_ADMINS_PROBLEMAS': True,
        'SLACK_WEBHOOK': None,  # URL do webhook do Slack se configurado
        'DISCORD_WEBHOOK': None  # URL do webhook do Discord se configurado
    }
}

# Configuração de logging para auditoria
LOGGING_AUDITORIA = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'auditoria': {
            'format': '{asctime} - {name} - {levelname} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'auditoria_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/auditoria_orcamentos.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'auditoria',
        },
        'auditoria_console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'auditoria',
        },
    },
    'loggers': {
        'orcamentos.auditoria': {
            'handlers': ['auditoria_file', 'auditoria_console'],
            'level': 'INFO',
            'propagate': True,
        },
        'orcamentos.monitor': {
            'handlers': ['auditoria_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configurações de segurança para auditoria
AUDITORIA_SECURITY = {
    # Criptografar dados sensíveis nos logs
    'CRIPTOGRAFAR_DADOS': False,

    # Chave de criptografia (se habilitado)
    'CHAVE_CRIPTOGRAFIA': None,

    # Verificar integridade dos logs
    'VERIFICAR_INTEGRIDADE': True,

    # Backup automático dos logs
    'BACKUP_AUTOMATICO': True,
    'PASTA_BACKUP': 'backups/auditoria/',

    # Compressão de logs antigos
    'COMPRIMIR_LOGS_ANTIGOS': True,
    'DIAS_PARA_COMPRESSAO': 30
}
