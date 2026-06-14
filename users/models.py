# models.py
from decimal import Decimal
from django.db import models
from django.contrib.auth.hashers import make_password

# Modelo de Roles
class Roles(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    estado_Rol = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_rol

# Modelo de Permisos
class Permisos(models.Model):
    nombre_permiso = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    estado_Permiso = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_permiso
class Sucursales(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
# Modelo de Usuarios
class Usuarios(models.Model):
    nombre_usuario = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=50, unique=True)
    correo = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)
    ci = models.CharField(max_length=20, unique=True)
    ci_departamento = models.CharField(max_length=2, default="EX")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado_Usuario = models.BooleanField(default=True)

    imagen_url = models.URLField(max_length=500, null=True, blank=True)
    imagen_public_id = models.CharField(max_length=255, null=True, blank=True)  
    sucursal = models.ForeignKey( Sucursales, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_usuario} {self.apellido}"

# Modelo de Roles de Usuarios
class UsuariosRoles(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("usuario", "rol")

    def __str__(self):
        return f"{self.usuario} {self.rol} "

# Modelo de Roles y Permisos
class RolesPermisos(models.Model):
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permisos, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("rol", "permiso")

    def __str__(self):
        return f"{self.rol} {self.permiso} "


""" seccion de ventas para un rol especifico  """


# Modelo de Categorías
class Categorias(models.Model):
    nombre_categoria = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    estado_categoria = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_categoria


# Modelo de Productos
class Productos(models.Model):
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_mayor = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    codigo_producto = models.CharField(max_length=50,)
    imagen_productos = models.URLField(max_length=500, null=True, blank=True)
    imagen_public_id = models.CharField(max_length=255, null=True, blank=True)  
    estado_equipo = models.BooleanField(default=True)
    
    sucursal = models.ForeignKey(Sucursales, on_delete=models.PROTECT, null=True,blank=True)

    class Meta:
        unique_together = (
            "codigo_producto",
            "sucursal"
        )
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre_producto"]

    def __str__(self):
        return f"{self.nombre_producto} ({self.codigo_producto})"


# Modelo de Ventas
class Ventas(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursales,on_delete=models.PROTECT, null=True, blank=True)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default="Completada") 
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"Venta #{self.id} realizada por {self.usuario}"


# Modelo de Detalles de Ventas
class DetallesVentas(models.Model):
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE)
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tipo_venta = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        if self.cantidad > self.producto.stock:
            raise ValueError(
                f"No hay suficiente stock para {self.producto.nombre_producto}"
            )
        self.producto.stock -= self.cantidad
        self.producto.save()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Detalle de {self.cantidad} {self.producto.nombre_producto} en la venta {self.venta.id}"




class Efectivo(models.Model):
    B200Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    B100Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    B50Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    B20Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    B10Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    M5Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    M2Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    M1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    M0_50Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    M0_20Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    M0_10Bs = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total = (
            self.B200Bs
            + self.B100Bs
            + self.B50Bs
            + self.B20Bs
            + self.B10Bs
            + self.M5Bs
            + self.M2Bs
            + self.M1
            + self.M0_50Bs
            + self.M0_20Bs
            + self.M0_10Bs
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Efectivo {self.total} Bs - {self.fecha_creacion.date()}"

