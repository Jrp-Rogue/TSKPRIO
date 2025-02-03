import streamlit as st
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Projets et Tâches avec Priorisation")

# 📌 Initialisation des projets en session
if "projets" not in st.session_state:
    st.session_state.projets = {}

# 📌 Fichiers JSON pour la sauvegarde
FICHIER_PROJETS = "projets.json"

# 📌 Fonction pour sauvegarder les projets dans un fichier JSON
def sauvegarder_projets():
    """Sauvegarde les projets dans un fichier JSON et pousse sur GitHub"""
    with open(FICHIER_PROJETS, "w") as f:
        json.dump(st.session_state.projets, f)
    
    st.success("Projets sauvegardés !")
    subprocess.run(["python", "auto_push.py"], check=True)

# 📌 Fonction pour charger les projets depuis un fichier JSON
def charger_projets():
    if os.path.exists(FICHIER_PROJETS) and os.path.getsize(FICHIER_PROJETS) > 0:
        try:
            with open(FICHIER_PROJETS, "r") as f:
                st.session_state.projets = json.load(f)
            st.success("Projets chargés depuis projets.json!")
        except json.JSONDecodeError:
            st.warning("Erreur de lecture du fichier JSON. Le fichier est peut-être corrompu.")
    else:
        st.warning("Aucun fichier projets.json trouvé ou il est vide.")

# 📌 Charger les projets si besoin
if st.button("Charger les projets sauvegardés"):
    charger_projets()

# 📌 Menu pour gérer les projets
st.subheader("📂 Gérer les projets")

# Liste des projets existants
projets_existants = list(st.session_state.projets.keys())
projet_selectionne = st.selectbox("Sélectionner un projet existant", projets_existants)

# Création d'un nouveau projet
nouveau_projet = st.text_input("Nom du nouveau projet")
if st.button("Créer un nouveau projet") and nouveau_projet:
    if nouveau_projet not in st.session_state.projets:
        st.session_state.projets[nouveau_projet] = []
        sauvegarder_projets()
        st.success(f"Projet '{nouveau_projet}' créé!")
    else:
        st.warning(f"Le projet '{nouveau_projet}' existe déjà!")

# Modification d'un projet
if projet_selectionne:
    nouveau_nom_projet = st.text_input("Modifier le nom du projet", projet_selectionne)
    if st.button("Modifier le projet") and nouveau_nom_projet:
        if nouveau_nom_projet not in st.session_state.projets:
            st.session_state.projets[nouveau_nom_projet] = st.session_state.projets.pop(projet_selectionne)
            sauvegarder_projets()
            st.success(f"Projet renommé en '{nouveau_nom_projet}'!")
        else:
            st.warning("Un projet avec ce nom existe déjà.")

    # Suppression d'un projet
    if st.button("Supprimer le projet"):
        del st.session_state.projets[projet_selectionne]
        sauvegarder_projets()
        st.success(f"Projet '{projet_selectionne}' supprimé!")

# 📌 Gestion des tâches
if projet_selectionne:
    st.subheader(f"Gestion du projet: {projet_selectionne}")

    # 📌 Ajout, modification et suppression de tâches (Fonctionnalités inchangées)
    
    # 📌 Matrice d'Eisenhower
    def classifier_taches_eisenhower(taches):
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
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.axhline(y=1, color='black', linewidth=2)
        ax.axvline(x=1, color='black', linewidth=2)
        
        quadrants = {
            'Important & Urgent': (1, 1),
            'Important mais Pas Urgent': (0, 1),
            'Pas Important mais Urgent': (1, 0),
            'Pas Important & Pas Urgent': (0, 0)
        }
        
        colors = {
            'Important & Urgent': 'red', 
            'Important mais Pas Urgent': 'orange',
            'Pas Important mais Urgent': 'blue',
            'Pas Important & Pas Urgent': 'gray'
        }
        
        for categorie, (x, y) in quadrants.items():
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[categorie], alpha=0.3))
            ax.text(x + 0.5, y + 0.9, categorie, ha='center', va='center', fontsize=12, fontweight='bold', color='black')
            for i, tache in enumerate(matrice[categorie]):
                ax.text(x + 0.5, y + 0.7 - (i * 0.15), tache["nom"], ha='center', va='center', fontsize=10, color='black')
        
        ax.axis('off')
        st.pyplot(fig)

    matrice = classifier_taches_eisenhower(st.session_state.projets[projet_selectionne])
    afficher_matrice(matrice)
