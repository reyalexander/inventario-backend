import os
import shutil


def eliminar_carpetas():
    # Ruta a la carpeta 'apps' dentro de tu proyecto Django
    ruta_apps = ".\\apps"

    # Carpetas a eliminar
    carpetas_eliminar = ["__pycache__", "migrations"]

    # Iterar sobre cada subcarpeta dentro de 'apps'
    for subcarpeta in os.listdir(ruta_apps):
        ruta_subcarpeta = os.path.join(ruta_apps, subcarpeta)
        if os.path.isdir(ruta_subcarpeta):
            for carpeta in carpetas_eliminar:
                ruta_carpeta = os.path.join(ruta_subcarpeta, carpeta)
                if os.path.exists(ruta_carpeta):
                    shutil.rmtree(ruta_carpeta)
                    print(f"Se ha eliminado la carpeta {carpeta} en {subcarpeta}")
                else:
                    print(f"La carpeta {carpeta} no existe en {subcarpeta}")


if __name__ == "__main__":
    eliminar_carpetas()