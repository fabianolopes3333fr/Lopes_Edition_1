from django.shortcuts import render
from django.http import JsonResponse
from projetos.models import Projeto
from contato.models import Contato
from django.db.models import Q
from .models import CategoriaColor, Couleur


def home(request):
    """Página inicial"""
    try:
        # Projetos visíveis para a homepage (usando visible_site em vez de ativo)
        projetos_destaque = Projeto.objects.filter(visible_site=True).order_by(
            "-date_creation"
        )[:6]

        # Estatísticas para a homepage
        total_projetos = Projeto.objects.filter(visible_site=True).count()

        context = {
            "projetos_destaque": projetos_destaque,
            "total_projetos": total_projetos,
            "anos_experiencia": 15,  # Você pode calcular dinamicamente
            "clientes_satisfeitos": 500,  # Você pode pegar do banco de dados
        }

        return render(request, "pages/home.html", context)

    except Exception as e:
        # Em caso de erro, renderizar página com contexto mínimo
        context = {
            "projetos_destaque": [],
            "total_projetos": 0,
            "anos_experiencia": 15,
            "clientes_satisfeitos": 500,
        }
        return render(request, "pages/home.html", context)


def sobre(request):
    """Página sobre nós"""
    context = {
        "empresa": {
            "nome": "LOPES PEINTURE",
            "fundacao": 2008,
            "experiencia": 15,
            "especializacoes": [
                "Peinture intérieure",
                "Peinture extérieure",
                "Décoration",
                "Rénovation",
                "Papier peint",
            ],
        }
    }
    return render(request, "pages/sobre.html", context)


def servicos(request):
    # Dados da empresa
    empresa = {
        "nome": "LOPES PEINTURE",
        "endereco": "275 chemin de la castellane, 31790 St Sauveur",
        "telefone": "+33 7 69 27 37 76",
        "email": "admlopespeinture@gmail.com",
        "site": "www.lopespeinture.fr",
    }

    # Services
    services = [
        {
            "title": "Peinture Intérieure",
            "description": "Transformez vos espaces intérieurs avec nos services de peinture professionnelle pour murs, plafonds, boiseries et plus encore.",
            "icon": "fas fa-brush",
            "link": "#",
        },
        {
            "title": "Peinture Extérieure",
            "description": "Protégez et embellissez l'extérieur de votre propriété avec nos services de peinture extérieure durables et résistants aux intempéries.",
            "icon": "fas fa-home",
            "link": "#",
        },
        {
            "title": "Revêtements Muraux",
            "description": "Ajoutez du caractère à vos murs avec notre sélection de papiers peints, revêtements décoratifs et techniques de finition spéciales.",
            "icon": "fas fa-layer-group",
            "link": "#",
        },
        {
            "title": "Rénovation",
            "description": "Services complets de rénovation incluant la préparation des surfaces, réparations, rebouchage et mise en peinture.",
            "icon": "fas fa-tools",
            "link": "#",
        },
        {
            "title": "Conseil en Décoration",
            "description": "Bénéficiez des conseils de nos experts en décoration pour choisir les couleurs, textures et finitions adaptées à votre espace.",
            "icon": "fas fa-palette",
            "link": "#",
        },
        {
            "title": "Peinture Commerciale",
            "description": "Solutions de peinture professionnelles pour bureaux, commerces, restaurants et autres espaces commerciaux.",
            "icon": "fas fa-building",
            "link": "#",
        },
    ]

    # Process steps
    process_steps = [
        {
            "title": "Consultation initiale",
            "description": "Nous commençons par une consultation pour comprendre vos besoins, préférences et objectifs pour votre projet.",
        },
        {
            "title": "Évaluation et devis",
            "description": "Nous évaluons votre espace, prenons des mesures et vous fournissons un devis détaillé et transparent.",
        },
        {
            "title": "Planification du projet",
            "description": "Une fois le devis approuvé, nous planifions le projet en détail, en établissant un calendrier qui convient à votre emploi du temps.",
        },
        {
            "title": "Préparation des surfaces",
            "description": "Nous préparons soigneusement toutes les surfaces à peindre, en effectuant les réparations nécessaires pour garantir un résultat impeccable.",
        },
        {
            "title": "Application de la peinture",
            "description": "Nos artisans appliquent la peinture avec précision et expertise, en utilisant des techniques professionnelles et des produits de qualité.",
        },
        {
            "title": "Inspection finale",
            "description": "Nous effectuons une inspection minutieuse pour nous assurer que le travail répond à nos normes élevées et à vos attentes.",
        },
    ]

    # FAQs
    faqs = [
        {
            "question": "Combien de temps dure un projet de peinture typique ?",
            "answer": "La durée d'un projet dépend de sa taille et de sa complexité. Une pièce standard peut prendre 1-2 jours, tandis qu'une maison entière peut nécessiter 1-2 semaines. Nous vous fournirons un calendrier précis lors de notre devis.",
        },
        {
            "question": "Quels types de peinture utilisez-vous ?",
            "answer": "Nous utilisons des peintures de haute qualité de marques réputées, adaptées à chaque type de surface et d'environnement. Nous proposons également des options écologiques à faible teneur en COV pour les clients soucieux de l'environnement.",
        },
        {
            "question": "Faut-il que je déplace mes meubles avant votre arrivée ?",
            "answer": "Nous pouvons déplacer les meubles légers dans le cadre de notre service. Pour les pièces très meublées, nous vous recommandons de déplacer les petits objets et objets fragiles. Les meubles lourds seront protégés et déplacés par notre équipe si nécessaire.",
        },
        {
            "question": "Proposez-vous une garantie sur vos travaux ?",
            "answer": "Oui, tous nos travaux sont garantis. Nous offrons une garantie de 2 ans sur la main-d'œuvre et nous respectons les garanties des fabricants pour les produits utilisés. Votre satisfaction est notre priorité.",
        },
        {
            "question": "Comment puis-je préparer ma maison avant votre arrivée ?",
            "answer": "Pour préparer votre maison, nous vous recommandons de retirer les objets fragiles, les décorations murales et les petits objets. Assurez-vous également que les zones à peindre sont accessibles et que les animaux domestiques sont dans un espace sécurisé.",
        },
    ]

    context = {
        "empresa": empresa,
        "services": services,
        "process_steps": process_steps,
        "faqs": faqs,
    }

    return render(request, "pages/services.html", context)


