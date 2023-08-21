# inventario-backend
Inventory System with E-commerce

## Project Status

En desarrollo

## Instalation

A continuación se detallan los pasos para configurar el proyecto en un entorno local.

```bash

# Requirements Backend
* python == 3.9.13

# Clonar el repositorio
git clone https://github.com/reyalexander/inventario-backend.git

# Navegar al directorio del proyecto
cd inventario-backend

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual Windows
venv/Scripts/activate

# Instalar dependencias
pip install -r requirements.txt

# Hacer las migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusario
python manage.py createsuperuser

# Ejemplo de cómo ejecutar el proyecto
python manage.py runserver


## Estructura del Proyecto
inventario-backend/
|-- clients/
|-- inventory/
|-- order/
|-- order_detail/
|-- products/
|-- providers/
|-- purchase/
|-- purchase_detail/
|-- user/
|-- .gitignore/
|-- manage.py
|-- README.md
|-- requirements.txt

```

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details