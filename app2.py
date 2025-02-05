import streamlit as st
import json
import os
import pandas as pd

# 📌 Nom du fichier pour stocker les tâches
FILE_NAME = "taches.json"

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

# 📌 Nom du fichier pour stocker la planification
PLANIF_FILE = "planifications.json"

# 📌 Fonction pour charger la planification depuis le fichier JSON
def charger_planification():
    if os.path.exists(PLANIF_FILE):
        with open(PLANIF_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                st.error("Erreur de format JSON dans la planification.")
                return {jour: [] for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]}
    return {jour: [] for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]}

# 📌 Fonction pour sauvegarder la planification dans le fichier JSON
def sauvegarder_planification():
    with open(PLANIF_FILE, "w") as f:
        json.dump(st.session_state.planifications, f)

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

    if not st.session_state.taches:
        st.warning("Aucune tâche disponible.")
        st.stop()

    taches_existantes = [t["nom"] for t in st.session_state.taches]
    tache_selectionnee = st.selectbox("Sélectionner une tâche", taches_existantes)

    if tache_selectionnee:
        # Copie de la tâche sélectionnée
        tache_modifiee = next(t for t in st.session_state.taches if t["nom"] == tache_selectionnee)
        tache_temp = tache_modifiee.copy()  # Éviter les modifications directes avant validation

        # Champs de modification
        tache_temp["nom"] = st.text_input("Nom de la tâche", value=tache_modifiee["nom"], key="nom_modify")
        tache_temp["urgence"] = st.slider("Niveau d'urgence", 1, 5, tache_modifiee["urgence"], key="urgence_modify")
        tache_temp["importance"] = st.slider("Niveau d'importance", 1, 5, tache_modifiee["importance"], key="importance_modify")

        # Dépendances
        options_dependances = [t["nom"] for t in st.session_state.taches if t["nom"] != tache_modifiee["nom"]]
        tache_temp["dependances"] = st.multiselect(
            "Tâches dont cette tâche dépend", 
            options_dependances, 
            default=tache_modifiee["dependances"], 
            key="dependances_modify"
        )

        if any(dep not in options_dependances for dep in tache_temp["dependances"]):
            st.error("Une ou plusieurs dépendances n'existent pas dans les tâches actuelles.")

        # Modification de la tâche
        if st.button("Modifier la tâche"):
            if tache_temp["nom"].strip():
                index = st.session_state.taches.index(tache_modifiee)
                st.session_state.taches[index] = tache_temp  # Remplacement dans la liste
                sauvegarder_taches()
                st.success(f"Tâche '{tache_temp['nom']}' modifiée !")
                st.rerun()
            else:
                st.error("Le nom de la tâche est requis.")

        # Suppression de la tâche (avec vérification des dépendances)
        if st.button("Supprimer la tâche"):
            taches_dependantes = [t["nom"] for t in st.session_state.taches if tache_selectionnee in t["dependances"]]

            if taches_dependantes:
                st.error(f"Impossible de supprimer cette tâche. Elle est une dépendance pour : {', '.join(taches_dependantes)}.")
            else:
                st.session_state.taches = [t for t in st.session_state.taches if t["nom"] != tache_selectionnee]
                sauvegarder_taches()
                st.success(f"Tâche '{tache_selectionnee}' supprimée !")
                st.rerun()


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
    

# 📌 Plan d'Action
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
        """Trie les tâches en prenant en compte la dépendance et la priorité Eisenhower"""
        taches_par_nom = {t['nom']: t for t in taches}

        # Définition des scores basés sur la matrice
        def score_eisenhower(tache):
            if tache in matrice['Important & Urgent']:
                return 4
            elif tache in matrice['Important mais Pas Urgent']:
                return 3
            elif tache in matrice['Pas Important mais Urgent']:
                return 2
            else:
                return 1

        # Gestion des dépendances avec tri topologique (Kahn’s Algorithm)
        def trier_par_dependance(taches):
            """Trie les tâches en respectant leurs dépendances"""
            ordre = []
            dependencies = {t['nom']: set(t['dependances']) for t in taches}
            independantes = [t for t in taches if not dependencies[t['nom']]]

            while independantes:
                tache = independantes.pop(0)
                ordre.append(tache)

                for t in taches:
                    if t['nom'] in dependencies and tache['nom'] in dependencies[t['nom']]:
                        dependencies[t['nom']].remove(tache['nom'])
                        if not dependencies[t['nom']]:  # Si plus de dépendance, on peut l'ajouter
                            independantes.append(t)

            if len(ordre) != len(taches):  # Dépendance circulaire détectée
                st.error("⚠️ Dépendances circulaires détectées ! Vérifiez les tâches.")
                return []

            return ordre

        # Classement initial des tâches par priorité Eisenhower
        taches_triees = sorted(taches, key=score_eisenhower, reverse=True)

        # Tri final en respectant les dépendances
        taches_finales = trier_par_dependance(taches_triees)

        return taches_finales

    # 📊 Génération de la matrice d'Eisenhower
    matrice = classifier_taches_eisenhower(st.session_state.taches)
    
    # 📋 Priorisation des tâches en fonction de la matrice d'Eisenhower et des dépendances
    taches_ordonnee = prioriser_taches(st.session_state.taches, matrice)

    # 📝 Affichage des tâches priorisées
    if taches_ordonnee:
        for i, tache in enumerate(taches_ordonnee, 1):
            dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
            st.write(f"{i}. {tache['nom']} (🔴 Urgence: {tache['urgence']}, 🟢 Importance: {tache['importance']}){dependances_str}")
    else:
        st.warning("Aucune tâche à afficher ou problème détecté dans les dépendances.")

# 📅 Planification hebdomadaire
elif choix == "Planification Hebdomadaire":
    st.subheader("📅 Planification Hebdomadaire")

    jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    # Initialisation de l'état si non existant
    if "planifications" not in st.session_state:
        st.session_state.planifications = charger_planification()

    # Interface pour assigner les tâches aux jours
    for jour in jours_semaine:
        # Liste des tâches disponibles
        options_taches = [t["nom"] for t in st.session_state.taches]
        
        # Récupère les tâches sélectionnées pour ce jour, et filtre les tâches supprimées
        taches_selectionnees = st.session_state.planifications[jour]
        taches_selectionnees_valides = [tache for tache in taches_selectionnees if tache in options_taches]
    
        # Met à jour les tâches sélectionnées dans le multiselect avec la liste des options valides
        taches_selectionnees = st.multiselect(
            f"Tâches pour {jour}",
            options=options_taches,
            default=taches_selectionnees_valides,  # Valeurs actuelles, uniquement celles valides
            key=f"planif_{jour}"
        )
    
        # Mise à jour de la planification
        st.session_state.planifications[jour] = taches_selectionnees
        sauvegarder_planification()  # Sauvegarde après modification

    # 📌 Affichage de la planification sous forme de tableau
    st.subheader("🗓️ Vue hebdomadaire")
    
    # Vérifie que `st.session_state.planifications` existe
    if "planifications" not in st.session_state:
        st.session_state.planifications = {jour: [] for jour in jours_semaine}
    
    # Trouver le nombre maximum de tâches pour définir le nombre de lignes du tableau
    max_tasks = max(len(taches) for taches in st.session_state.planifications.values())
    
    # Reformater les données pour que chaque tâche soit sur une ligne distincte
    table = {jour: (st.session_state.planifications[jour] + [""] * (max_tasks - len(st.session_state.planifications[jour])))
             for jour in jours_semaine}
    
    # Création du DataFrame
    df = pd.DataFrame(table)
    
    # Affichage sous forme de tableau
    st.dataframe(df)

