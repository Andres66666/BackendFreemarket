# views.py
from datetime import datetime
import pytz
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import json
from cloudinary.uploader import upload
import cloudinary.uploader

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
from django.shortcuts import get_object_or_404

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
    queryset = Productos.objects.all()
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
            data["categoria"] = Categorias.objects.get(id=categoria_id)
        except Categorias.DoesNotExist:
            return Response(
                {"error": "La categoría especificada no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 🔥 QUITADO TODO LO DE imagen_productos
        
        producto = Productos.objects.create(**data)
        return Response(
            ProductoSerializer(producto).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        data = request.data.copy()
        
        # 🔥 QUITADO TODO LO DE imagen_productos
        # if "imagen_productos" in request.FILES: ← ELIMINADO

        categoria_data = request.data.get("categoria")
        if isinstance(categoria_data, str):
            categoria_data = json.loads(categoria_data)

        if isinstance(categoria_data, dict) and "id" in categoria_data:
            instance.categoria_id = categoria_data["id"]
        elif categoria_data:
            instance.categoria_id = categoria_data

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
class VentasViewSet(viewsets.ModelViewSet):
    queryset = Ventas.objects.all()
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
    queryset = DetallesVentas.objects.all()
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


