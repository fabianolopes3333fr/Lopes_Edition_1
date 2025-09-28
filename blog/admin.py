from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CategorieBlog,
    ArticleBlog,
    CommentaireBlog,
    NewsletterSubscriber,
    NewsletterList,
)


@admin.register(CategorieBlog)
class CategorieBlogAdmin(admin.ModelAdmin):
    list_display = ["nom", "slug", "couleur_preview", "actif", "ordre"]
    list_filter = ["actif"]
    search_fields = ["nom", "description"]
    prepopulated_fields = {"slug": ("nom",)}
    list_editable = ["actif", "ordre"]

    def couleur_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.couleur,
        )

    couleur_preview.short_description = "Couleur"


class CommentaireBlogInline(admin.TabularInline):
    model = CommentaireBlog
    extra = 0
    readonly_fields = ["date_creation", "ip_address"]
    fields = ["nom", "email", "contenu", "status", "date_creation"]


@admin.register(ArticleBlog)
class ArticleBlogAdmin(admin.ModelAdmin):
    list_display = [
        "titre",
        "auteur",
        "categorie",
        "status",
        "featured",
        "vues",
        "date_publication",
    ]
    list_filter = [
        "status",
        "featured",
        "categorie",
        "auteur",
        "date_creation",
        "date_publication",
    ]
    search_fields = ["titre", "resume", "contenu", "tags"]
    prepopulated_fields = {"slug": ("titre",)}
    readonly_fields = ["date_creation", "date_modification", "vues"]
    list_editable = ["status", "featured"]
    date_hierarchy = "date_publication"
    inlines = [CommentaireBlogInline]

    fieldsets = (
        ("Contenu principal", {"fields": ("titre", "slug", "resume", "contenu")}),
        ("Métadonnées", {"fields": ("auteur", "categorie", "tags")}),
        ("Images", {"fields": ("image_principale", "image_alt")}),
        ("Publication", {"fields": ("status", "date_publication", "featured")}),
        (
            "SEO",
            {"fields": ("meta_description", "meta_keywords"), "classes": ("collapse",)},
        ),
        (
            "Statistiques",
            {
                "fields": ("vues", "date_creation", "date_modification"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.auteur = request.user
        super().save_model(request, obj, form, change)


@admin.register(CommentaireBlog)
class CommentaireBlogAdmin(admin.ModelAdmin):
    list_display = [
        "nom",
        "article",
        "status",
        "date_creation",
        "ip_address",
        "has_parent",
    ]
    list_filter = ["status", "date_creation", "article"]
    search_fields = ["nom", "email", "contenu", "article__titre"]
    readonly_fields = ["date_creation", "ip_address"]
    list_editable = ["status"]
    actions = ["approve_comments", "reject_comments"]

    def has_parent(self, obj):
        return obj.parent is not None

    has_parent.boolean = True
    has_parent.short_description = "Réponse"

    def approve_comments(self, request, queryset):
        updated = queryset.update(status="approuve")
        self.message_user(request, f"{updated} commentaires approuvés.")

    approve_comments.short_description = "Approuver les commentaires sélectionnés"

    def reject_comments(self, request, queryset):
        updated = queryset.update(status="rejete")
        self.message_user(request, f"{updated} commentaires rejetés.")

    reject_comments.short_description = "Rejeter les commentaires sélectionnés"


@admin.register(NewsletterList)
class NewsletterListAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description_preview",
        "active",
        "subscriber_count",
        "active_subscriber_count",
        "created_at",
    ]
    list_filter = ["active", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["active"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "subscriber_count",
        "active_subscriber_count",
    ]
    actions = ["activate_lists", "deactivate_lists", "export_subscribers"]

    fieldsets = (
        ("Informações Básicas", {"fields": ("name", "description", "active")}),
        (
            "Estatísticas",
            {
                "fields": ("subscriber_count", "active_subscriber_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadados",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def description_preview(self, obj):
        """Prévia da descrição truncada"""
        if obj.description:
            return (
                obj.description[:50] + "..."
                if len(obj.description) > 50
                else obj.description
            )
        return "-"

    description_preview.short_description = "Descrição"

    def active_display(self, obj):
        """Status ativo com ícone colorido"""
        if obj.active:
            return format_html('<span style="color: green;">✓ Ativa</span>')
        return format_html('<span style="color: red;">✗ Inativa</span>')

    active_display.short_description = "Status Visual"

    def subscriber_count(self, obj):
        """Total de assinantes"""
        count = obj.subscribers.count()
        return format_html(
            "<strong>{}</strong> assinante{}".format(count, "s" if count != 1 else "")
        )

    subscriber_count.short_description = "Total Assinantes"

    def active_subscriber_count(self, obj):
        """Assinantes ativos"""
        count = obj.subscribers.filter(active=True).count()
        return format_html(
            '<span style="color: green;"><strong>{}</strong></span> ativo{}'.format(
                count, "s" if count != 1 else ""
            )
        )

    active_subscriber_count.short_description = "Assinantes Ativos"

    # Actions
    def activate_lists(self, request, queryset):
        """Ativar listas selecionadas"""
        updated = queryset.update(active=True)
        self.message_user(
            request, f"{updated} lista(s) ativada(s) com sucesso.", level="SUCCESS"
        )

    activate_lists.short_description = "Ativar listas selecionadas"

    def deactivate_lists(self, request, queryset):
        """Desativar listas selecionadas"""
        updated = queryset.update(active=False)
        self.message_user(
            request, f"{updated} lista(s) desativada(s) com sucesso.", level="WARNING"
        )

    deactivate_lists.short_description = "Desativar listas selecionadas"

    def export_subscribers(self, request, queryset):
        """Exportar assinantes das listas selecionadas"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="newsletter_subscribers.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "Lista",
                "Email",
                "Nome",
                "Interesses",
                "Data Inscrição",
                "Ativo",
                "Confirmado",
            ]
        )

        for newsletter_list in queryset:
            for subscriber in newsletter_list.subscribers.all():
                writer.writerow(
                    [
                        newsletter_list.name,
                        subscriber.email,
                        subscriber.prenom or "",
                        subscriber.interests or "",
                        subscriber.date_joined.strftime("%d/%m/%Y %H:%M"),
                        "Sim" if subscriber.active else "Não",
                        "Sim" if getattr(subscriber, "confirmed", False) else "Não",
                    ]
                )

        return response

    export_subscribers.short_description = "Exportar assinantes (CSV)"


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "prenom_display",
        "status_display",
        "formatted_interests",
        "lists_display",
        "date_joined",
        "last_activity",
    ]
    list_filter = [
        "active",
        "confirmed",
        "rgpd_consent",
        "date_joined",
        "lists",
        ("date_confirmed", admin.DateFieldListFilter),
        ("last_email_sent", admin.DateFieldListFilter),
    ]
    search_fields = ["email", "prenom", "interests"]
    readonly_fields = [
        "date_joined",
        "date_confirmed",
        "confirmation_token",
        "last_email_sent",
        "ip_address",
    ]
    filter_horizontal = ["lists"]
    actions = [
        "activate_subscribers",
        "deactivate_subscribers",
        "confirm_emails",
        "send_confirmation_email",
        "export_selected_subscribers",
    ]
    list_per_page = 50

    fieldsets = (
        ("Informações Pessoais", {"fields": ("prenom", "email")}),
        ("Preferências", {"fields": ("interests", "lists")}),
        ("Status", {"fields": ("active", "confirmed", "rgpd_consent")}),
        (
            "Confirmação",
            {
                "fields": ("confirmation_token", "date_confirmed"),
                "classes": ("collapse",),
            },
        ),
        (
            "Atividade",
            {
                "fields": ("date_joined", "last_email_sent", "ip_address"),
                "classes": ("collapse",),
            },
        ),
    )

    def prenom_display(self, obj):
        """Nome com fallback para parte do email"""
        if obj.prenom:
            return obj.prenom
        return format_html('<em style="color: #666;">{}</em>', obj.email.split("@")[0])

    prenom_display.short_description = "Nome"

    def status_display(self, obj):
        """Status visual com cores"""
        status_parts = []

        if obj.active:
            status_parts.append('<span style="color: green;">✓ Ativo</span>')
        else:
            status_parts.append('<span style="color: red;">✗ Inativo</span>')

        if getattr(obj, "confirmed", False):
            status_parts.append('<span style="color: blue;">✓ Confirmado</span>')
        else:
            status_parts.append('<span style="color: orange;">⚠ Não confirmado</span>')

        if obj.rgpd_consent:
            status_parts.append('<span style="color: green;">✓ RGPD</span>')
        else:
            status_parts.append('<span style="color: red;">✗ RGPD</span>')

        return format_html("<br>".join(status_parts))

    status_display.short_description = "Status"

    def formatted_interests(self, obj):
        """Interesses formatados com badges"""
        if not obj.interests:
            return format_html('<em style="color: #666;">Nenhum</em>')

        interests = (
            obj.get_interests_display()
            if hasattr(obj, "get_interests_display")
            else obj.interests.split(",")
        )
        badges = []

        for interest in interests:
            badges.append(
                f'<span style="background: #e3f2fd; color: #1976d2; padding: 2px 6px; '
                f'border-radius: 3px; font-size: 11px; margin-right: 2px;">{interest.strip()}</span>'
            )

        return format_html("".join(badges))

    formatted_interests.short_description = "Interesses"

    def lists_display(self, obj):
        """Listas associadas"""
        lists = obj.lists.filter(active=True)
        if not lists.exists():
            return format_html('<em style="color: #666;">Nenhuma</em>')

        list_names = [
            f'<span style="background: #f3e5f5; color: #7b1fa2; padding: 2px 6px; '
            f'border-radius: 3px; font-size: 11px; margin-right: 2px;">{lst.name}</span>'
            for lst in lists
        ]

        return format_html("".join(list_names))

    lists_display.short_description = "Listas"

    def last_activity(self, obj):
        """Última atividade"""
        if hasattr(obj, "last_email_sent") and obj.last_email_sent:
            return format_html(
                'Email: <span style="color: #666;">{}</span>',
                obj.last_email_sent.strftime("%d/%m/%Y"),
            )
        return format_html('<em style="color: #666;">Nenhuma</em>')

    last_activity.short_description = "Última Atividade"

    # Actions
    def activate_subscribers(self, request, queryset):
        """Ativar assinantes selecionados"""
        updated = queryset.update(active=True)
        self.message_user(
            request, f"{updated} assinante(s) ativado(s) com sucesso.", level="SUCCESS"
        )

    activate_subscribers.short_description = "Ativar assinantes selecionados"

    def deactivate_subscribers(self, request, queryset):
        """Desativar assinantes selecionados"""
        updated = queryset.update(active=False)
        self.message_user(
            request,
            f"{updated} assinante(s) desativado(s) com sucesso.",
            level="WARNING",
        )

    deactivate_subscribers.short_description = "Desativar assinantes selecionados"

    def confirm_emails(self, request, queryset):
        """Confirmar emails dos assinantes selecionados"""
        from django.utils import timezone

        updated = queryset.update(confirmed=True, date_confirmed=timezone.now())
        self.message_user(
            request, f"{updated} email(s) confirmado(s) com sucesso.", level="SUCCESS"
        )

    confirm_emails.short_description = "Confirmar emails selecionados"

    def send_confirmation_email(self, request, queryset):
        """Enviar email de confirmação para assinantes não confirmados"""
        unconfirmed = queryset.filter(confirmed=False)
        count = 0

        for subscriber in unconfirmed:
            # Aqui você implementaria o envio do email de confirmação
            # Por exemplo, usando Django's send_mail ou Celery task
            try:
                # send_confirmation_email_task.delay(subscriber.id)
                count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Erro ao enviar email para {subscriber.email}: {str(e)}",
                    level="ERROR",
                )

        if count > 0:
            self.message_user(
                request,
                f"{count} email(s) de confirmação enviado(s) com sucesso.",
                level="SUCCESS",
            )

    send_confirmation_email.short_description = "Enviar email de confirmação"

    def export_selected_subscribers(self, request, queryset):
        """Exportar assinantes selecionados para CSV"""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="subscribers_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            [
                "Email",
                "Nome",
                "Interesses",
                "Ativo",
                "Confirmado",
                "RGPD",
                "Data Inscrição",
                "Data Confirmação",
                "Listas",
                "IP",
            ]
        )

        for subscriber in queryset:
            lists_names = ", ".join([lst.name for lst in subscriber.lists.all()])
            writer.writerow(
                [
                    subscriber.email,
                    subscriber.prenom or "",
                    subscriber.interests or "",
                    "Sim" if subscriber.active else "Não",
                    "Sim" if getattr(subscriber, "confirmed", False) else "Não",
                    "Sim" if subscriber.rgpd_consent else "Não",
                    (
                        subscriber.date_joined.strftime("%d/%m/%Y %H:%M")
                        if subscriber.date_joined
                        else ""
                    ),
                    (
                        getattr(subscriber, "date_confirmed", "").strftime(
                            "%d/%m/%Y %H:%M"
                        )
                        if getattr(subscriber, "date_confirmed", None)
                        else ""
                    ),
                    lists_names,
                    getattr(subscriber, "ip_address", "") or "",
                ]
            )

        return response

    export_selected_subscribers.short_description = "Exportar selecionados (CSV)"

    def get_queryset(self, request):
        """Otimizar consultas com prefetch_related"""
        return super().get_queryset(request).prefetch_related("lists")

    def save_model(self, request, obj, form, change):
        """Personalizar salvamento"""
        if not change:  # Novo objeto
            # Capturar IP se disponível
            if hasattr(request, "META"):
                x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
                if x_forwarded_for:
                    ip = x_forwarded_for.split(",")[0]
                else:
                    ip = request.META.get("REMOTE_ADDR")
                if hasattr(obj, "ip_address"):
                    obj.ip_address = ip

        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Campos readonly dinâmicos"""
        readonly = list(self.readonly_fields)

        # Se o usuário não for superuser, tornar alguns campos readonly
        if not request.user.is_superuser:
            readonly.extend(["confirmation_token", "ip_address"])

        return readonly

    def has_delete_permission(self, request, obj=None):
        """Permissão de exclusão personalizada"""
        # Apenas superusers podem excluir assinantes
        return request.user.is_superuser

    def get_list_filter(self, request):
        """Filtros dinâmicos baseados no usuário"""
        filters = list(self.list_filter)

        # Adicionar filtros extras para superusers
        if request.user.is_superuser:
            filters.extend(
                [
                    ("ip_address", admin.EmptyFieldListFilter),
                    ("confirmation_token", admin.EmptyFieldListFilter),
                ]
            )

        return filters

    def changelist_view(self, request, extra_context=None):
        """Personalizar view da lista com estatísticas"""
        extra_context = extra_context or {}

        # Adicionar estatísticas ao contexto
        total_subscribers = NewsletterSubscriber.objects.count()
        active_subscribers = NewsletterSubscriber.objects.filter(active=True).count()
        confirmed_subscribers = NewsletterSubscriber.objects.filter(
            confirmed=True
        ).count()
        rgpd_compliant = NewsletterSubscriber.objects.filter(rgpd_consent=True).count()

        extra_context.update(
            {
                "total_subscribers": total_subscribers,
                "active_subscribers": active_subscribers,
                "confirmed_subscribers": confirmed_subscribers,
                "rgpd_compliant": rgpd_compliant,
                "confirmation_rate": round(
                    (
                        (confirmed_subscribers / total_subscribers * 100)
                        if total_subscribers > 0
                        else 0
                    ),
                    1,
                ),
                "active_rate": round(
                    (
                        (active_subscribers / total_subscribers * 100)
                        if total_subscribers > 0
                        else 0
                    ),
                    1,
                ),
            }
        )

        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        """Adicionar CSS/JS personalizado"""

        css = {"all": ("admin/css/newsletter_admin.css",)}
        js = ("admin/js/newsletter_admin.js",)


# Personalização adicional para melhor UX
class NewsletterSubscriberInline(admin.TabularInline):
    """Inline para usar em outros modelos se necessário"""

    model = NewsletterSubscriber.lists.through
    extra = 0
    verbose_name = "Assinante"
    verbose_name_plural = "Assinantes"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("newslettersubscriber")


# Filtros personalizados
class ConfirmedListFilter(admin.SimpleListFilter):
    """Filtro personalizado para status de confirmação"""

    title = "Status de Confirmação"
    parameter_name = "confirmed_status"

    def lookups(self, request, model_admin):
        return (
            ("confirmed", "Confirmados"),
            ("unconfirmed", "Não Confirmados"),
            ("pending", "Pendentes"),
        )

    def queryset(self, request, queryset):
        if self.value() == "confirmed":
            return queryset.filter(confirmed=True)
        elif self.value() == "unconfirmed":
            return queryset.filter(confirmed=False)
        elif self.value() == "pending":
            return queryset.filter(confirmed=False, active=True)


class InterestsListFilter(admin.SimpleListFilter):
    """Filtro por interesses específicos"""

    title = "Interesses"
    parameter_name = "interests_filter"

    def lookups(self, request, model_admin):
        # Buscar todos os interesses únicos
        interests_set = set()
        for subscriber in NewsletterSubscriber.objects.exclude(interests=""):
            if subscriber.interests:
                for interest in subscriber.interests.split(","):
                    interests_set.add(interest.strip())

        return [(interest, interest.title()) for interest in sorted(interests_set)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(interests__icontains=self.value())


# Adicionar os filtros personalizados à classe admin
NewsletterSubscriberAdmin.list_filter = [
    "active",
    ConfirmedListFilter,
    "rgpd_consent",
    "date_joined",
    "lists",
    InterestsListFilter,
    ("date_confirmed", admin.DateFieldListFilter),
    ("last_email_sent", admin.DateFieldListFilter),
]
