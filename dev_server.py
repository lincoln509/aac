import os
import re
import base64
import mimetypes
from http.server import SimpleHTTPRequestHandler
import socketserver

PORT = 8000
# Initialisation propre des dossiers absolus
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT_DIR, 'web-demo')

def update_all_readmes_base64():
    """Scanne les fichiers de la démo web pour synchroniser les blocs README."""
    target_files = []
    for root, _, files in os.walk(WEB_DIR):
        for file in files:
            if file.endswith(('.js', '.html')):
                target_files.append(os.path.join(root, file))

    block_regex = r'(\{\s*name\s*:\s*["\']([^"\']+)["\']\s*,\s*path\s*:\s*["\']([^"\']+)["\']\s*,\s*lang\s*:\s*["\']([^"\']+)["\']\s*,\s*b64\s*:\s*["\'])(.*?)(["\']\s*\})'

    for target_path in target_files:
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()

        modified = False

        def replace_b64(match):
            nonlocal modified
            prefix = match.group(1)
            readme_rel_path = match.group(3)
            suffix = match.group(6)

            clean_rel_path = readme_rel_path.lstrip('./').replace('../', '')
            actual_readme_path = os.path.join(ROOT_DIR, clean_rel_path)

            if os.path.exists(actual_readme_path):
                with open(actual_readme_path, 'rb') as readme_file:
                    new_b64 = base64.b64encode(readme_file.read()).decode('utf-8')
                modified = True
                print(f"🔄 Synchro effectuée : {readme_rel_path} -> {os.path.basename(target_path)}")
                return f"{prefix}{new_b64}{suffix}"
            return match.group(0)

        new_content = re.sub(block_regex, replace_b64, content, flags=re.DOTALL)
        if modified:
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

class AutoUpdateHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        kwargs['directory'] = WEB_DIR
        super().__init__(*args, **kwargs)

    def do_GET(self):
        # 1. Nettoyer et normaliser le chemin demandé par le navigateur
        # Enlève les paramètres de requêtes éventuels (?v=1.2 etc)
        clean_path = self.path.split('?')[0]

        # 2. Déclencher la mise à jour des README au chargement principal
        if clean_path in ('/', '/index.html', '/web-demo', '/web-demo/'):
            try:
                update_all_readmes_base64()
            except Exception as e:
                print(f"⚠️ Erreur synchro : {e}")

        # 3. Intercepter le dossier assets situé hors de web-demo
        normalized_path = clean_path.lstrip('/') # Enlève le premier slash
        if normalized_path.startswith('assets/'):
            # Convertit le chemin web en chemin Windows/Linux valide
            local_asset_path = os.path.join(ROOT_DIR, normalized_path.replace('/', os.sep))

            if os.path.exists(local_asset_path) and os.path.isfile(local_asset_path):
                self.send_response(200)

                # Détection automatique du type MIME (png, jpg, svg, gif...)
                mime_type, _ = mimetypes.guess_type(local_asset_path)
                if mime_type:
                    self.send_header('Content-type', mime_type)

                self.end_headers()

                # Envoi des données binaires de l'image
                with open(local_asset_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                print(f"❌ Image introuvable sur le disque : {local_asset_path}")

        # Comportement standard pour le reste des fichiers (dans web-demo)
        return super().do_GET()

# Initialisation et démarrage du serveur
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), AutoUpdateHandler) as httpd:
    print(f"🚀 Serveur robuste actif sur http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté.")

