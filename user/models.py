from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
# Create your models here.

class UserManager(BaseUserManager):
    '''Interfaz que proporcionan las operaciones de consulta de la base de datos para Usuarios'''
    def create_user(self, email, first_name, password = None):
        '''función para crear usuarios'''
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
                email=self.normalize_email(email),
                first_name=first_name,
            )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, password):
        '''función para crear un super usuario (comando: createsuperuser)'''
        user = self.create_user(
                email=email,
                password=password,
                first_name=first_name,
            )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
    

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(blank=False,unique=True,max_length=40) 
    first_name = models.CharField(blank=False,max_length=40)
    last_name = models.CharField(blank=False,max_length=40)
    address = models.CharField(blank=False,max_length=100)
    phone = models.CharField(blank=False,max_length=12)
    ruc = models.CharField(blank=False,max_length=11)
    igv = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    photo = models.ImageField(upload_to="user_photo",null=True,blank=True, default='https://w7.pngwing.com/pngs/81/570/png-transparent-profile-logo-computer-icons-user-user-blue-heroes-logo.png')
    is_admin = models.BooleanField(default=False,verbose_name='super administrador')
    # estado de super administrador del usuario
    is_active = models.BooleanField(default=True,verbose_name='estado')
    # estado del usuario
    is_superuser = models.BooleanField(default=False,verbose_name='super usuario')
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        ordering = ['first_name']


