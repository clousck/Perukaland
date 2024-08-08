import subprocess
import minecraft_launcher_lib
import tkinter as tk
import json
import os
import platform
import requests
import threading

def check_installation():
    if deserialize_verifier() == None:
        if len(versions) == 2:
            serialize_verifier()
            return True

        def accept():
            nonlocal approval
            approval = True
            app.destroy()
        def decline():
            nonlocal approval
            approval = False
            app.destroy()

        approval = False

        app = tk.Tk()
        app.title("Approval")
        app.geometry("300x100")

        label = tk.Label(app, text="Se instalará el launcher en:\n"+minecraft_directory)
        label.pack(pady=5)

        # Botón Aceptar
        accept_button = tk.Button(app, text="Aceptar", command=accept)
        accept_button.pack(side=tk.RIGHT, padx=40)

        # Botón Cancelar
        decline_button = tk.Button(app, text="Cancelar", command=decline)
        decline_button.pack(side=tk.LEFT, padx=40)
        app.mainloop()

        if approval:
            minecraft_version = minecraft_launcher_lib.forge.find_forge_version("1.20.1")

            app = tk.Tk()
            app.title("Status")
            label = tk.Label(app, text="Descargando e instalando Minecraft Forge 1.20.1\n(Esto puede tardar varios minutos)")
            label.pack(pady=5)
            app.geometry("400x150")

            file_label = tk.Label(app, text="")
            file_label.pack(pady=5)

            progress_label = tk.Label(app, text="")
            progress_label.pack(pady=5)

            app.update()
            
            current_max = 0

            def set_status(status: str):
                print(status)
                file_label.config(text=status)
                app.update()

            def set_progress(progress: int):
                global current_max
                print(f"{progress}/{current_max}")
                progress_label.config(text=f"{progress}/{current_max}")
                app.update()

            def set_max(new_max: int):
                global current_max
                current_max = new_max

            callback = {
                "setStatus": set_status,
                "setProgress": set_progress,
                "setMax": set_max
            }

            minecraft_launcher_lib.forge.install_forge_version(minecraft_version, minecraft_directory, callback=callback)
            
            app.destroy()
            update_launcher()
            serialize_verifier()
            return True
        return False
    else:
        return True

def update_launcher():
    app = tk.Tk()
    app.title("Status")
    app.geometry("400x130")

    status_label = tk.Label(app, text="Descargando e instalando recursos\n(Esto puede tardar varios minutos)")
    status_label.pack(pady=5)

    file_label = tk.Label(app, text="")
    file_label.pack(pady=5)

    progress_label = tk.Label(app, text="")
    progress_label.pack(pady=5)

    cancel = False
    def cancel_update():
        nonlocal cancel
        cancel = True
        app.destroy()

    cancel_button = tk.Button(app, text="Cancelar", command=cancel_update)
    cancel_button.pack(pady=5)

    mods_directory = os.path.join(minecraft_directory, 'mods')
    os.makedirs(mods_directory, exist_ok=True)

    resourcepack_directory = os.path.join(minecraft_directory, 'resourcepacks')
    os.makedirs(resourcepack_directory, exist_ok=True)

    resourcepack_directory = os.path.join(minecraft_directory, 'servers')
    os.makedirs(resourcepack_directory, exist_ok=True)

    github_api_mods_url = "https://api.github.com/repos/clousck/Perukalauncher/contents/resources/mods"
    github_api_resourcepack_url = "https://api.github.com/repos/clousck/Perukalauncher/contents/resources/resourcepack"
    github_api_serverconfig_url = "https://api.github.com/repos/clousck/Perukalauncher/contents/resources/server"
    
    def download_mods():
        def download_mod(file_url, file_path):
            response = requests.get(file_url, stream=True)
            response.headers.get('content-length', 0)
            chunk_size = 1024
            with open(file_path, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)

        nonlocal cancel
        response = requests.get(github_api_mods_url)
        if response.status_code == 200:
            files = response.json()
            total_files = len(files)
            downloaded_files = 0

            for file in files:
                if cancel:
                    break

                if file['type'] == 'file':
                    file_url = file['download_url']
                    file_name = file['name']
                    file_path = os.path.join(mods_directory, file_name)

                    downloaded_files += 1
                    if not os.path.exists(file_path):
                        file_label.config(text=f"{file_name}")
                        progress_label.config(text=f"Descargando {downloaded_files}/{total_files}")
                        print(f"Descargado: {file_name}")
                        download_mod(file_url, file_path)
                        app.update_idletasks()
                    else:
                        print(f"El archivo {file_name} ya existe, omitiendo descarga.")
                        progress_label.config(text=f"Omite {downloaded_files}/{total_files}")
        else:
            print(f"Error al obtener la lista de archivos: {response.status_code}")
        download_resourcepack()

    def download_resourcepack():
        nonlocal cancel
        response = requests.get(github_api_resourcepack_url)
        if response.status_code == 200:
            files = response.json()
            total_files = len(files)
            downloaded_files = 0

            file = files[0]

            if file['type'] == 'file' and not cancel:
                file_url = file['download_url']
                file_name = 'Perukapack'
                file_path = os.path.join(resourcepack_directory, file_name)

                downloaded_files += 1
                
                file_label.config(text=f"{file_name}")
                progress_label.config(text=f"Descargando {downloaded_files}/{total_files}")
                print(f"Descargado: {file_name}")
                
                response = requests.get(file_url, stream=True)
                response.headers.get('content-length', 0)
                chunk_size = 1024
                with open(file_path, 'wb') as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)

                app.update_idletasks()
        else:
            print(f"Error al obtener resourcepack: {response.status_code}")
        app.destroy()

    #Use different threads to use cancel button and download process
    download_thread = threading.Thread(target=download_mods)
    download_thread.start()

    app.mainloop()
    return True

