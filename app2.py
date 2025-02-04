import streamlit as st
import json
import os
import pandas as pd

# 📌 Nom du fichier pour stocker les tâches
FILE_NAME = "taches.json"

PLANIFICATION_FILE = "planification.json"

# 📌 Fonction pour charger les tâches depuis le fichier JSON
def charger_taches():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            try:
                # Tente de charger le contenu JSON
                return json.load(f)
            except json.JSONDecodeError:
                # Si le fichier est corrompu ou vide, retourne une liste vide
                st.error("Erreur de format JSON, le fichier est peut-être corrompu ou vide.")
                return []
    return []

# 📌 Fonction pour sauvegarder les tâches dans le fichier JSON
def sauvegarder_taches():
    with open(FILE_NAME, "w") as f:
        json.dump(st.session_state.taches, f)

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Tâches")

# 📌 Chargement des tâches depuis le fichier JSON (si elles existent)
if "taches" not in st.session_state:
    st.session_state.taches = charger_taches()

# 📌 Menu de navigation
menu = ["Ajouter une tâche", "Modifier ou supprimer une tâche", "Matrice d'Eisenhower", "Plan d'Action", "Planification Hebdomadaire"]
choix = st.sidebar.selectbox("Sélectionner une option", menu)

# 📌 Ajouter une tâche
if choix == "Ajouter une tâche":
    st.subheader("➕ Ajouter une tâche")
    nom = st.text_input("Nom de la tâche :")
    urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
    importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")
    
    # Sélection des dépendances parmi les tâches existantes
    options_dependances = [t["nom"] for t in st.session_state.taches]
    dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances, key="dependances_add")

    if any(dep not in options_dependances for dep in dependances):
        st.error("Une ou plusieurs dépendances n'existent pas dans les tâches actuelles.")
    
    if st.button("Ajouter la tâche"):
        if nom:
            nouvelle_tache = {
                "nom": nom,
                "urgence": urgence,
                "importance": importance,
                "dependances": dependances
            }
            st.session_state.taches.append(nouvelle_tache)
            sauvegarder_taches()  # Sauvegarde après ajout
            st.success(f"Tâche '{nom}' ajoutée !")
        else:
            st.error("Le nom de la tâche est requis.")

# 📌 Modifier ou supprimer une tâche
elif choix == "Modifier ou supprimer une tâche":
    st.subheader("✏️ Modifier ou supprimer une tâche")
    taches_existantes = [t["nom"] for t in st.session_state.taches]
    tache_selectionnee = st.selectbox("Sélectionner une tâche", taches_existantes)

    if tache_selectionnee:
        tache_modifiee = next(t for t in st.session_state.taches if t["nom"] == tache_selectionnee)
        
        # Champs pour modifier la tâche
        nouveau_nom = st.text_input("Nom de la tâche", value=tache_modifiee["nom"], key="nom_modify")
        nouvelle_urgence = st.slider("Niveau d'urgence", 1, 5, tache_modifiee["urgence"], key="urgence_modify")
        nouvelle_importance = st.slider("Niveau d'importance", 1, 5, tache_modifiee["importance"], key="importance_modify")
        
        # Définir les options de dépendances en utilisant les tâches existantes (sans la tâche actuelle)
        options_dependances = [t["nom"] for t in st.session_state.taches if t["nom"] != tache_modifiee["nom"]]
        
        nouvelles_dependances = st.multiselect("Tâches dont cette tâche dépend", options_dependances, default=tache_modifiee["dependances"], key="dependances_modify")
        
        if any(dep not in options_dependances for dep in nouvelles_dependances):
            st.error("Une ou plusieurs dépendances n'existent pas dans les tâches actuelles.")
        
        if st.button("Modifier la tâche"):
            if nouveau_nom:
                tache_modifiee.update({"nom": nouveau_nom, "urgence": nouvelle_urgence, "importance": nouvelle_importance, "dependances": nouvelles_dependances})
                sauvegarder_taches()  # Sauvegarde après modification
                st.success(f"Tâche '{nouveau_nom}' modifiée !")
            else:
                st.error("Le nom de la tâche est requis.")
        
        if st.button("Supprimer la tâche"):
            st.session_state.taches = [t for t in st.session_state.taches if t["nom"] != tache_selectionnee]
            sauvegarder_taches()  # Sauvegarde après suppression
            st.success(f"Tâche '{tache_selectionnee}' supprimée !")

# 📌 Matrice d'Eisenhower
elif choix == "Matrice d'Eisenhower":
    def classifier_taches_eisenhower(taches):
        """Classe les tâches selon la matrice d'Eisenhower"""
        matrice = {
            'Important & Urgent': [],
            'Important mais Pas Urgent': [],
            'Pas Important mais Urgent': [],
            'Pas Important & Pas Urgent': []
        }
        for tache in taches:
            if tache['importance'] >= 3 and tache['urgence'] >= 3:
                matrice['Important & Urgent'].append(tache)
            elif tache['importance'] >= 3 and tache['urgence'] < 3:
                matrice['Important mais Pas Urgent'].append(tache)
            elif tache['importance'] < 3 and tache['urgence'] >= 3:
                matrice['Pas Important mais Urgent'].append(tache)
            else:
                matrice['Pas Important & Pas Urgent'].append(tache)
        return matrice
    
    def afficher_matrice(matrice):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.axhline(y=1, color='black', linewidth=2)
        ax.axvline(x=1, color='black', linewidth=2)
        colors = {'Important & Urgent': 'red', 'Important mais Pas Urgent': 'orange', 'Pas Important mais Urgent': 'blue', 'Pas Important & Pas Urgent': 'gray'}
        
        for categorie, taches_liste in matrice.items():
            x, y = (0, 1) if categorie == 'Important & Urgent' else (1, 1) if categorie == 'Important mais Pas Urgent' else (0, 0) if categorie == 'Pas Important mais Urgent' else (1, 0)
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[categorie], alpha=0.3))
            ax.text(x + 0.5, y + 1.05, categorie, ha='center', va='center', fontsize=12, fontweight='bold', color='black')
            for i, tache in enumerate(taches_liste):
                ax.text(x + 0.5, y + 1.05 - (i + 1) * 0.15, tache["nom"], ha='center', va='center', fontsize=10, color='black')
        ax.set_xticks([0.5, 1.5])
        ax.set_yticks([0.5, 1.5])
        ax.axis('off')
        st.pyplot(fig)
    if "taches" in st.session_state and len(st.session_state.taches) > 0:
        matrice = classifier_taches_eisenhower(st.session_state.taches)
        afficher_matrice(matrice)   
    else:
        st.error("Aucune tâche disponible pour classer.")
    

