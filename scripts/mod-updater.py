import os
import requests
import platform

def update_mods():

    github_api_mods_url = "https://api.github.com/repos/clousck/Perukaland/contents/mods"

    user_os = os.getenv('USER') or os.getenv('USERNAME')

    if platform.system() == "Windows":
        mods_directory = os.path.join("C:/Users", user_os, "AppData/Roaming/.minecraft/mods")
    else:
        mods_directory = os.path.join("/home", user_os, ".minecraft", "mods")
    
    def download_mods():
        def download_mod(file_url, file_path):
            response = requests.get(file_url, stream=True)
            response.headers.get('content-length', 0)
            chunk_size = 1024
            with open(file_path, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)

        try: 
            response = requests.get(github_api_mods_url, timeout=5)
            if response.status_code == 200:
                files = response.json()
                github_mods = set()
                local_mods = set(os.listdir(mods_directory)) if os.path.exists(mods_directory) else set()

                os.makedirs(mods_directory, exist_ok=True)

                # Descargar o actualizar mods
                for file in files:
                    if file['type'] == 'file':
                        file_name = file['name']
                        file_url = file['download_url']
                        file_path = os.path.join(mods_directory, file_name)

                        github_mods.add(file_name)

                        if not os.path.exists(file_path):
                            print(f"Descargado: {file_name}")
                            download_mod(file_url, file_path)
                        else:
                            print(f"El archivo {file_name} ya existe, omitiendo descarga.")

                # Eliminar mods que no están en el repositorio
                mods_to_delete = local_mods - github_mods
                for mod in mods_to_delete:
                    mod_path = os.path.join(mods_directory, mod)
                    if os.path.isfile(mod_path):
                        os.remove(mod_path)
                        print(f"Eliminado: {mod}")

            else:
                print(f"Error al obtener la lista de archivos: {response.status_code}")
        except TimeoutError:
            print(f"Error al establecer la conexión con el servidor: {response.status_code}")
    
    download_mods()
    input("Presione enter para finalizar...")
    return True

update_mods()
