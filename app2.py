import streamlit as st
import matplotlib.pyplot as plt
import json
import os

# 📌 Nom du fichier pour stocker les tâches
FILE_NAME = "taches.json"

# 📌 Fonction pour charger les tâches depuis le fichier JSON
def charger_taches():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
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
menu = ["Dashboard", "Ajouter une tâche", "Modifier ou supprimer une tâche", "Matrice d'Eisenhower", "Plan d'Action"]
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

# 📌 Matrice d'Eisenhower et autres sections
# (Les autres sections de ton code restent inchangées)

