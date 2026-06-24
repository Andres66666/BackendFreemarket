# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views_usuarios, views_produtos


# Crea un router y registra tus ViewSets
router = DefaultRouter()
router.register(r"permisos", views_usuarios.PermisosViewSet)
router.register(r"roles", views_usuarios.RolesViewSet)
router.register(r"usuarios", views_usuarios.UsuariosViewSet)
router.register(r"usuariosroles", views_usuarios.UsuariosRolesViewSet)
router.register(r"rolespermisos", views_usuarios.RolesPermisosViewSet)

# rutas de ventas
router.register(r"categorias", views_produtos.CategoriasViewSet)
router.register(r"productos", views_produtos.ProductosViewSet)
router.register(r"ventas", views_produtos.VentasViewSet)
router.register(r"detallesventas", views_produtos.DetallesVentasViewSet)

# rutas de nuevas tablas
router.register(r"efectivo", views_produtos.EfectivoViewSet)

router.register(r"sucursales", views_usuarios.SucursalesViewSet)

# rutas de creditos
router.register(r"clientes",  views_usuarios.ClientesViewSet)
router.register(r"creditos",  views_usuarios.CreditosViewSet)
router.register(r"pagoscredito",  views_usuarios.PagosCreditoViewSet)
router.register(r"reciboscredito",  views_usuarios.RecibosCreditoViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("login/", views_usuarios.LoginView.as_view(), name="login"),
    path('productos/sucursal/<int:sucursal_id>/', views_produtos.productos_por_sucursal, name='productos-por-sucursal'),
    path(
        'ventas/sucursal/<int:sucursal_id>/',
        views_produtos.ventas_por_sucursal,
        name='ventas-por-sucursal',
    ),
    path(
        'detallesventas/sucursal/<int:sucursal_id>/',
        views_produtos.detalles_ventas_por_sucursal,
        name='detalles-ventas-por-sucursal',
    ),
    path(
        "clientes/buscar/<str:ci>/",
        views_usuarios.buscar_cliente_ci,
        name="buscar_cliente_ci",
    ),
]