# 📌 Plan d'action
elif choix == "Plan d'Action":

    st.subheader("📌 Plan d'Action")

    def classifier_taches_eisenhower(taches):
        """Classe les tâches selon la matrice d'Eisenhower"""
        matrice = {
            'Important & Urgent': [],
            'Important mais Pas Urgent': [],
            'Pas Important mais Urgent': [],
            'Pas Important & Pas Urgent': []
        }
        for tache in taches:
            if tache['importance'] >= 3 and tache['urgence'] >= 3:
                matrice['Important & Urgent'].append(tache)
            elif tache['importance'] >= 3 and tache['urgence'] < 3:
                matrice['Important mais Pas Urgent'].append(tache)
            elif tache['importance'] < 3 and tache['urgence'] >= 3:
                matrice['Pas Important mais Urgent'].append(tache)
            else:
                matrice['Pas Important & Pas Urgent'].append(tache)
        return matrice

    def prioriser_taches(taches, matrice):
        """Trie les tâches en prenant en compte la dépendance, la priorité et la matrice d'Eisenhower."""
        taches_par_nom = {t['nom']: t for t in taches}

        # Fonction pour obtenir le score d'une tâche basé sur la matrice
        def score(tache, visited=None):
            if visited is None:
                visited = set()
            if tache['nom'] in visited:
                return float('-inf')  # Évite les boucles infinies
            visited.add(tache['nom'])

            # Score basé sur la matrice d'Eisenhower (urgence et importance)
            if tache in matrice['Important & Urgent']:
                base_score = 4
            elif tache in matrice['Important mais Pas Urgent']:
                base_score = 3
            elif tache in matrice['Pas Important mais Urgent']:
                base_score = 2
            else:
                base_score = 1

            # Ajustement du score en fonction des dépendances
            if tache['dependances']:
                max_dependance_score = max(score(taches_par_nom[d], visited) for d in tache['dependances'])
                # Le score ajusté ne sera pas inférieur à la priorité de la matrice
                base_score = max(base_score, max_dependance_score)

            return base_score

        # On utilise le score calculé pour trier les tâches
        taches_triees = sorted(taches, key=score, reverse=True)

        # On fait en sorte que les tâches dépendantes soient priorisées avant celles qui en dépendent
        taches_finales = []
        taches_deja_affichees = set()

        # On place les tâches qui n'ont pas de dépendances en premier
        for tache in taches_triees:
            if not tache['dependances']:
                taches_finales.append(tache)
                taches_deja_affichees.add(tache['nom'])

        # Ensuite, on place les tâches dépendantes
        for tache in taches_triees:
            if tache['nom'] not in taches_deja_affichees:
                taches_finales.append(tache)

        return taches_finales

    # 📊 Génération de la matrice d'Eisenhower
    matrice = classifier_taches_eisenhower(st.session_state.taches)
    
    # 📋 Priorisation des tâches en fonction de la matrice d'Eisenhower et des dépendances
    taches_ordonnee = prioriser_taches(st.session_state.taches, matrice)

    # Affichage des tâches priorisées avec numérotation
    for i, tache in enumerate(taches_ordonnee, 1):
        dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
        st.write(f"{i}. {tache['nom']} (🔴 Urgence: {tache['urgence']}, 🟢 Importance: {tache['importance']}){dependances_str}")

# 📅 Planification hebdomadaire
elif choix == "Planification Hebdomadaire":
    st.subheader("📅 Planification Hebdomadaire")

    jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    # Charger la planification si elle n'est pas encore dans `st.session_state`
    if "planification" not in st.session_state:
        st.session_state.planification = charger_planification()

    # Interface pour assigner les tâches aux jours
    for jour in jours_semaine:
        taches_selectionnees = st.multiselect(
            f"Tâches pour {jour}",
            options=[t["nom"] for t in st.session_state.taches],  # Liste des tâches
            default=st.session_state.planification[jour],  # Valeurs actuelles
            key=f"planif_{jour}"
        )
        st.session_state.planification[jour] = taches_selectionnees  # Mise à jour
    
    # Sauvegarde automatique dès qu'un changement est détecté
    sauvegarder_planification()

    # 📌 Affichage de la planification sous forme de tableau
    st.subheader("🗓️ Vue hebdomadaire")
    
    # Trouver le nombre maximum de tâches pour définir le nombre de lignes du tableau
    max_tasks = max(len(taches) for taches in st.session_state.planification.values())
    
    # Reformater les données pour que chaque tâche soit sur une ligne distincte
    table = {jour: (st.session_state.planification[jour] + [""] * (max_tasks - len(st.session_state.planification[jour])))
             for jour in jours_semaine}
    
    # Création du DataFrame
    df = pd.DataFrame(table)
    
    # Affichage sous forme de tableau
    st.dataframe(df)
