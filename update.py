import subprocess
import os
import argparse
import re
import json
from datetime import datetime


def version_request():
    #Una vez iniciado el programa, se selecciona que tipo de actualizacion va a realizar
    type_version = input("Selecciona el tipo de versión a actualizar (1: wc, 2: wp, 3: both): ").strip()

    # Diccionario donde guardaremos las versiones seleccionadas
    versions = {}

    # Según la elección, pedimos la(s) versión(es)
    if type_version == "1":
        versions["wc"] = input("Introduce la nueva versión de WooCommerce: ").strip()

    elif type_version == "2":
        versions["wp"] = input("Introduce la nueva versión de WordPress: ").strip()

    elif type_version == "3":
        versions["wc"] = input("Introduce la nueva versión de WooCommerce: ").strip()
        versions["wp"] = input("Introduce la nueva versión de WordPress: ").strip()

    else:
        print("Opción no válida.")
        return None

    return type_version, versions

class GitManager:
    
    def is_git_repo(repo_path):
        """Verifica si la carpeta es un repositorio Git válido."""
        return os.path.isdir(os.path.join(repo_path, ".git"))
    
    
    def has_uncommitted_changes(repo_path):
        """Verifica si hay cambios sin confirmar en el repositorio."""
        try:
            result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True)
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    
    def pull_all(repo_path):
        """Accede a la carpeta del repositorio y ejecuta git pullall."""
        try:
            if not os.path.isdir(repo_path):
                print(f"❌ La carpeta '{repo_path}' no existe.")
                return
            
            if not GitManager.is_git_repo(repo_path):
                print(f"❌ La carpeta '{repo_path}' no es un repositorio Git válido.")
                return
            
            if GitManager.has_uncommitted_changes(repo_path):
                print("⚠️ Hay cambios sin confirmar en el repositorio. Confirma o descarta los cambios antes de continuar.")
                return
            
            os.chdir(repo_path)
            subprocess.run(["git", "pullall"], capture_output=True, text=True, check=True)
            print("✅ Proceso de pullall completado correctamente.")
        except FileNotFoundError:
            print(f"❌ La carpeta '{repo_path}' no existe.")
        except subprocess.CalledProcessError as e:
            print("❌ Error al ejecutar git pullall:")
            print(e.stderr)

    
    def git_diff(repo_path):
        """Muestra los cambios realizados en el repositorio."""
        try:
            os.chdir(repo_path)
            result = subprocess.run(["git", "diff"], capture_output=True, text=True, check=True)
            print("📝 Cambios realizados:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("❌ Error al ejecutar git diff:")
            print(e.stderr)
    
    
    def git_add(repo_path):
        """Ejecuta git add . para añadir cambios al área de preparación."""
        try:
            if not GitManager.is_git_repo(repo_path):
                print(f"❌ La carpeta '{repo_path}' no es un repositorio Git válido.")
                return
            
            os.chdir(repo_path)
            subprocess.run(["git", "add", "."], capture_output=True, text=True, check=True)
            print("✅ Archivos añadidos correctamente al área de preparación.")
        except subprocess.CalledProcessError as e:
            print("❌ Error al ejecutar git add:")
            print(e.stderr)
    
    
    def git_commit(repo_path, version):
       
        """Ejecuta git commit con un mensaje en formato '1.42.0 - Released on 24 February 2025'."""
        try:

            GitManager.git_add(repo_path)
            today = datetime.today().strftime("%d %B %Y")
            commit_message = f"= {version} - Released on {today} ="

            os.chdir(repo_path)
            subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True, check=True)
            print(f"✅ Cambios confirmados con mensaje: {commit_message}")

            GitManager.git_tag_push(repo_path, version)
            GitManager.git_push(repo_path)

        except subprocess.CalledProcessError as e:
            print("❌ Error al ejecutar git commit:")
            print(e.stderr)

    
    def git_tag_push(repo_path, version):
        """Crea un tag con la versión y lo sube al repositorio remoto."""
        try:
            os.chdir(repo_path)
            
            # Crear el tag
            subprocess.run(["git", "tag", version], capture_output=True, text=True, check=True)
            print(f"🏷️  Tag '{version}' creado correctamente.")

            # Subir el tag
            subprocess.run(["git", "push", "origin", version], capture_output=True, text=True, check=True)
            print(f"🚀 Tag '{version}' enviado al repositorio remoto.")
        except subprocess.CalledProcessError as e:
            print("❌ Error al ejecutar git tag o git push origin:")
            print(e.stderr)
    
    
    def git_push(repo_path):
        """Ejecuta git push para enviar los cambios al repositorio remoto."""
        try:
            os.chdir(repo_path)
            subprocess.run(["git", "push"], capture_output=True, text=True, check=True)
            print("✅ Cambios enviados al repositorio remoto.")
        except subprocess.CalledProcessError as e:
            print("❌ Error al ejecutar git push:")
            print(e.stderr)

    
    def run_npm_build_zip(repo_path):
        """Ejecuta el comando 'npm run build-zip'."""
        try:
            os.chdir(repo_path)
            subprocess.run(["npm", "run", "build-zip"], capture_output=True, text=True, check=True)
            print("✅ Comando 'npm run build-zip' ejecutado correctamente.")
        except subprocess.CalledProcessError as e:
            print("❌ Error al ejecutar 'npm run build-zip':")
            print(e.stderr)


