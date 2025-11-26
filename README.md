# App Update Automation

Script para automatizar actualizaciones de plugins basadas en repositorios Git. El script modifica versiones en archivos clave (init.php, package.json, readme.txt), muestra diffs, permite confirmar commits, crear tags y ejecutar pasos adicionales según el tipo de plugin (free/premium).

## Propósito

El objetivo principal de este proyecto es simplificar y agilizar el proceso de mantenimiento y actualización de plugins, especialmente en entornos donde se manejan múltiples repositorios. Esto incluye tareas como:

- Incrementar versiones automáticamente en archivos clave (`init.php`, `package.json`, `readme.txt`).
- Confirmar y enviar cambios al repositorio remoto.
- Crear tags y ejecutar comandos personalizados.
- Procesar múltiples rutas desde un archivo para actualizar varios plugins en una sola ejecución.

## Instalación

### Requisitos

Antes de comenzar, asegúrate de tener instalados los siguientes componentes:

- **Python**: Versión 3.6 o superior.
- **Git**: Instalado y configurado en tu sistema.
- **Node.js**: Instalado para ejecutar comandos npm.

### Pasos de instalación

1. Clona este repositorio en tu máquina local:

   ```bash
   git clone https://github.com/tu_usuario/app-update-automation.git
   ```

2. Navega al directorio del proyecto:

   ```bash
   cd app-update-automation
   ```

3. Instala las dependencias necesarias (si aplica).

## Uso

El script principal es `files/update.py`. Ejecútalo desde la raíz del proyecto con Python:

```bash
python3 files/update.py --file "repos.txt" --task update --type_plugins free
```

Parámetros principales
----------------------
- --file : Ruta a un archivo que contiene una lista de rutas a repositorios (una por línea).
- --task : Tarea a ejecutar (actualmente `update`).
- --type_plugins : `free` o `premium` (controla pasos adicionales post-commit segun el tipo de plugin que se estan actualizando).

Formato del archivo de rutas
---------------------------
Cada línea representa una entrada. El primer campo es la ruta al repositorio:
```
/ruta/al/plugin1
```
El script toma el primer y unico campo como la ruta.

### Manejo de errores

El script incluye manejo de errores robusto para garantizar que las tareas se ejecuten de manera segura. Algunos ejemplos de validaciones y mensajes de error:


- El script valida que la ruta exista y que sea un repositorio Git (presencia de `.git`).
- Antes de ejecutar pulls se comprueba si hay cambios sin commitear.
- Las versiones deben cumplir el formato semántico `X.Y.Z` para la versión del plugin.
- Mensajes específicos se imprimen en caso de errores en comandos `git` o `npm`.
- Errores capturados evitan abortos silenciosos, se muestran con contexto.

Errores comunes y soluciones
----------------------------
- "Ruta no válida": revisa que la ruta en `repos.txt` exista y sea accesible.
- "No es un repositorio Git válido": asegúrate de que la carpeta contiene `.git`.
- "Hay cambios sin confirmar": realiza commit o stash manualmente antes de usar el script.
- `string indices must be integers, not 'str'`: suele ocurrir por pasar un objeto inesperado en lugar de un diccionario; asegurarse de que `version_request()` devuelve (type_version, versions) y que `versions` es un dict con claves esperadas (`plugin`, `wc`, `wp`).

#### TODO: Añadir más mejorar sobre control de errores y procedimiento para evitar comportamiento erróneos

## Estructura del proyecto

La estructura del proyecto está organizada para facilitar la comprensión y mantenimiento:

```
app-update-automation/
├── files/
│   └── update.py       # Script principal para ejecutar tareas.
├── README.md           # Documentación del proyecto.
└── repos.txt           # Archivo con rutas de repositorios.
```

### Flujo interactivo (qué ocurre al ejecutar)
------------------------------------------
1. Si --file y --task están presentes, se solicita el tipo de versión a actualizar:
   - 1: Solo WooCommerce (wc).
   - 2: Solo WordPress (wp).
   - 3: Ambos.
