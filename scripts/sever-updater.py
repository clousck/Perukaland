import os
import requests

def update_launcher():

    github_api_mods_url = "https://api.github.com/repos/clousck/Perukaland/contents/mods"
    github_api_plugins_url = "https://api.github.com/repos/clousck/Perukaland/contents/plugins"

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
            repo_mod_files = [file['name'] for file in files if file['type'] == 'file']

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
                        print(f"El mod {file_name} ya existe, omitiendo descarga.")

            local_mod_files = os.listdir('./mods')
            for local_mod in local_mod_files:
                if local_mod not in repo_mod_files:
                    local_mod_path = os.path.join('./mods', local_mod)
                    os.remove(local_mod_path)
                    print(f"Eliminado mod local: {local_mod}")

        else:
            print(f"Error al obtener la lista de archivos: {response.status_code}")
    
    def download_plugins():
        def download_plugin(file_url, file_path):
            response = requests.get(file_url, stream=True)
            response.headers.get('content-length', 0)
            chunk_size = 1024
            with open(file_path, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)

        response = requests.get(github_api_plugins_url)
        if response.status_code == 200:
            files = response.json()
            downloaded_files = 0

            os.makedirs('./plugins', exist_ok=True)
            repo_plugin_files = [file['name'] for file in files if file['type'] == 'file']

            for file in files:

                if file['type'] == 'file':
                    file_url = file['download_url']
                    file_name = file['name']
                    file_path = os.path.join('./plugins', file_name)

                    downloaded_files += 1
                    if not os.path.exists(file_path):
                        print(f"Descargado: {file_name}")
                        download_plugin(file_url, file_path)
                    else:
                        print(f"El plugin {file_name} ya existe, omitiendo descarga.")

            local_plugin_files = os.listdir('./plugins')
            for local_plugin in local_plugin_files:
                if local_plugin not in repo_plugin_files:
                    local_plugin_path = os.path.join('./plugins', local_plugin)
                    os.remove(local_plugin_path)
                    print(f"Eliminado plugin local: {local_plugin}")

        else:
            print(f"Error al obtener la lista de archivos: {response.status_code}")

    download_mods()
    download_plugins()
    return True

update_launcher()
