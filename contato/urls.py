from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"contatos", views.ContatoViewSet)
router.register(r"pieces-jointes", views.PieceJointeViewSet)

urlpatterns = router.urls
