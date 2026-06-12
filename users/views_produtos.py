# views.py
from datetime import datetime
import cloudinary
import pytz
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import json

from .models import (
    Categorias,
    DetallesVentas,
    Efectivo,
    Productos,
    Usuarios,
    Ventas,
)
from .serializers import (
    CategoriaSerializer,
    DetallesVentasSerializer,
    EfectivoSerializer,
    ProductoSerializer,
    VentaSerializer,
)

""" seccion para las ventas  """


class CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Categorias.objects.all()
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
    queryset = Productos.objects.select_related("categoria").all()
    serializer_class = ProductoSerializer

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
        categoria_id = request.data.get("categoria")
        try:
            data["categoria"] = Categorias.objects.get(
                id=categoria_id
            )
        except Categorias.DoesNotExist:
            return Response(
                {"error": "La categoría especificada no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # ===================================
        # SUBIR IMAGEN
        # ===================================
        if "imagen_productos" in request.FILES:
            try:
                uploaded_image = cloudinary.uploader.upload(
                    request.FILES["imagen_productos"],
                    folder="productos"
                )
                data["imagen_productos"] = uploaded_image.get(
                    "secure_url"
                )
                data["imagen_public_id"] = uploaded_image.get(
                    "public_id"
                )
            except Exception as e:
                return Response(
                    {
                        "error": f"Error al subir imagen: {str(e)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        producto = Productos.objects.create(**data)
        return Response(
            ProductoSerializer(producto).data,
            status=status.HTTP_201_CREATED,
        )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        # ===================================
        # ACTUALIZAR IMAGEN
        # ===================================
        if "imagen_productos" in request.FILES:
            try:
                # Eliminar imagen anterior
                if instance.imagen_public_id:
                    cloudinary.uploader.destroy(
                        instance.imagen_public_id
                    )
                uploaded_image = cloudinary.uploader.upload(
                    request.FILES["imagen_productos"],
                    folder="productos"
                )
                data["imagen_productos"] = uploaded_image.get(
                    "secure_url"
                )
                data["imagen_public_id"] = uploaded_image.get(
                    "public_id"
                )
            except Exception as e:
                return Response(
                    {
                        "error": f"Error al actualizar imagen: {str(e)}"
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
        # ===================================
        # CATEGORIA
        # ===================================
        categoria_data = request.data.get("categoria")
        if categoria_data:
            try:
                if isinstance(categoria_data, str):
                    try:
                        categoria_data = json.loads(categoria_data)

                    except:
                        pass
                if (
                    isinstance(categoria_data, dict)
                    and "id" in categoria_data
                ):

                    data["categoria"] = categoria_data["id"]
                else:
                    data["categoria"] = categoria_data
            except Exception:
                return Response(
                    {"error": "Categoría inválida"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        serializer = self.get_serializer(
            instance,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class VentasViewSet(viewsets.ModelViewSet):
    queryset = Ventas.objects.select_related("usuario").all()
    serializer_class = VentaSerializer

    def create(self, request, *args, **kwargs):
        usuario_data = request.data.get("usuario")

        if isinstance(usuario_data, dict) and "id" in usuario_data:
            usuario_id = usuario_data["id"]
        else:
            usuario_id = usuario_data  # Asumir que es un ID

        try:
            usuario = Usuarios.objects.get(id=usuario_id)
        except Usuarios.DoesNotExist:
            return Response(
                {"error": "El usuario especificado no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        local_tz = pytz.timezone("America/La_Paz")  # Zona horaria de Bolivia
        fecha_venta = datetime.now(local_tz)  # Obtener la hora local directamente

        data = {
            "usuario": usuario,
            "estado": request.data.get("estado", "Pendiente"),
            "total": request.data.get(
                "total", 0.00
            ),  # Asegúrate de que el total tenga un valor por defecto
            "fecha_venta": fecha_venta,  # Este campo se manejará automáticamente en el modelo
        }
        venta = Ventas.objects.create(**data)

        return Response(VentaSerializer(venta).data, status=status.HTTP_201_CREATED)
        
class DetallesVentasViewSet(viewsets.ModelViewSet):
    queryset = DetallesVentas.objects.select_related("producto__categoria", "venta__usuario").all()
    serializer_class = DetallesVentasSerializer

    def create(self, request, *args, **kwargs):
        print("🔥 DATOS RECIBIDOS:", request.data)
        
        data = request.data.copy()
        print("🔄 DATOS FINALES:", data)
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            detalle = serializer.save()
            print("✅ CREADO!")
            return Response(serializer.data, status=201)
        
        print("❌ ERRORES:", serializer.errors)
        return Response(serializer.errors, status=400)



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