def setup_config(options):
    def set_name():
        if(len(entry.get()) > 0):
            options['username'] = entry.get()
            app.destroy()
    
    if options['username'] == "":
        app = tk.Tk()
        app.title("Username")
        app.geometry("300x100")

        label = tk.Label(app, text="Enter your username:")
        label.pack(pady=5)

        entry = tk.Entry(app)
        entry.pack(pady=5)

        submit_button = tk.Button(app, text="Submit", command=set_name)
        submit_button.pack(pady=5)
        app.mainloop()

def serialize_options():
    with open(os.path.join(minecraft_directory, 'options.json'), 'w') as f:
        json.dump(options, f)
def deserialize_options():
    try:
        with open(os.path.join(minecraft_directory, 'options.json'), 'r') as f:
            options = json.load(f)
            return options
    except FileNotFoundError:
        options = {
            'username': '',
            'uuid': '',
            'token': ''
        }
        return options
    
def serialize_verifier():
    with open(os.path.join(minecraft_directory, 'verifier.json'), 'w') as f:
        json.dump({}, f)
def deserialize_verifier():
    try:
        with open(os.path.join(minecraft_directory, 'verifier.json'), 'r') as f:
            options = json.load(f)
            return options
    except FileNotFoundError:
        return None

def show_gui():
    def close_window():
        app.destroy()

    def initialize_game():
        app.destroy()
        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(versions[1]["id"], minecraft_directory, options)
        #minecraft_command += ["--width", "1000", "--height", "1000"]
        subprocess.run(minecraft_command, cwd=minecraft_directory)

    def open_minecraft_directory():
        absolute_path = os.path.abspath(minecraft_directory)
        print(f"Abriendo el directorio: {absolute_path}")  # Verificar la ruta
        if os.name == 'nt':  # Para Windows
            subprocess.Popen(f'explorer "{absolute_path}"')
        elif os.name == 'posix':  # Para macOS y Linux
            subprocess.Popen(['xdg-open', absolute_path])

    app = tk.Tk()
    app.title("Perukaland Launcher")

    label_frame = tk.Frame(app)
    label_frame.pack(pady=5)

    label = tk.Label(label_frame, text="Username:")
    label.pack(side=tk.LEFT, padx=5)

    entry = tk.Entry(label_frame)
    entry.pack(pady=5)
    entry.insert(0, options['username'])

    close_button = tk.Button(app, text="Cerrar", command=close_window)
    close_button.pack(side=tk.LEFT, padx=5, pady=5)

    update_mods_button = tk.Button(app, text="Actualizar", command=update_launcher)
    update_mods_button.pack(side=tk.LEFT, padx=5, pady=5)

    open_folder_button = tk.Button(app, text="F", command=open_minecraft_directory)
    open_folder_button.pack(side=tk.LEFT, padx=5)

    play_button = tk.Button(app, text="Jugar", command=initialize_game)
    play_button.pack(side=tk.RIGHT, padx=5, pady=5)

    app.mainloop()

#Get OS user to use in the .perukalauncher directory
user_os = os.getenv('USER') or os.getenv('USERNAME')
#Set directory depending on the OS
if platform.system() == "Windows":
    minecraft_directory = f"C://Users//{user_os}//AppData//Roaming//.perukalauncher"
else:
    minecraft_directory = f"/home/{user_os}/.perukalauncher"

#Get versions already installed
versions = minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)

if check_installation():
    versions = minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)
    
    options = deserialize_options()
    setup_config(options)
    serialize_options()

    show_gui()