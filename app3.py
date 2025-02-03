import streamlit as st
import json
import os

# 📌 Nom du fichier JSON
FICHIER_JSON = "projets.json"

# 📌 Fonction pour sauvegarder les projets dans un fichier JSON
def sauvegarder_projets():
    try:
        with open(FICHIER_JSON, "w") as f:
            json.dump(st.session_state.projets, f, indent=4)
        st.success("Projets sauvegardés !")
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde : {e}")

# 📌 Fonction pour charger les projets depuis un fichier JSON
def charger_projets():
    if os.path.exists(FICHIER_JSON):
        try:
            with open(FICHIER_JSON, "r") as f:
                st.session_state.projets = json.load(f)
            st.success("Projets chargés avec succès !")
            st.rerun()
        except json.JSONDecodeError:
            st.error("Le fichier JSON est corrompu. Essayez de le supprimer et de recommencer.")
    else:
        st.warning("Aucun fichier trouvé. Commencez par créer un projet.")

# 📌 Initialisation des projets en session
if "projets" not in st.session_state:
    st.session_state.projets = {}

# 📌 Interface utilisateur
st.title("📂 Gestion des Projets")

# 📌 Charger les projets existants
if st.button("Charger les projets sauvegardés"):
    charger_projets()

# 📌 Création d'un nouveau projet
nouveau_projet = st.text_input("Nom du nouveau projet")
if st.button("Créer un projet") and nouveau_projet:
    if nouveau_projet not in st.session_state.projets:
        st.session_state.projets[nouveau_projet] = []
        sauvegarder_projets()
    else:
        st.warning("Ce projet existe déjà.")

# 📌 Sélection d'un projet existant
projets_existants = list(st.session_state.projets.keys())
projet_selectionne = st.selectbox("Sélectionnez un projet", projets_existants)

if projet_selectionne:
    st.subheader(f"Gestion des tâches pour : {projet_selectionne}")
    
    # 📌 Ajout d'une tâche
    nom_tache = st.text_input("Nom de la tâche")
    if st.button("Ajouter la tâche") and nom_tache:
        st.session_state.projets[projet_selectionne].append({"nom": nom_tache})
        sauvegarder_projets()
    
    # 📌 Affichage des tâches
    st.write("### Liste des tâches")
    for tache in st.session_state.projets[projet_selectionne]:
        st.write(f"- {tache['nom']}")
    
    # 📌 Supprimer une tâche
    tache_a_supprimer = st.selectbox("Sélectionner une tâche à supprimer", [t["nom"] for t in st.session_state.projets[projet_selectionne]])
    if st.button("Supprimer la tâche"):
        st.session_state.projets[projet_selectionne] = [t for t in st.session_state.projets[projet_selectionne] if t["nom"] != tache_a_supprimer]
        sauvegarder_projets()
        st.success("Tâche supprimée.")
