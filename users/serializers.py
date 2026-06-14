# serializers
from rest_framework import serializers
from .models import (
    Categorias,
    DetallesVentas,
    Efectivo,
    Productos,
    Sucursales,
    Usuarios,
    Roles,
    Permisos,
    UsuariosRoles,
    RolesPermisos,
    Ventas,
)


class LoginSerializer(serializers.Serializer):
    correo = serializers.EmailField(max_length=100, required=False, allow_null=True)
    password = serializers.CharField(max_length=255, required=True)

class SucursalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursales
        fields = "__all__"

class UsuarioSerializer(serializers.ModelSerializer):
    sucursal = SucursalesSerializer(read_only=True)
    sucursal_id = serializers.PrimaryKeyRelatedField(
            queryset=Sucursales.objects.all(),
            source="sucursal",
            write_only=True,
            required=False
        )
    class Meta:
        model = Usuarios
        exclude = ["password"]


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = "__all__"


class PermisosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permisos
        fields = "__all__"

class UsuariosRolesSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    rol = RolSerializer(read_only=True)
    

    class Meta:
        model = UsuariosRoles
        fields = "__all__"


class RolesPermisosSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    permiso = PermisosSerializer(read_only=True)

    class Meta:
        model = RolesPermisos
        fields = "__all__"


""" seccion de ventas tienda """


# Serializers para la sección de ventas
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = "__all__"


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    sucursal = SucursalesSerializer(read_only=True)
    sucursal_id = serializers.PrimaryKeyRelatedField(
            queryset=Sucursales.objects.all(),
            source="sucursal",
            write_only=True,
            required=False
        )
    class Meta:
        model = Productos
        fields = "__all__"


class VentaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    sucursal = SucursalesSerializer(read_only=True)

    class Meta:
        model = Ventas
        fields = "__all__"


class VentaListSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()
    sucursal = serializers.SerializerMethodField()

    class Meta:
        model = Ventas
        fields = ["id", "usuario", "sucursal", "fecha_venta", "estado", "total"]

    def get_usuario(self, obj):
        return {
            "id": obj.usuario_id,
            "nombre_usuario": obj.usuario.nombre_usuario,
            "apellido": obj.usuario.apellido,
        }

    def get_sucursal(self, obj):
        return {
            "id": obj.sucursal_id,
            "nombre": obj.sucursal.nombre if obj.sucursal else None,
        }


class DetallesVentasSerializer(serializers.ModelSerializer):
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Productos.objects.all(),
        source='producto',
        write_only=True
    )
    venta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ventas.objects.all(),
        source='venta',
        write_only=True
    )
    producto = ProductoSerializer(read_only=True)
    venta = VentaSerializer(read_only=True) 
    class Meta:
        model = DetallesVentas
        fields = "__all__"


class DetalleVentaListSerializer(serializers.ModelSerializer):
    producto = serializers.SerializerMethodField()
    venta = serializers.SerializerMethodField()

    class Meta:
        model = DetallesVentas
        fields = ["id", "producto", "venta", "cantidad", "precio", "subtotal", "tipo_venta"]

    def get_producto(self, obj):
        categoria = None
        if obj.producto.categoria_id:
            categoria = {
                "id": obj.producto.categoria_id,
                "nombre_categoria": obj.producto.categoria.nombre_categoria,
            }

        return {
            "id": obj.producto_id,
            "nombre_producto": obj.producto.nombre_producto,
            "codigo_producto": obj.producto.codigo_producto,
            "categoria": categoria,
            "precio_compra": obj.producto.precio_compra,
            "precio_unitario": obj.producto.precio_unitario,
            "precio_mayor": obj.producto.precio_mayor,
        }

    def get_venta(self, obj):
        return {
            "id": obj.venta_id,
            "fecha_venta": obj.venta.fecha_venta,
            "estado": obj.venta.estado,
            "usuario": {
                "id": obj.venta.usuario_id,
                "nombre_usuario": obj.venta.usuario.nombre_usuario,
                "apellido": obj.venta.usuario.apellido,
                "ci": obj.venta.usuario.ci,
            },
        }

class EfectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Efectivo
        fields = "__all__"