2. Se piden las versiones correspondientes (wc y/o wp).
3. Para cada ruta válida en el archivo se pregunta si se desea actualizar el plugin.
4. Se solicita la nueva versión del plugin (formato X.Y.Z). Si es válida:
   - Se actualizan init.php, package.json y readme.txt según lo seleccionado.
   - Se muestra `git diff`.
   - Se pregunta si confirmar y efectuar commit/tag/push.
   - Si es `premium`/`free`, se muestran pasos adicionales (comentados o por implementar).

#### Diagrama de flujo

```mermaid
flowchart TD
    %% Estilos
    classDef startEnd fill:#f9f,stroke:#333,stroke-width:2px,color:#000;
    classDef step fill:#bbf,stroke:#333,stroke-width:1px,color:#000;
    classDef decision fill:#ffd,stroke:#333,stroke-width:2px,color:#000;
    classDef premium fill:#cfc,stroke:#333,stroke-width:1px,color:#000;
    classDef free fill:#fcf,stroke:#333,stroke-width:1px,color:#000;

    %% Inicio
    A[Inicio aplicación]:::startEnd --> B[Limpieza archivos ZIP]:::step
    B --> C[Leer parámetros: plugins.txt, tipo plugin]:::step
    C --> D[Solicitar versiones: plugin, WC, WP]:::step
    D --> E[Seleccionar actualización: WC / WP / WC+WP]:::decision
    E --> F[Ejecutar git pullall]:::step

    %% Actualización de archivos
    subgraph UPDATES [Actualización de archivos]
        direction TB
        G{Tipo de actualización}:::decision
        G --> H[init.php y readme.txt → WC]:::step
        G --> I[init.php y readme.txt → WP]:::step
        G --> J[init.php y readme.txt → ambos]:::step
        H --> K[Actualizar package.json]:::step
        I --> K
        J --> K
        K --> L[Mostrar cambios]:::step
        L --> M[Confirmar commit → git add . → commit → push]:::step
    end

    %% Tipo de plugin
    subgraph PLUGIN [Procesos adicionales según tipo de plugin]
        direction TB
        N{Tipo de plugin}:::decision
        N --> O[npm run build-zip → subir paquete → modificar XML → actualizar Live Demo]:::premium
        N --> P[npm run release → limpiar carpetas viejas → crear carpeta nueva → copiar trunk → commit SVN]:::free
    end

    %% Fin
    M --> N
    O --> Q[FIN DEL PROCESO]:::startEnd
    P --> Q

### Descripción de archivos clave

- **`update.py`**: Contiene la lógica principal para ejecutar tareas de automatización. Está dividido en clases:
  - `GitManager`: Maneja operaciones relacionadas con Git.
  - `FileModifier`: Modifica archivos clave como `init.php`, `package.json`, y `readme.txt`.
  - `TaskManager`: Coordina la ejecución de tareas específicas.
- **`repos.txt`**: Archivo que lista rutas de repositorios para procesar en lote.

## Contribución

Si deseas contribuir a este proyecto, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una rama para tu contribución:

   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

3. Realiza tus cambios y envía un pull request.

## Licencia

Este proyecto está bajo la licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente, siempre y cuando incluyas la licencia original.

## Contacto

Si tienes preguntas o necesitas soporte, puedes contactar al autor del proyecto en [alberto.mrtn.nu@gmail.com](mailto:tu_email@example.com).


## Buenas prácticas

- Ejecuta primero en un repositorio de prueba.
- Revisa los diffs antes de confirmar cambios.

## Mejoras:


1. cuando se haga el pullall si  hay cambios preguntar si forzar a que se fuerce el pullall
2. que encuentre bien el changelog para poder añadir los nuevos comentarios
3. eliminar .zip antes de crearlo si ya existe
