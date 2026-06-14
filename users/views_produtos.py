# views.py
from datetime import datetime
import cloudinary
import pytz
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

from .models import (
    Categorias,
    DetallesVentas,
    Efectivo,
    Productos,
    Sucursales,
    Usuarios,
    Ventas,
)
from .serializers import (
    CategoriaSerializer,
    DetalleVentaListSerializer,
    DetallesVentasSerializer,
    EfectivoSerializer,
    ProductoSerializer,
    VentaListSerializer,
    VentaSerializer,
)

""" seccion para las ventas  """


class CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Categorias.objects.filter(estado_categoria=True).order_by("nombre_categoria")
    serializer_class = CategoriaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_create(serializer)  # Guarda la nueva categoría
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Permite actualizaciones parciales
        instance = (
            self.get_object()
        )  # Obtiene la instancia de la categoría a actualizar
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_update(serializer)  # Actualiza la categoría
        return Response(serializer.data)

class ProductosViewSet(viewsets.ModelViewSet):
    queryset = (
        Productos.objects.select_related("categoria", "sucursal")
        .filter(estado_equipo=True)
        .order_by("nombre_producto")
    )
    serializer_class = ProductoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        sucursal_id = self.request.query_params.get("sucursal_id")
        if sucursal_id:
            return queryset.filter(sucursal_id=sucursal_id)

        return queryset

    # =====================================
    # CREAR PRODUCTO
    # =====================================
    def create(self, request, *args, **kwargs):

        data = {
            "nombre_producto": request.data.get("nombre_producto"),
            "descripcion": request.data.get("descripcion"),
            "precio_compra": request.data.get("precio_compra"),
            "precio_unitario": request.data.get("precio_unitario"),
            "precio_mayor": request.data.get("precio_mayor"),
            "stock": request.data.get("stock"),
            "codigo_producto": request.data.get("codigo_producto"),
        }

        # ==========================
        # CATEGORIA
        # ==========================
        categoria_id = request.data.get("categoria")
        try:
            data["categoria"] = Categorias.objects.get(
                id=categoria_id
            )
        except Categorias.DoesNotExist:
            return Response(
                {
                    "error": (
                        "La categoría especificada "
                        "no existe."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # ==========================
        # SUCURSAL
        # ==========================
        sucursal_id = request.data.get("sucursal_id")
        if sucursal_id:
            try:
                data["sucursal"] = (
                    Sucursales.objects.get(
                        id=sucursal_id
                    )
                )
            except Sucursales.DoesNotExist:
                return Response(
                    {
                        "error": (
                            "La sucursal especificada "
                            "no existe."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # ==========================
        # IMAGEN
        # ==========================
        if "imagen_productos" in request.FILES:
            try:
                uploaded_image = (
                    cloudinary.uploader.upload(
                        request.FILES[
                            "imagen_productos"
                        ],
                        folder="productos",
                    )
                )
                data["imagen_productos"] = (
                    uploaded_image.get(
                        "secure_url"
                    )
                )
                data["imagen_public_id"] = (
                    uploaded_image.get(
                        "public_id"
                    )
                )
            except Exception as e:
                return Response(
                    {
                        "error": (
                            f"Error al subir imagen: "
                            f"{str(e)}"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:
            producto = Productos.objects.create(**data)

            return Response(
                ProductoSerializer(producto).data,
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            print("ERROR PRODUCTO:", str(e))

            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
    # =====================================
    # EDITAR PRODUCTO
    # =====================================
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        # ==========================
        # IMAGEN
        # ==========================
        if "imagen_productos" in request.FILES:
            try:
                if instance.imagen_public_id:
                    cloudinary.uploader.destroy(
                        instance.imagen_public_id
                    )
                uploaded_image = (
                    cloudinary.uploader.upload(
                        request.FILES[
                            "imagen_productos"
                        ],
                        folder="productos",
                    )
                )
                data["imagen_productos"] = (
                    uploaded_image.get(
                        "secure_url"
                    )
                )
                data["imagen_public_id"] = (
                    uploaded_image.get(
                        "public_id"
                    )
                )
            except Exception as e:
                return Response(
                    {
                        "error": (
                            f"Error al actualizar "
                            f"imagen: {str(e)}"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            data["imagen_productos"] = (
                instance.imagen_productos
            )
            data["imagen_public_id"] = (
                instance.imagen_public_id
            )
        # ==========================
        # CATEGORIA
        # ==========================
        categoria_data = request.data.get(
            "categoria"
        )
        if categoria_data:
            try:
                if isinstance(
                    categoria_data,
                    str
                ):
                    try:
                        categoria_data = json.loads(
                            categoria_data
                        )
                    except:
                        pass
                if (isinstance(categoria_data, dict)
                    and "id"
                    in categoria_data
                ):
                    data["categoria"] = (
                        categoria_data["id"]
                    )
                else:
                    data["categoria"] = (
                        categoria_data
                    )
            except Exception:
                return Response(
                    {
                        "error":
                        "Categoría inválida"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # ==========================
        # SUCURSAL
        # ==========================
        sucursal_id = request.data.get(
            "sucursal_id"
        )
        if sucursal_id:
            try:
                Sucursales.objects.get(
                    id=sucursal_id
                )
                data["sucursal"] = (sucursal_id)
            except Sucursales.DoesNotExist:
                return Response(
                    {"error":"Sucursal inválida"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # ==========================
        # GUARDAR
        # ==========================
        serializer = self.get_serializer(instance,data=data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VentasViewSet(viewsets.ModelViewSet):
    queryset = Ventas.objects.select_related("usuario", "sucursal").all().order_by("-id")
    serializer_class = VentaSerializer

    def create(self, request, *args, **kwargs):
        usuario_data = request.data.get("usuario")

        if isinstance(usuario_data, dict) and "id" in usuario_data:
            usuario_id = usuario_data["id"]
        else:
            usuario_id = usuario_data

        try:
            usuario = Usuarios.objects.select_related(
                "sucursal"
            ).get(id=usuario_id)

        except Usuarios.DoesNotExist:
            return Response(
                {"error": "El usuario especificado no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        local_tz = pytz.timezone("America/La_Paz")
        fecha_venta = datetime.now(local_tz)

        data = {
            "usuario": usuario,
            "sucursal": usuario.sucursal,  # ← NUEVO
            "estado": request.data.get(
                "estado",
                "Completada"
            ),
            "total": request.data.get(
                "total",
                0.00
            ),
            "fecha_venta": fecha_venta,
        }

        venta = Ventas.objects.create(**data)

        return Response(
            VentaSerializer(venta).data,
            status=status.HTTP_201_CREATED
        )


@api_view(["GET"])
def productos_por_sucursal(request, sucursal_id=None):
    sucursal_id = sucursal_id or request.query_params.get("sucursal_id")
    if not sucursal_id:
        return Response(
            {"error": "Se requiere el identificador de la sucursal."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    productos = (
        Productos.objects.select_related("categoria", "sucursal")
        .filter(sucursal_id=sucursal_id, estado_equipo=True)
        .order_by("nombre_producto")
    )
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data)


# views.py



@api_view(['GET'])
def ventas_por_sucursal(request, sucursal_id):

    ventas = (
        Ventas.objects
        .select_related('usuario', 'sucursal')
        .only(
            'id',
            'usuario_id',
            'sucursal_id',
            'fecha_venta',
            'estado',
            'total',
            'usuario__nombre_usuario',
            'usuario__apellido',
            'sucursal__nombre',
        )
        .filter(sucursal_id=sucursal_id)
        .order_by('-fecha_venta')
    )

    serializer = VentaListSerializer(ventas, many=True)

    return Response(serializer.data)



class DetallesVentasViewSet(viewsets.ModelViewSet):
    queryset = (
        DetallesVentas.objects.select_related(
            "producto__categoria",
            "producto__sucursal",
            "venta__usuario",
            "venta__sucursal",
        )
        .all()
        .order_by("-id")
    )
    serializer_class = DetallesVentasSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
def detalles_ventas_por_sucursal(request, sucursal_id):
    detalles = (
        DetallesVentas.objects.select_related(
            "producto__categoria",
            "venta__usuario",
        )
        .only(
            "id",
            "cantidad",
            "precio",
            "subtotal",
            "tipo_venta",
            "producto_id",
            "producto__nombre_producto",
            "producto__codigo_producto",
            "producto__categoria_id",
            "producto__precio_compra",
            "producto__precio_unitario",
            "producto__precio_mayor",
            "venta_id",
            "venta__fecha_venta",
            "venta__estado",
            "venta__usuario_id",
            "venta__usuario__nombre_usuario",
            "venta__usuario__apellido",
            "venta__usuario__ci",
        )
        .filter(venta__sucursal_id=sucursal_id)
        .order_by("-venta__fecha_venta", "-id")
    )

    serializer = DetalleVentaListSerializer(detalles, many=True)
    return Response(serializer.data)


class EfectivoViewSet(viewsets.ModelViewSet):
    queryset = Efectivo.objects.all()
    serializer_class = EfectivoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