class FileModifier:

    def adjust_latest_wc_version(self, version):
        """Ajusta la versión de WooCommerce restando 2 al número menor."""
        major, minor = map(int, version.split('.'))

        if minor < 2:
            major -= 1
            minor = 10 + minor - 2
        else:
            minor -= 2

        new_version = f"{major}.{minor}"
        return new_version

    def update_package_json(self, package_path, plugin_version=None):
        """Modifica package.json con la nueva versión."""
        try:

            with open(package_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            if "version" in data:
                
                data["version"] = f"{plugin_version}"
            
            with open(package_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
        except Exception as e:
            print(f"❌ Error al modificar {package_path}: {e}")
            return
        
        print(f"✅ Modificado: {package_path}")

    def update_init_php(self, init_path, versions, type_version, adjust_latest_wc_version):
        """Modifica init.php con las nuevas versiones para WP y WC."""
        with open(init_path, "r", encoding="utf-8") as file:
            content = file.read()

        content = re.sub(r'\* Version:\s*\d+\.\d+\.\d+', f"* Version: {versions['plugin']}", content)
        if type_version in ["1", "3"] and "wc" in versions:
            content = re.sub(r'\* WC requires at least:\s*(\d+)\.(\d+)',lambda m: f"* WC requires at least: {adjust_latest_wc_version(versions['wc'])}", content)
            content = re.sub(r'\* WC tested up to:\s*(\d+)\.(\d+)', lambda m: f"* WC tested up to: {(versions['wc'])}", content)
        content = re.sub(r'\* @version\s*(\d+)\.(\d+)\.(\d+)', lambda m: f"* @version {versions['plugin']}", content)

        # Expresión regular para encontrar la constante YITH_*_VERSION (excluyendo _DB_)
        #pattern = r"(define\(\s*'YITH_[A-Z_]+(?<!_DB)_VERSION'\s*,\s*')(\d+)\.(\d+)\.(\d+)"
        pattern = r"(define\(\s*'Y[A-Z_]*?(?<!_DB)_VERSION'\s*,\s*')(\d+)\.(\d+)\.(\d+)"

        content = re.sub(pattern, lambda m: f"{m.group(1)}{versions['plugin']}", content)
        
        with open(init_path, "w", encoding="utf-8") as file:
            file.write(content)
        
        print(f"✅ Modificado: {init_path}")

    def update_readme(self, readme_path, versions, type_version, adjust_latest_wc_version):
        """Actualiza las versiones y el changelog en el archivo readme.txt para WP y WC."""
        try:
            with open(readme_path, "r", encoding="utf-8") as file:
                content = file.readlines()

            #TODO: comprobar si se quiere hacer los cambios para wp tambien o solo para wc

            rules = {
                "Stable tag:": {
                    "regex": r"(\d+\.\d+\.\d+)",
                    "value": lambda v: v["plugin"]
                },
                "Tested up to:": {
                    "regex": r"(\d+\.\d+)",
                    "value": lambda v: v["wp"]
                },
                "Requires at least:": {
                    "regex": r"(\d+\.\d+)",
                    "value": lambda v: self.adjust_latest_wc_version(v["wp"])
                }
            }

            if type_version == "1":
                active_rules = {
                    k: v for k, v in rules.items()
                    if k == "Stable tag:"
                }
            else:
                # aplicar todas las reglas
                active_rules = rules

            for i, line in enumerate(content):
                for prefix, rule in active_rules.items():
                    if line.startswith(prefix):
                        old_version = re.search(rule["regex"], line).group()
                        new_version = rule["value"](versions)
                        content[i] = line.replace(old_version, new_version)
                        break

            # Buscar el índice de la sección Changelog
            changelog_index = content.index("== Changelog ==\n") + 1

            today = datetime.today().strftime("%d %B %Y")
            
            if type_version == "1":
                new_changelog = f"\n= {versions['plugin']} - Released on {today} =\n* New: Support for WooCommerce {versions['wc']}\n* Update: YITH plugin framework\n"
            elif type_version == "2":
                new_changelog = f"\n= {versions['plugin']} - Released on {today} =\n* New: Support for WordPress {versions['wp']}\n* Update: YITH plugin framework\n"
            else:
                new_changelog = f"\n= {versions['plugin']} - Released on {today} =\n* New: Support for WooCommerce {versions['wc']}\n* New: Support for WordPress {versions['wp']}\n* Update: YITH plugin framework\n"

            # Insertar el nuevo changelog después de "== Changelog =="
            content.insert(changelog_index, new_changelog)

            with open(readme_path, "w", encoding="utf-8") as file:
                file.writelines(content)

            print("✅ Archivo readme.txt actualizado correctamente.")
        except Exception as e:
            print(f"❌ Error al actualizar readme.txt: {e}")

class TaskManager:

    def __init__(self):
        
        self.tasks = {
            "update": lambda path: self.run_update(path),
        }

        self.versions = {}
        self.plugin_version = ""
        self.type_plugins = None
        self.type_version = None
        self.fileModifier = FileModifier()

    def procesar_archivo_rutas(self, file, task, type_plugin, type_version, versions):
        """ Recorre un archivo y ejecuta una tarea sobre cada ruta válida encontrada """
        if task not in self.tasks:
            print(f"Tarea '{task}' no encontrada.")
            return

        self.versions = versions  # Actualiza las versiones
        self.type_plugins = type_plugin  # Actualiza el tipo de plugin
        self.type_version = type_version  # Actualiza el tipo de version
        self.file_modifier = FileModifier()  # Instancia FileModifier

        with open(file, 'r', encoding='utf-8') as f:
            for index, linea in enumerate(f, start=1):
                # La ruta es el primer y unico elemento de la línea
                args = linea.split(',')
                path = args[0].strip()  

                if os.path.exists(path):  # Validamos que sea una ruta existente
                    plugin_name = os.path.basename(path)  # Extraemos el nombre del plugin
                    response = input(f"¿Quieres actualizar el siguiente plugin {plugin_name}? (s/n): ").strip().lower()
                    
                    if response == 's':
                        while True:
                            version_input = input(f"¿A que version quieres actualizar el plugin {plugin_name}? (ej. 1.33.0): ").strip().lower()

                            if not re.match(r'^\d+\.\d+\.\d+$', version_input):
                                print("❌ Formato inválido. Debe ser X.Y.Z, por ejemplo 1.23.4")
                                continue  # vuelve a preguntar

                            plugin_version = version_input
                            break  # formato correcto, salir del bucle

                        self.plugin_version = plugin_version  # Actualiza la version del plugin
                        self.versions['plugin'] = plugin_version  # Añade la version del plugin al diccionario de versiones
                       
                        print(f"Ejecutando '{task}' en: {path}")
                        self.tasks[task](path)  # Ejecuta la tarea sobre la ruta válida
                    else:
                        print(f"Omitiendo {plugin_name}")
                else:
                    print(f"Ruta no válida: {path}")

    
    def run_update(self, repo_path):
        try:
            print("Iniciando actualización...")
            # Actualizamos el repositorio antes de hacer cualquier cambio
            GitManager.pull_all(repo_path)
            
            if self.versions == {}:
                print("No se han proporcionado versiones para actualizar.")
                return
            
            self.file_modifier.update_init_php(os.path.join(repo_path, "init.php"), self.versions, self.type_version, self.file_modifier.adjust_latest_wc_version)
            self.file_modifier.update_readme(os.path.join(repo_path, "readme.txt"), self.versions, self.type_version, self.file_modifier.adjust_latest_wc_version)
            self.file_modifier.update_package_json(os.path.join(repo_path, "package.json"), self.plugin_version)

            # Mostramos los cambios realizados
            GitManager.git_diff(repo_path)

            '''Esto es para que el usuario pueda revisar los cambios y añadir otras modificaciones antes de hacer el commit'''
            print("¿Deseas confirmar los cambios ahora? (s/n): ")
            confirm = input().strip().lower()
            if confirm == 's':
                # hacer git add ., git commit y git push
                GitManager.git_commit(repo_path, self.plugin_version)
                
            if self.type_plugins == "premium":
                print("Ejecutando pasos adicionales para plugins PREMIUM...")
                #GitManager.run_npm_build_zip(repo_path)

            if self.type_plugins == "free":
                print("Ejecutando pasos adicionales para plugins FREE...")
                #TODO Lógica para mover carpetas crear tag, mover archivos
                #GitManager.run_npm_release(repo_path)

        except Exception as e:
            print(f"Error en 'run_update': {e}")
            return  # Detiene la ejecución de 'run_update_all' pero permite continuar con el bucle


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutar tareas de automatización.")

    #TODO Limpiamos archivos zip (ver donde se estan creando)

    parser.add_argument("--type_plugins", help="Tipo de plugins a actualizar", choices=["free", "premium"], default=None)
    parser.add_argument("--file", help="Archivo con rutas de los plugins para procesar", default=None)
    parser.add_argument("--task", help="Tarea a ejecutar", choices=["update"], default=None)
    args = parser.parse_args()

    #almacenamos los argumentos en data por si se necesitan luego
    type_plugins = args.type_plugins 
   
    # create TaskManager instance
    manager = TaskManager()

    # Si se proporciona un archivo y una tarea, procesa las rutas del archivo ejecutando la tarea especificada.
    if ( args.file and args.task == 'update' ):

        type_version, versions = version_request()

        manager.procesar_archivo_rutas(args.file, args.task, type_plugins, type_version, versions)
    else:
        print("❌ Debes especificar una tarea con --task o un archivo con --file para procesar rutas.")


