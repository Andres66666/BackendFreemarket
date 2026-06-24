# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.hashers import check_password
from django.db.models import Prefetch
from rest_framework_simplejwt.tokens import RefreshToken
import cloudinary.uploader


from .models import (
    Clientes,
    Creditos,
    PagosCredito,
    Permisos,
    Productos,
    RecibosCredito,
    Roles,
    Sucursales,
    Usuarios,
    RolesPermisos,
    UsuariosRoles,
)
from .serializers import (
    ClienteSerializer,
    CreditoListSerializer,
    CreditoSerializer,
    PagoCreditoSerializer,
    PermisosSerializer,
    ReciboCreditoSerializer,
    RolSerializer,
    RolesPermisosSerializer,
    SucursalesSerializer,
    UsuarioSerializer,
    LoginSerializer,
    UsuariosRolesSerializer,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

""" esto es la seccion de login """


# backend
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        correo = serializer.validated_data.get("correo")
        password = serializer.validated_data.get("password")

        try:
            usuario = Usuarios.objects.get(correo=correo)
        except Usuarios.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        if not usuario.estado_Usuario:
            return Response(
                {"error": "No puedes iniciar sesión!!!. Comuníquese con el administrador. Gracias."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not check_password(password, usuario.password):
            return Response(
                {"error": "Credenciales incorrectas"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(usuario)
        access_token = str(refresh.access_token)

        # Una sola query con JOIN, en vez de prefetch anidado
        roles_permisos = (
            RolesPermisos.objects
            .filter(rol__usuariosroles__usuario=usuario)
            .select_related("rol", "permiso")
        )

        roles = list({rp.rol.nombre_rol for rp in roles_permisos})
        permisos = list({rp.permiso.nombre_permiso for rp in roles_permisos})

        if not roles or not permisos:
            return Response(
                {"error": "El usuario no tiene roles ni permisos asignados."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "access_token": access_token,
                "roles": roles,
                "permisos": permisos,
                "nombre_usuario": usuario.nombre_usuario,
                "apellido": usuario.apellido,
                "imagen_url": usuario.imagen_url,
                "usuario_id": usuario.id,
                "sucursal_id": usuario.sucursal.id , # temporalmente node
                "sucursal_nombre": usuario.sucursal.nombre, # temporalmente node
            },
            status=status.HTTP_200_OK,
        )

# ViewSet for Permisos
class PermisosViewSet(viewsets.ModelViewSet):
    queryset = Permisos.objects.all()
    serializer_class = PermisosSerializer

    def create(self, request, *args, **kwargs):
        # Extraer datos del request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_create(serializer)  # Guarda el nuevo permiso
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Permite actualizaciones parciales
        instance = self.get_object()  # Obtiene la instancia del permiso a actualizar
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_update(serializer)  # Actualiza el permiso
        return Response(serializer.data)


# ViewSet for Roles
class RolesViewSet(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolSerializer

    def create(self, request, *args, **kwargs):
        # Extraer datos del request
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_create(serializer)  # Guarda el nuevo rol
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = True  # Permite actualizaciones parciales
        instance = self.get_object()  # Obtiene la instancia del rol a actualizar
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Valida los datos
        self.perform_update(serializer)  # Actualiza el rol
        return Response(serializer.data)


# ViewSet for Usuarios
class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if "imagen_url" in request.FILES:
            try:
                uploaded_image = cloudinary.uploader.upload(
                    request.FILES["imagen_url"],
                    folder="usuarios"
                )
                data["imagen_url"] = uploaded_image.get(
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
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        return Response(
            self.get_serializer(usuario).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        if "imagen_url" in request.FILES:
            try:
                if instance.imagen_public_id:
                    cloudinary.uploader.destroy(
                        instance.imagen_public_id
                    )
                uploaded_image = cloudinary.uploader.upload(
                    request.FILES["imagen_url"],
                    folder="usuarios"
                )
                data["imagen_url"] = uploaded_image.get(
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

            data["imagen_url"] = instance.imagen_url
            data["imagen_public_id"] = (
                instance.imagen_public_id
            )
        serializer = self.get_serializer(
            instance,
            data=data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ViewSet for UsuariosRoles
class UsuariosRolesViewSet(viewsets.ModelViewSet):
    queryset = UsuariosRoles.objects.all()
    serializer_class = UsuariosRolesSerializer

    def create(self, request, *args, **kwargs):
        usuario_id = request.data.get("usuario")
        rol_id = request.data.get("rol")

        if UsuariosRoles.objects.filter(usuario_id=usuario_id, rol_id=rol_id).exists():
            return Response(
                {"error": ["El usuario ya tiene este rol asignado"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario_rol = UsuariosRoles.objects.create(usuario_id=usuario_id, rol_id=rol_id)
        return Response(
            UsuariosRolesSerializer(usuario_rol).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        usuario_id = request.data.get("usuario", {}).get("id", instance.usuario_id)
        rol_id = request.data.get("rol", {}).get("id", instance.rol_id)

        if (
            UsuariosRoles.objects.filter(usuario_id=usuario_id, rol_id=rol_id)
            .exclude(pk=instance.pk)
            .exists()
        ):
            return Response(
                {"error": ["El usuario ya tiene este rol asignado"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.usuario_id = usuario_id
        instance.rol_id = rol_id
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ViewSet for RolesPermisos


class RolesPermisosViewSet(viewsets.ModelViewSet):
    queryset = RolesPermisos.objects.all()
    serializer_class = RolesPermisosSerializer

    def create(self, request, *args, **kwargs):
        rol_id = request.data.get("rol")
        permiso_id = request.data.get("permiso")

        # Verificar si ya existe la relación entre rol y permiso
        if RolesPermisos.objects.filter(rol_id=rol_id, permiso_id=permiso_id).exists():
            return Response(
                {"error": ["Este rol ya tiene este permiso asignado"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crear la relación
        roles_permisos = RolesPermisos.objects.create(
            rol_id=rol_id, permiso_id=permiso_id
        )
        return Response(
            RolesPermisosSerializer(roles_permisos).data, status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        rol_id = request.data.get("rol", {}).get("id", instance.rol_id)
        permiso_id = request.data.get("permiso", {}).get("id", instance.permiso_id)

        # Verificar si ya existe la relación entre rol y permiso, excluyendo la instancia actual
        if (
            RolesPermisos.objects.filter(rol_id=rol_id, permiso_id=permiso_id)
            .exclude(pk=instance.pk)
            .exists()
        ):
            return Response(
                {"error": ["Este rol ya tiene este permiso asignado"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Actualizar la relación
        instance.rol_id = rol_id
        instance.permiso_id = permiso_id
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class SucursalesViewSet(viewsets.ModelViewSet):
    queryset = Sucursales.objects.all()
    serializer_class = SucursalesSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sucursal = serializer.save()
        return Response(
            self.get_serializer(sucursal).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
""" nueva seccion  """

class ClientesViewSet(viewsets.ModelViewSet):

    queryset = Clientes.objects.all().order_by("nombre")
    serializer_class = ClienteSerializer

    def create(self, request, *args, **kwargs):

        ci = request.data.get("ci")

        if Clientes.objects.filter(ci=ci).exists():

            return Response(
                {
                    "error":
                    "Ya existe un cliente con ese CI"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        cliente = serializer.save()

        return Response(
            self.get_serializer(cliente).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    

class CreditosViewSet(viewsets.ModelViewSet):

    queryset = (
        Creditos.objects
        .select_related(
            "cliente",
            "producto",
            "usuario"
        )
        .all()
        .order_by("-id")
    )

    serializer_class = CreditoSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return CreditoListSerializer
        return CreditoSerializer

    def create(self, request, *args, **kwargs):

        producto_id = request.data.get("producto_id")
        cuotas = int(request.data.get("cantidad_cuotas"))

        try:
            producto = Productos.objects.get(
                id=producto_id
            )

        except Productos.DoesNotExist:

            return Response(
                {"error": "Producto no encontrado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        precio_total = producto.precio_unitario
        cuota_mensual = precio_total / cuotas

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        credito = serializer.save(
            precio_total=precio_total,
            cuota_mensual=cuota_mensual,
            saldo_pendiente=precio_total,
            estado="PAGANDO"
        )

        return Response(
            CreditoSerializer(credito).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
class PagosCreditoViewSet(viewsets.ModelViewSet):

    queryset = (
        PagosCredito.objects
        .select_related(
            "credito",
            "credito__cliente",
            "credito__producto"
        )
        .all()
        .order_by("-id")
    )

    serializer_class = PagoCreditoSerializer

    def create(self, request, *args, **kwargs):

        credito_id = request.data.get("credito_id")

        try:
            credito = Creditos.objects.select_related(
                "producto"
            ).get(id=credito_id)

        except Creditos.DoesNotExist:
            return Response(
                {"error": "Crédito no encontrado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

  
        if PagosCredito.objects.filter(credito=credito).count() >= credito.cantidad_cuotas:
            return Response(
                {"error": "Ya se alcanzó el número máximo de cuotas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if credito.estado == "PAGADO":
            return Response(
                {"error": "El crédito ya fue cancelado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pago = serializer.save()

        credito.cuotas_pagadas += 1
        credito.saldo_pendiente -= pago.monto_pagado

        if credito.saldo_pendiente <= 0:
            credito.saldo_pendiente = Decimal("0.00")
            credito.estado = "PAGADO"

            if not credito.stock_descontado:
                producto = credito.producto
                if producto.stock > 0:
                    producto.stock -= 1
                    producto.save()

                credito.stock_descontado = True

        credito.save()

        return Response(
            PagoCreditoSerializer(pago).data,
            status=status.HTTP_201_CREATED,
        )

class RecibosCreditoViewSet(viewsets.ModelViewSet):

    queryset = (
        RecibosCredito.objects
        .select_related(
            "pago",
            "pago__credito",
            "pago__credito__cliente"
        )
        .all()
        .order_by("-id")
    )

    serializer_class = ReciboCreditoSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        recibo = serializer.save()

        return Response(
            self.get_serializer(recibo).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
@api_view(["GET"])
def buscar_cliente_ci(request, ci):

    try:
        cliente = Clientes.objects.get(ci=ci)

        serializer = ClienteSerializer(cliente)

        return Response(serializer.data)

    except Clientes.DoesNotExist:

        return Response(
            {"error": "Cliente no encontrado"},
            status=status.HTTP_404_NOT_FOUND
        )