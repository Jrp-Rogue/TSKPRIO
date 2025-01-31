import json

# Fonction pour sauvegarder les tâches dans un fichier
def sauvegarder_taches(taches, fichier='taches.json'):
    with open(fichier, 'w') as f:
        json.dump(taches, f, indent=4)

# Fonction pour charger les tâches depuis un fichier
def charger_taches(fichier='taches.json'):
    try:
        with open(fichier, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Fonction pour classifier les tâches dans la matrice d'Eisenhower
def classifier_taches_eisenhower(taches):
    matrice = {
        'important_urgent': [],
        'important_pas_urgent': [],
        'pas_important_urgent': [],
        'pas_important_pas_urgent': []
    }
    
    for tache in taches:
        if tache['importance'] >= 3 and tache['urgence'] >= 3:
            matrice['important_urgent'].append(tache)
        elif tache['importance'] >= 3 and tache['urgence'] < 3:
            matrice['important_pas_urgent'].append(tache)
        elif tache['importance'] < 3 and tache['urgence'] >= 3:
            matrice['pas_important_urgent'].append(tache)
        else:
            matrice['pas_important_pas_urgent'].append(tache)
    
    return matrice

# Fonction pour afficher les tâches
def afficher_taches(taches):
    if not taches:
        print("Aucune tâche dans la liste.")
    else:
        for i, tache in enumerate(taches, 1):
            dependances = ', '.join(tache['dependances']) if tache['dependances'] else "Aucune"
            print(f"{i}. {tache['nom']} (Urgence: {tache['urgence']}, Importance: {tache['importance']}, Dépendances: {dependances})")

# Fonction pour afficher la matrice d'Eisenhower
def afficher_matrice(matrice):
    print("\n📌 Matrice d'Eisenhower :")
    for categorie, liste in matrice.items():
        print(f"\n{categorie.replace('_', ' ').title()}:")
        for tache in liste:
            print(f" - {tache['nom']}")

# Fonction pour modifier une tâche
def modifier_tache(tache):
    print(f"Modification de la tâche: {tache['nom']}")
    try:
        tache['urgence'] = int(input("Nouveau niveau d'urgence (1-5) : "))
        tache['importance'] = int(input("Nouveau niveau d'importance (1-5) : "))
        nouvelles_dependances = input(f"Dépendances actuelles: {', '.join(tache['dependances']) if tache['dependances'] else 'Aucune'}\nNouvelles dépendances (séparées par des virgules) : ").strip()
        tache['dependances'] = [dep.strip() for dep in nouvelles_dependances.split(',')] if nouvelles_dependances else []
    except ValueError:
        print("Erreur de saisie. Les valeurs d'urgence et d'importance doivent être des nombres entiers entre 1 et 5.")

# Fonction pour supprimer une tâche
def supprimer_tache(taches, index):
    try:
        del taches[index-1]
        print("Tâche supprimée.")
    except IndexError:
        print("Erreur : tâche non trouvée.")

# Fonction pour prioriser les tâches
def prioriser_taches(taches, matrice):
    taches_par_nom = {t['nom']: t for t in taches}
    
    def score(tache, visited=None):
        if visited is None:
            visited = set()
        if tache['nom'] in visited:
            return float('-inf')  # Évite les boucles infinies
        visited.add(tache['nom'])
        
        # Score basé sur la matrice d'Eisenhower
        if tache in matrice['important_urgent']:
            base_score = 4
        elif tache in matrice['important_pas_urgent']:
            base_score = 3
        elif tache in matrice['pas_important_urgent']:
            base_score = 2
        else:
            base_score = 1
        
        # Ajustement du score en fonction des dépendances
        if tache['dependances']:
            return min(score(taches_par_nom[d], visited) for d in tache['dependances']) - 1
        return base_score
    
    taches_ordonnee = sorted(taches, key=score, reverse=True)
    
    print("\n📌 Plan d'action priorisé :\n")
    for i, tache in enumerate(taches_ordonnee, 1):
        dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
        print(f"{i}. {tache['nom']} (Urgence: {tache['urgence']}, Importance: {tache['importance']}){dependances_str}")

# Fonction principale pour gérer les tâches
def gerer_taches():
    taches = charger_taches()  # Charger les tâches depuis un fichier (si elles existent)
    
    while True:
        print("\nOptions disponibles :")
        print("1. Afficher les tâches")
        print("2. Modifier une tâche")
        print("3. Supprimer une tâche")
        print("4. Ajouter une nouvelle tâche")
        print("5. Sauvegarder et quitter")
        choix = input("Que souhaitez-vous faire ? (1-5) : ")

        if choix == '1':
            afficher_taches(taches)

        elif choix == '2':
            afficher_taches(taches)
            try:
                index_tache = int(input("Entrez le numéro de la tâche à modifier : "))
                if 1 <= index_tache <= len(taches):
                    modifier_tache(taches[index_tache-1])
                else:
                    print("Numéro de tâche invalide.")
            except ValueError:
                print("Erreur : veuillez entrer un numéro valide.")

        elif choix == '3':
            afficher_taches(taches)
            try:
                index_tache = int(input("Entrez le numéro de la tâche à supprimer : "))
                if 1 <= index_tache <= len(taches):
                    supprimer_tache(taches, index_tache)
                else:
                    print("Numéro de tâche invalide.")
            except ValueError:
                print("Erreur : veuillez entrer un numéro valide.")

        elif choix == '4':
            nom = input("Nom de la nouvelle tâche : ").strip()
            urgence = int(input("Niveau d'urgence (1-5) : "))
            importance = int(input("Niveau d'importance (1-5) : "))
            dependances = input("Dépendances (séparées par des virgules) : ").strip()
            taches.append({
                'nom': nom,
                'urgence': urgence,
                'importance': importance,
                'dependances': [dep.strip() for dep in dependances.split(',')] if dependances else []
            })
            print("Nouvelle tâche ajoutée.")

        elif choix == '5':
            matrice = classifier_taches_eisenhower(taches)  # Classifier les tâches dans la matrice d'Eisenhower
            afficher_matrice(matrice)  # Afficher la matrice d'Eisenhower
            prioriser_taches(taches, matrice)  # Prioriser les tâches en fonction de la matrice
            sauvegarder_taches(taches)
            print("Tâches sauvegardées. Au revoir!")
            break

        else:
            print("Choix invalide. Veuillez choisir une option entre 1 et 5.")

# Lancer la gestion des tâches
gerer_taches()

