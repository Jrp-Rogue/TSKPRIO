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

# 📌 Initialisation correcte des tâches dans session_state
if "taches" not in st.session_state:
    st.session_state.taches = []

# 📌 Ajouter une tâche
if choix == "Ajouter une tâche":
    st.subheader("➕ Ajouter une tâche")

    # 📌 Saisie du nom
    nom = st.text_input("Nom de la tâche :").strip()

    # 📌 Sélection des niveaux d'urgence et d'importance
    urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
    importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")

    # 📌 Sélection des dépendances parmi les tâches existantes
    options_dependances = [t["nom"] for t in st.session_state.taches]
    dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances, key="dependances_add")

    # 🔍 Vérifications et feedback utilisateur
    erreur = None

    if not nom:
        erreur = "Le nom de la tâche est requis."
    elif any(dep not in options_dependances for dep in dependances):
        erreur = "Une ou plusieurs dépendances sélectionnées n'existent pas."
    elif any(t["nom"].strip().lower() == nom.lower() for t in st.session_state.taches):  # Vérifie existence sans espaces parasites
        erreur = f"Une tâche avec le nom '{nom}' existe déjà !"

    # 🔘 Bouton d'ajout (désactivé si erreur)
    if st.button("Ajouter la tâche", disabled=bool(erreur)):
        nouvelle_tache = {
            "nom": nom,
            "urgence": urgence,
            "importance": importance,
            "dependances": dependances
        }
        st.session_state.taches.append(nouvelle_tache)
        sauvegarder_taches()  # Sauvegarde après ajout ✅
        st.success(f"Tâche '{nom}' ajoutée !")

    # Affichage de l'erreur si besoin
    if erreur:
        st.error(erreur)

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
    import matplotlib.pyplot as plt
    import textwrap

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
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)

        # Grille de la matrice
        ax.axhline(y=1, color='black', linewidth=2)
        ax.axvline(x=1, color='black', linewidth=2)

        colors = {
            'Important & Urgent': 'red',
            'Important mais Pas Urgent': 'orange',
            'Pas Important mais Urgent': 'blue',
            'Pas Important & Pas Urgent': 'gray'
        }

        positions = {
            'Important & Urgent': (0, 1),
            'Important mais Pas Urgent': (1, 1),
            'Pas Important mais Urgent': (0, 0),
            'Pas Important & Pas Urgent': (1, 0)
        }

        for categorie, taches_liste in matrice.items():
            x, y = positions[categorie]

            # Ajout des couleurs de fond
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[categorie], alpha=0.2))

            # Affichage des tâches par catégorie
            for idx, tache in enumerate(taches_liste):
                ax.text(x + 0.1, y + 0.1 + idx * 0.15, 
                        f"{tache['nom']}", 
                        ha='left', va='top', fontsize=10, 
                        wrap=True)

        ax.set_title("Matrice d'Eisenhower", fontsize=14)
        ax.set_xticks([0.5, 1.5])
        ax.set_xticklabels(['Urgent', 'Pas Urgent'])
        ax.set_yticks([0.5, 1.5])
        ax.set_yticklabels(['Pas Important', 'Important'])
        ax.axis('off')
        st.pyplot(fig)

    matrice = classifier_taches_eisenhower(st.session_state.taches)
    afficher_matrice(matrice)

# 📌 Plan d'action
elif choix == "Plan d'Action":
    st.subheader("📝 Plan d'Action")
    st.write("Dans cette section, tu peux élaborer un plan d'action pour chaque tâche.")
    # Ajouter un formulaire d'action détaillée si nécessaire
    pass

# 📌 Planification hebdomadaire
elif choix == "Planification Hebdomadaire":
    st.subheader("🗓️ Planification Hebdomadaire")

    # 📌 Charger ou initialiser la planification
    if "planifications" not in st.session_state:
        st.session_state.planifications = charger_planification()

    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    
    for jour in jours:
        st.write(f"### {jour}")
        taches_jour = st.session_state.planifications.get(jour, [])
        taches_jour = sorted(taches_jour, key=lambda t: (t["urgence"], t["importance"]), reverse=True)  # Tri selon la priorité

        for t in taches_jour:
            st.write(f"- {t['nom']} (Urgence: {t['urgence']}, Importance: {t['importance']})")

        # 📌 Option pour ajouter une tâche au jour en cours
        tache_selectionnee = st.selectbox(f"Ajouter une tâche pour {jour}", [t["nom"] for t in st.session_state.taches])

        if st.button(f"Ajouter une tâche pour {jour}"):
            if tache_selectionnee:
                tache_ajoutee = next(t for t in st.session_state.taches if t["nom"] == tache_selectionnee)
                st.session_state.planifications[jour].append(tache_ajoutee)
                sauvegarder_planification() 
                st.success(f"Tâche '{tache_ajoutee['nom']}' ajoutée à la planification de {jour}!")
