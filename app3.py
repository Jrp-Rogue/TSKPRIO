import streamlit as st
import json
import matplotlib.pyplot as plt
import numpy as np
import os

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Projets et Tâches avec Priorisation")

# 📌 Initialisation des projets en session
if "projets" not in st.session_state:
    st.session_state.projets = {}

# 📌 Fichiers JSON pour la sauvegarde
FICHIER_PROJETS = "projets.json"

# 📌 Fonction pour sauvegarder les projets dans un fichier JSON
def sauvegarder_projets():
    with open(FICHIER_PROJETS, "w") as f:
        json.dump(st.session_state.projets, f)
    st.success("Projets sauvegardés dans projets.json!")

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

# 📌 Sélection ou création d'un projet
st.subheader("📂 Sélectionner ou créer un projet")
nouveau_projet = st.text_input("Nom du nouveau projet :")
if st.button("Créer un projet"):
    if nouveau_projet and nouveau_projet not in st.session_state.projets:
        st.session_state.projets[nouveau_projet] = []
        sauvegarder_projets()
        st.success(f"Projet '{nouveau_projet}' créé !")
    elif not nouveau_projet:
        st.error("Le nom du projet est requis.")
    else:
        st.warning("Ce projet existe déjà.")

projet_selectionne = st.selectbox("Sélectionner un projet", list(st.session_state.projets.keys()), index=0 if st.session_state.projets else None)

if projet_selectionne:
    st.subheader(f"📌 Projet sélectionné : {projet_selectionne}")
    
    # 📌 Formulaire pour ajouter une tâche
    st.subheader("➕ Ajouter une tâche")
    nom = st.text_input("Nom de la tâche :")
    urgence = st.slider("Niveau d'urgence", 1, 5, 3)
    importance = st.slider("Niveau d'importance", 1, 5, 3)
    options_dependances = [t["nom"] for t in st.session_state.projets[projet_selectionne]]
    dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances)
    
    if st.button("Ajouter la tâche"):
        if nom:
            nouvelle_tache = {"nom": nom, "urgence": urgence, "importance": importance, "dependances": dependances}
            st.session_state.projets[projet_selectionne].append(nouvelle_tache)
            sauvegarder_projets()
            st.success(f"Tâche '{nom}' ajoutée !")
        else:
            st.error("Le nom de la tâche est requis.")
    
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
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.axhline(y=1, color='black', linewidth=2)
        ax.axvline(x=1, color='black', linewidth=2)
        
        colors = {
            'Important & Urgent': 'red', 
            'Important mais Pas Urgent': 'orange',
            'Pas Important mais Urgent': 'blue',
            'Pas Important & Pas Urgent': 'gray'
        }
        
        for categorie, taches_liste in matrice.items():
            x, y = (0, 1) if categorie == 'Important & Urgent' else (1, 1) if categorie == 'Important mais Pas Urgent' else (0, 0) if categorie == 'Pas Important mais Urgent' else (1, 0)
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[categorie], alpha=0.3))
            ax.text(x + 0.5, y + 1.05, categorie, ha='center', va='center', fontsize=12, fontweight='bold', color='black')
            for i, tache in enumerate(taches_liste):
                ax.text(x + 0.5, y + 1.05 - (i + 1) * 0.15, tache["nom"], ha='center', va='center', fontsize=10, color='black')
        
        ax.axis('off')
        st.pyplot(fig)

    matrice = classifier_taches_eisenhower(st.session_state.projets[projet_selectionne])
    afficher_matrice(matrice)
