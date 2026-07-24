# import os
# import re
# import base64
#
# # 1. Chemins des fichiers
# base_dir = os.path.dirname(os.path.abspath(__file__))
# readme_path = os.path.join(base_dir, 'README.md')
# target_path = os.path.join(base_dir, 'web-demo', 'index.html') # Ajustez si nécessaire
#
# # 2. Lire et encoder en Base64
# with open(readme_path, 'rb') as f:
#     b64_string = base64.b64encode(f.read()).decode('utf-8')
#
# # 3. Lire le fichier cible
# with open(target_path, 'r', encoding='utf-8') as f:
#     content = f.read()
#
# # 4. Remplacer le contenu
# regex = r'(b64:\s*["\'])([^"\']*)(["\'])'
# if re.search(regex, content):
#     new_content = re.sub(regex, f'\\1{b64_string}\\3', content)
#     with open(target_path, 'w', encoding='utf-8') as f:
#         f.write(new_content)
#     print("✅ Le code Base64 du README a été mis à jour en Python !")
# else:
#     print("❌ Clé 'b64' introuvable dans le fichier cible.")
import os
import re
import base64

# 1. Configuration des dossiers
base_dir = os.path.dirname(os.path.abspath(__file__)) # Dossier web-demo
root_dir = os.path.dirname(base_dir)                  # Racine acc-toolkit
readme_path = os.path.join(root_dir, 'README.md')

# 2. Trouver automatiquement le fichier JS dans web-demo
target_path = None
for file in os.listdir(base_dir):
    if file.endswith('.js') and file != 'update_readme.py': # Évite de se cibler soi-même
        target_path = os.path.join(base_dir, file)
        break

if not target_path:
    # Si aucun .js n'est trouvé, on se rabat par sécurité sur index.html
    target_path = os.path.join(base_dir, 'index.html')

print(f"🔍 Fichier cible détecté : {os.path.basename(target_path)}")

# 3. Lire le README et l'encoder en Base64
with open(readme_path, 'rb') as f:
    b64_string = base64.b64encode(f.read()).decode('utf-8')

# 4. Lire le fichier cible
with open(target_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 5. Remplacer le contenu avec la Regex flexible
regex = r'(b64\s*:\s*["\'])(.*?)(["\'])'

if re.search(regex, content, re.DOTALL):
    new_content = re.sub(regex, f'\\1{b64_string}\\3', content, flags=re.DOTALL)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ Le code Base64 a été mis à jour avec succès dans {os.path.basename(target_path)} !")
else:
    print(f"❌ Erreur : La clé 'b64' n'a pas été trouvée dans {os.path.basename(target_path)}.")
