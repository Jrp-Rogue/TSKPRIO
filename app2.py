import streamlit as st
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import requests
from git import Repo

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Tâches")

# 📌 Initialisation des tâches en session
if "taches" not in st.session_state:
    st.session_state.taches = []

# 📌 Fonction pour sauvegarder les tâches dans un fichier JSON
def sauvegarder_taches():
    with open("taches.json", "w") as f:
        json.dump(st.session_state.taches, f)
    st.success("Tâches sauvegardées dans taches.json!")
    push_to_github()  # Push vers GitHub après chaque sauvegarde

# 📌 Fonction pour charger les tâches depuis un fichier JSON
def charger_taches():
    try:
        with open("taches.json", "r") as f:
            st.session_state.taches = json.load(f)
        st.success("Tâches chargées depuis taches.json!")
    except FileNotFoundError:
        st.warning("Aucun fichier taches.json trouvé.")

# 📌 Charger les tâches si besoin
if st.button("Charger les tâches sauvegardées"):
    charger_taches()

# 📌 Fonction de push vers GitHub
def push_to_github():
    repo_path = "Jrp-Rogue/TSKPRIO"  # Le chemin de ton dépôt Git local
    repo = Repo(repo_path)
    repo.git.add('taches.json')  # Ajoute le fichier taches.json à l'index
    repo.git.commit('-m', 'Mise à jour des tâches')  # Commit des modifications
    repo.git.push()  # Effectue le push vers GitHub
    st.success("Les tâches ont été envoyées sur GitHub!")

# 📌 Formulaire pour ajouter une tâche
st.subheader("➕ Ajouter une tâche")
nom = st.text_input("Nom de la tâche :")
urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")

# 📌 Sélection des dépendances parmi les tâches existantes
options_dependances = [t["nom"] for t in st.session_state.taches]
dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances, key="dependances_add")

# 📌 Vérification des dépendances
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
        sauvegarder_taches()
        st.success(f"Tâche '{nom}' ajoutée !")
    else:
        st.error("Le nom de la tâche est requis.")

# 📌 Suppression d'une tâche
st.subheader("🗑️ Supprimer une tâche")
taches_a_supprimer = [t["nom"] for t in st.session_state.taches]
tache_a_supprimer = st.selectbox("Sélectionner une tâche à supprimer", taches_a_supprimer)

if st.button("Supprimer la tâche"):
    if tache_a_supprimer:
        st.session_state.taches = [t for t in st.session_state.taches if t["nom"] != tache_a_supprimer]
        sauvegarder_taches()
        st.success(f"Tâche '{tache_a_supprimer}' supprimée !")
    else:
        st.error("Aucune tâche sélectionnée.")

# 📌 Modification d'une tâche
st.subheader("✏️ Modifier une tâche")
tache_a_modifier = st.selectbox("Sélectionner une tâche à modifier", taches_a_supprimer)

if tache_a_modifier:
    # Récupérer la tâche à modifier
    tache_modifiee = next(t for t in st.session_state.taches if t["nom"] == tache_a_modifier)

    # Champs pour modifier les détails de la tâche
    nouveau_nom = st.text_input("Nom de la tâche", value=tache_modifiee["nom"], key="nom_modify")
    nouvelle_urgence = st.slider("Niveau d'urgence", 1, 5, tache_modifiee["urgence"], key="urgence_modify")
    nouvelle_importance = st.slider("Niveau d'importance", 1, 5, tache_modifiee["importance"], key="importance_modify")
    nouvelles_dependances = st.multiselect("Tâches dont cette tâche dépend", options_dependances, default=tache_modifiee["dependances"], key="dependances_modify")

    # Vérification des dépendances lors de la modification
    if any(dep not in options_dependances for dep in nouvelles_dependances):
        st.error("Une ou plusieurs dépendances n'existent pas dans les tâches actuelles.")

    if st.button("Modifier la tâche"):
        if nouveau_nom:
            tache_modifiee["nom"] = nouveau_nom
            tache_modifiee["urgence"] = nouvelle_urgence
            tache_modifiee["importance"] = nouvelle_importance
            tache_modifiee["dependances"] = nouvelles_dependances
            sauvegarder_taches()
            st.success(f"Tâche '{nouveau_nom}' modifiée !")
        else:
            st.error("Le nom de la tâche est requis.")

# 📌 Affichage des tâches sous forme de matrice d'Eisenhower
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

# 📌 Affichage de la matrice d'Eisenhower en visuel avec matplotlib
def afficher_matrice(matrice):
    """Affiche une matrice d'Eisenhower en visuel avec matplotlib."""
    fig, ax = plt.subplots(figsize=(10, 10))

    # Créer un fond de couleur pour chaque quadrant
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)

    # Grilles et lignes pour délimiter les quadrants
    ax.axhline(y=1, color='black', linewidth=2)
    ax.axvline(x=1, color='black', linewidth=2)

    # Définition des couleurs pour chaque quadrant
    colors = {
        'Important & Urgent': 'red', 
        'Important mais Pas Urgent': 'orange',
        'Pas Important mais Urgent': 'blue',
        'Pas Important & Pas Urgent': 'gray'
    }

    # Remplir les quadrants avec les tâches et ajouter des titres
    for categorie, taches_liste in matrice.items():
        if categorie == 'Important & Urgent':
            x, y = 0, 1
        elif categorie == 'Important mais Pas Urgent':
            x, y = 1, 1
        elif categorie == 'Pas Important mais Urgent':
            x, y = 0, 0
        else:
            x, y = 1, 0

        # Remplir chaque quadrant avec une couleur de fond
        ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[categorie], alpha=0.3))

        # Ajouter le titre du quadrant
        ax.text(x + 0.5, y + 1.05, categorie, ha='center', va='center', fontsize=12, fontweight='bold', color='black')

        # Ajouter les tâches dans chaque quadrant
        for i, tache in enumerate(taches_liste):
            ax.text(x + 0.5, y + 1.05 - (i + 1) * 0.15, tache["nom"], ha='center', va='center', fontsize=10, color='black')

    ax.set_xticks([0.5, 1.5])
    ax.set_yticks([0.5, 1.5])

    # Désactiver les axes
    ax.axis('off')

    st.pyplot(fig)

# 📌 Affichage de la matrice d'Eisenhower
st.subheader("📊 Matrice d'Eisenhower")
matrice = classifier_taches_eisenhower(st.session_state.taches)
afficher_matrice(matrice)

# 📌 Plan d'action priorisé
def prioriser_taches(taches):
    """Trie les tâches en prenant en compte l'urgence, l'importance et les dépendances."""
    
    def score(tache):
        """Calcul du score basé sur l'urgence et l'importance"""
        return tache['urgence'] * 2 + tache['importance']  # Poids plus important à l'urgence

    # Trie les tâches par score
    taches_triees = sorted(taches, key=score, reverse=True)

    # Ordonnancement des tâches en fonction des dépendances
    ordonnees = []
    while taches_triees:
        for tache in taches_triees:
            if all(dep in [t["nom"] for t in ordonnees] for dep in tache['dependances']):
                ordonnees.append(tache)
                taches_triees.remove(tache)
                break

    return ordonnees

# 📌 Affichage du plan d'action priorisé
st.subheader("📋 Plan d'Action Priorisé")
taches_ordonnee = prioriser_taches(st.session_state.taches)

for i, tache in enumerate(taches_ordonnee, 1):
    dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
    st.write(f"{i}. {tache['nom']} (Urgence: {tache['urgence']}, Importance: {tache['importance']}){dependances_str}")
