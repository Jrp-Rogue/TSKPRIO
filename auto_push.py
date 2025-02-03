import os

def push_to_github():
    os.system("git add projets.json")
    os.system('git commit -m "Mise à jour automatique des fichiers de projets"')
    os.system("git push origin main")  # Change 'main' selon ta branche

try:
    push_to_github()
    print("✅ Modifications poussées sur GitHub avec succès !")
except Exception as e:
    print(f"❌ Erreur lors du push : {e}")
