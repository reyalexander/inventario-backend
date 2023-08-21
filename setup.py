import os
from cx_Freeze import setup, Executable

# Ruta a la carpeta de tu proyecto Django
project_dir = os.path.dirname(os.path.abspath(__file__))

# Otras rutas importantes dentro de tu proyecto
manage_path = os.path.join(project_dir, 'manage.py')
static_path = os.path.join(project_dir, 'static')

# Configuración de cx_Freeze
setup(
    name="MyDjangoApp",
    version="1.0",
    description="My Django App",
    options={
        "build_exe": {
            "packages": ["django"],
            "include_files": [
                (manage_path, 'manage.py'),
                (static_path, 'static')
            ],
            "excludes": ['tkinter']  # Si no lo necesitas
        }
    },
    executables=[Executable("manage.py")]
)

