import os
import requests

def update_launcher():

    github_api_mods_url = "https://api.github.com/repos/clousck/Perukalauncher/contents/resources/mods"
    
    def download_mods():
        def download_mod(file_url, file_path):
            response = requests.get(file_url, stream=True)
            response.headers.get('content-length', 0)
            chunk_size = 1024
            with open(file_path, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)

        response = requests.get(github_api_mods_url)
        if response.status_code == 200:
            files = response.json()
            downloaded_files = 0

            os.makedirs('./mods', exist_ok=True)

            for file in files:

                if file['type'] == 'file':
                    file_url = file['download_url']
                    file_name = file['name']
                    file_path = os.path.join('./mods', file_name)

                    downloaded_files += 1
                    if not os.path.exists(file_path):
                        print(f"Descargado: {file_name}")
                        download_mod(file_url, file_path)
                    else:
                        print(f"El archivo {file_name} ya existe, omitiendo descarga.")
        else:
            print(f"Error al obtener la lista de archivos: {response.status_code}")
    download_mods()
    return True

update_launcher()