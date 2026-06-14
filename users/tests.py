from django.test import TestCase
from django.urls import reverse

from .models import (
    Categorias,
    DetallesVentas,
    Productos,
    Sucursales,
    Usuarios,
    Ventas,
)


class DetallesVentasSucursalFilterTests(TestCase):
    def setUp(self):
        self.sucursal_a = Sucursales.objects.create(nombre="Sucursal A", direccion="Dir A")
        self.sucursal_b = Sucursales.objects.create(nombre="Sucursal B", direccion="Dir B")

        self.usuario_a = Usuarios.objects.create(
            nombre_usuario="Ana",
            apellido="Pérez",
            fecha_nacimiento="1990-01-01",
            telefono="70000001",
            correo="ana@example.com",
            password="123456",
            ci="1000001",
            sucursal=self.sucursal_a,
        )
        self.usuario_b = Usuarios.objects.create(
            nombre_usuario="Luis",
            apellido="Gómez",
            fecha_nacimiento="1991-02-02",
            telefono="70000002",
            correo="luis@example.com",
            password="123456",
            ci="1000002",
            sucursal=self.sucursal_b,
        )

        self.categoria = Categorias.objects.create(nombre_categoria="Categoría Test")

        self.producto_a = Productos.objects.create(
            nombre_producto="Producto A",
            descripcion="Desc A",
            precio_compra=10,
            precio_unitario=12,
            precio_mayor=15,
            stock=5,
            categoria=self.categoria,
            codigo_producto="A-001",
            sucursal=self.sucursal_a,
        )
        self.producto_b = Productos.objects.create(
            nombre_producto="Producto B",
            descripcion="Desc B",
            precio_compra=20,
            precio_unitario=25,
            precio_mayor=30,
            stock=5,
            categoria=self.categoria,
            codigo_producto="B-001",
            sucursal=self.sucursal_b,
        )

        self.venta_a = Ventas.objects.create(
            usuario=self.usuario_a,
            sucursal=self.sucursal_a,
            total=12,
        )
        self.venta_b = Ventas.objects.create(
            usuario=self.usuario_b,
            sucursal=self.sucursal_b,
            total=25,
        )

        self.detalle_a = DetallesVentas.objects.create(
            venta=self.venta_a,
            producto=self.producto_a,
            cantidad=1,
            precio=12,
            subtotal=12,
            tipo_venta="unidad",
        )
        self.detalle_b = DetallesVentas.objects.create(
            venta=self.venta_b,
            producto=self.producto_b,
            cantidad=1,
            precio=25,
            subtotal=25,
            tipo_venta="unidad",
        )

    def test_lista_detalles_por_sucursal_del_usuario(self):
        url = reverse("detalles-ventas-por-sucursal", args=[self.sucursal_a.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], self.detalle_a.id)