def contato_view(request):
    """Página de contato"""
    if request.method == "POST":
        try:
            # Processar formulário de contato
            nome = request.POST.get("nome")
            email = request.POST.get("email")
            telefone = request.POST.get("telefone")
            assunto = request.POST.get("assunto")
            mensagem = request.POST.get("mensagem")

            # Criar contato
            contato = Contato.objects.create(
                nome=nome,
                email=email,
                telefone=telefone,
                assunto=assunto,
                mensagem=mensagem,
            )

            return JsonResponse(
                {"success": True, "message": "Votre message a été envoyé avec succès!"}
            )

        except Exception as e:
            return JsonResponse(
                {"success": False, "message": "Erreur lors de l'envoi du message."}
            )

    context = {
        "contato_info": {
            "telefone": "+33 07 69 27 37 76",
            "email": "admlopespeinture@gmail.com",
            "endereco": "275 chemin de la castellane, 31790 St Sauveur",
            "horario": "Lun-Ven: 8h-18h, Sam: 9h-17h",
        }
    }
    return render(request, "pages/contato.html", context)


def realisations(request):
    """View para a página de realizações/projetos"""
    try:
        # Buscar projetos do banco de dados (usando visible_site em vez de ativo)
        projetos = Projeto.objects.filter(visible_site=True).order_by("-date_creation")

        context = {
            "projetos": projetos,
        }

        return render(request, "pages/realisations.html", context)

    except Exception as e:
        # Log do erro
        print(f"Erro na view realisations: {e}")

        # Retornar página com contexto vazio em caso de erro
        context = {
            "projetos": [],
        }

        return render(request, "pages/realisations.html", context)


def nos_couleurs(request):
    """Página do catálogo de cores"""
    # Buscar todas as categorias ativas com suas cores
    categorias = CategoriaColor.objects.filter(ativo=True).prefetch_related("couleurs")

    context = {
        "categorias": categorias,
        "empresa": {
            "nome": "LOPES PEINTURE",
        },
    }
    return render(request, "pages/nos-couleurs.html", context)


def api_couleurs(request):
    """API para buscar cores via AJAX"""
    categoria_slug = request.GET.get("categoria", "all")
    search = request.GET.get("search", "").lower()

    # Base query
    couleurs = Couleur.objects.filter(disponible=True).select_related("categoria")

    # Filtrar por categoria
    if categoria_slug != "all":
        couleurs = couleurs.filter(categoria__slug=categoria_slug)

    # Filtrar por busca
    if search:
        couleurs = couleurs.filter(
            models.Q(nome__icontains=search)
            | models.Q(codigo__icontains=search)
            | models.Q(categoria__nome__icontains=search)
        )

    # Converter para JSON
    data = []
    for couleur in couleurs:
        data.append(
            {
                "name": couleur.nome,
                "code": couleur.codigo,
                "rgb": couleur.rgb_string,
                "hex": couleur.hex_color,
                "category": couleur.categoria.nome,
                "description": couleur.description,
                "popular": couleur.populaire,
            }
        )

    return JsonResponse({"couleurs": data})
