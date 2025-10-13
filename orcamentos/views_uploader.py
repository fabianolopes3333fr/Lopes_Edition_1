from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .auditoria import AuditoriaManager
from .models import Projeto, AnexoProjeto


@login_required
@require_http_methods(["POST"])
def upload_anexo_projeto(request, uuid):
    """Upload de anexo via AJAX"""
    try:
        projeto = get_object_or_404(Projeto, uuid=uuid, cliente=request.user)

        # Verificar se há arquivo no request
        if 'arquivo' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'Nenhum arquivo enviado'})

        arquivo = request.FILES['arquivo']
        descricao = request.POST.get('descricao', '')

        # Validar tipo de arquivo
        tipos_permitidos = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        if not any(arquivo.name.lower().endswith(ext) for ext in tipos_permitidos):
            return JsonResponse({
                'success': False,
                'error': 'Tipo de arquivo não permitido. Use: PDF, JPG, PNG, DOC, DOCX'
            })

        # Criar anexo usando o modelo correto
        anexo = AnexoProjeto.objects.create(
            projeto=projeto,
            arquivo=arquivo,
            descricao=descricao
        )

        # Registrar na auditoria
        AuditoriaManager.registrar_criacao(
            usuario=request.user,
            objeto=anexo,
            request=request
        )

        return JsonResponse({
            'success': True,
            'anexo': {
                'id': anexo.id,
                'arquivo': anexo.arquivo.url,
                'descricao': anexo.descricao or 'Arquivo',
                'created_at': anexo.created_at.strftime('%d/%m/%Y %H:%M')
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao fazer upload: {str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def excluir_anexo_projeto(request, uuid, anexo_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método não permitido'})

    try:
        # Verificar se é o dono do projeto
        projeto = get_object_or_404(Projeto, uuid=uuid, cliente=request.user)
        anexo = get_object_or_404(AnexoProjeto, id=anexo_id, projeto=projeto)

        # Registrar exclusão na auditoria antes de deletar
        from .auditoria import AuditoriaManager
        AuditoriaManager.registrar_exclusao(
            usuario=request.user,
            objeto=anexo,
            request=request
        )

        # Deletar arquivo físico se existir
        if anexo.arquivo:
            try:
                anexo.arquivo.delete()
            except:
                pass  # Ignorar erro se arquivo não existir fisicamente

        # Deletar registro
        anexo.delete()

        return JsonResponse({'success': True, 'message': 'Anexo excluído com sucesso'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})