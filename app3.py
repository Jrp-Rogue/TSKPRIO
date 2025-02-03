import streamlit as st
import json
import os
import matplotlib.pyplot as plt

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Projets et de Tâches avec Priorisation")

# 📌 Initialisation des projets en session
if "projets" not in st.session_state:
    st.session_state.projets = {}

# 📌 Fichier de stockage des projets
FICHIER_PROJETS = "projets.json"

# 📌 Fonction pour sauvegarder les projets
def sauvegarder_projets():
    with open(FICHIER_PROJETS, "w") as f:
        json.dump(st.session_state.projets, f, indent=4)
    st.success("Projets sauvegardés !")

# 📌 Fonction pour charger les projets depuis un fichier JSON
def charger_projets():
    if os.path.exists(FICHIER_PROJETS) and os.path.getsize(FICHIER_PROJETS) > 0:
        try:
            with open(FICHIER_PROJETS, "r") as f:
                st.session_state.projets = json.load(f)
            st.success("Projets chargés !")
        except json.JSONDecodeError:
            st.error("Erreur lors du chargement des projets. Le fichier est peut-être corrompu.")
    else:
        st.warning("Aucun projet trouvé.")

# 📌 Charger les projets si besoin
if st.button("Charger les projets sauvegardés"):
    charger_projets()

# 📌 Sélection ou création d'un projet
st.subheader("📂 Gestion des Projets")
nouveau_projet = st.text_input("Nom du nouveau projet :")

if st.button("Créer un projet"):
    if nouveau_projet:
        if nouveau_projet not in st.session_state.projets:
            st.session_state.projets[nouveau_projet] = []
            sauvegarder_projets()
            st.success(f"Projet '{nouveau_projet}' créé !")
        else:
            st.error("Ce projet existe déjà.")
    else:
        st.error("Le nom du projet est requis.")

projet_selectionne = st.selectbox("Sélectionner un projet", list(st.session_state.projets.keys()), index=0 if st.session_state.projets else None)

if projet_selectionne:
    st.session_state.taches = st.session_state.projets[projet_selectionne]
    st.subheader(f"📌 Gestion des Tâches pour le projet '{projet_selectionne}'")
    
    # 📌 Ajout d'une tâche
    nom = st.text_input("Nom de la tâche :")
    urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
    importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")
    options_dependances = [t["nom"] for t in st.session_state.taches]
    dependances = st.multiselect("Dépendances", options_dependances, key="dependances_add")
    
    if st.button("Ajouter la tâche"):
        if nom:
            nouvelle_tache = {"nom": nom, "urgence": urgence, "importance": importance, "dependances": dependances}
            st.session_state.taches.append(nouvelle_tache)
            st.session_state.projets[projet_selectionne] = st.session_state.taches
            sauvegarder_projets()
            st.success(f"Tâche '{nom}' ajoutée !")
        else:
            st.error("Le nom de la tâche est requis.")
    
    # 📌 Suppression d'une tâche
    taches_a_supprimer = [t["nom"] for t in st.session_state.taches]
    tache_a_supprimer = st.selectbox("Sélectionner une tâche à supprimer", taches_a_supprimer, key="supp_tache")
    
    if st.button("Supprimer la tâche"):
        st.session_state.taches = [t for t in st.session_state.taches if t["nom"] != tache_a_supprimer]
        st.session_state.projets[projet_selectionne] = st.session_state.taches
        sauvegarder_projets()
        st.success(f"Tâche '{tache_a_supprimer}' supprimée !")
    
    # 📌 Matrice d'Eisenhower
    def classifier_taches_eisenhower(taches):
        matrice = {'Important & Urgent': [], 'Important mais Pas Urgent': [], 'Pas Important mais Urgent': [], 'Pas Important & Pas Urgent': []}
        for tache in taches:
            if tache['importance'] >= 3 and tache['urgence'] >= 3:
                matrice['Important & Urgent'].append(tache)
            elif tache['importance'] >= 3:
                matrice['Important mais Pas Urgent'].append(tache)
            elif tache['urgence'] >= 3:
                matrice['Pas Important mais Urgent'].append(tache)
            else:
                matrice['Pas Important & Pas Urgent'].append(tache)
        return matrice
    
    def afficher_matrice(matrice):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.axhline(y=1, color='black', linewidth=2)
        ax.axvline(x=1, color='black', linewidth=2)
        colors = {'Important & Urgent': 'red', 'Important mais Pas Urgent': 'orange', 'Pas Important mais Urgent': 'blue', 'Pas Important & Pas Urgent': 'gray'}
        for i, (categorie, taches_liste) in enumerate(matrice.items()):
            x, y = divmod(i, 2)
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[categorie], alpha=0.3))
            ax.text(x + 0.5, y + 1.05, categorie, ha='center', va='center', fontsize=12, fontweight='bold', color='black')
            for j, tache in enumerate(taches_liste):
                ax.text(x + 0.5, y + 0.9 - j * 0.15, tache["nom"], ha='center', va='center', fontsize=10, color='black')
        ax.axis('off')
        st.pyplot(fig)
    
    st.subheader("📊 Matrice d'Eisenhower")
    matrice = classifier_taches_eisenhower(st.session_state.taches)
    afficher_matrice(matrice)
    
    # 📌 Plan d'Action Priorisé
    st.subheader("📋 Plan d'Action Priorisé")
    for i, tache in enumerate(sorted(st.session_state.taches, key=lambda x: x['urgence'] * 2 + x['importance'], reverse=True), 1):
        st.write(f"{i}. {tache['nom']} (Urgence: {tache['urgence']}, Importance: {tache['importance']})")
