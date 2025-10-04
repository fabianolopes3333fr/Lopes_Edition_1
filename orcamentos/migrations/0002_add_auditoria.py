# Generated migration for auditoria models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orcamentos', '0001_initial'),  # Adjust based on your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='LogAuditoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('sessao_id', models.CharField(blank=True, max_length=40)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('acao', models.CharField(choices=[('criacao', 'Création'), ('edicao', 'Modification'), ('exclusao', 'Suppression'), ('visualizacao', 'Consultation'), ('envio', 'Envoi'), ('aprovacao', 'Approbation'), ('rejeicao', 'Rejet'), ('cancelamento', 'Annulation')], max_length=20, verbose_name='Action')),
                ('descricao', models.TextField(verbose_name='Description')),
                ('object_id', models.PositiveIntegerField()),
                ('dados_anteriores', models.JSONField(blank=True, null=True, verbose_name='Données précédentes')),
                ('dados_posteriores', models.JSONField(blank=True, null=True, verbose_name='Nouvelles données')),
                ('campos_alterados', models.JSONField(blank=True, null=True, verbose_name='Champs modifiés')),
                ('modulo', models.CharField(max_length=50, verbose_name='Module')),
                ('funcionalidade', models.CharField(max_length=100, verbose_name='Fonctionnalité')),
                ('sucesso', models.BooleanField(default=True)),
                ('erro_mensagem', models.TextField(blank=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logs_auditoria', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Log d'audit",
                'verbose_name_plural': "Logs d'audit",
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddIndex(
            model_name='logauditoria',
            index=models.Index(fields=['timestamp'], name='orcamentos_l_timesta_idx'),
        ),
        migrations.AddIndex(
            model_name='logauditoria',
            index=models.Index(fields=['usuario'], name='orcamentos_l_usuario_idx'),
        ),
        migrations.AddIndex(
            model_name='logauditoria',
            index=models.Index(fields=['acao'], name='orcamentos_l_acao_idx'),
        ),
        migrations.AddIndex(
            model_name='logauditoria',
            index=models.Index(fields=['modulo'], name='orcamentos_l_modulo_idx'),
        ),
        migrations.AddIndex(
            model_name='logauditoria',
            index=models.Index(fields=['content_type', 'object_id'], name='orcamentos_l_content_obj_idx'),
        ),
    ]
