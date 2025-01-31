import streamlit as st
import json
import matplotlib.pyplot as plt
import numpy as np

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

# 📌 Formulaire pour ajouter une tâche
st.subheader("➕ Ajouter une tâche")
nom = st.text_input("Nom de la tâche :")
urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")

# 📌 Sélection des dépendances parmi les tâches existantes
options_dependances = [t["nom"] for t in st.session_state.taches]
dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances, key="dependances_add")

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

# 📌 Affichage des tâches sous forme de matrice d'Eisenhower
def classifier_taches_eisenhower(taches):
    """Classe les tâches selon la matrice d'Eisenhower"""
    matrice = {
        '🔴 Important & Urgent': [],
        '🟡 Important mais Pas Urgent': [],
        '🔵 Pas Important mais Urgent': [],
        '⚪ Pas Important & Pas Urgent': []
    }
    for tache in taches:
        if tache['importance'] >= 3 and tache['urgence'] >= 3:
            matrice['🔴 Important & Urgent'].append(tache)
        elif tache['importance'] >= 3 and tache['urgence'] < 3:
            matrice['🟡 Important mais Pas Urgent'].append(tache)
        elif tache['importance'] < 3 and tache['urgence'] >= 3:
            matrice['🔵 Pas Important mais Urgent'].append(tache)
        else:
            matrice['⚪ Pas Important & Pas Urgent'].append(tache)
    return matrice

# 📌 Affichage de la matrice d'Eisenhower en visuel avec matplotlib
def afficher_matrice(matrice):
    """Affiche une matrice d'Eisenhower en visuel avec matplotlib."""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_xticks([0.5, 1.5])
    ax.set_yticks([0.5, 1.5])
    
    ax.axhline(y=1, color='black', linewidth=2)
    ax.axvline(x=1, color='black', linewidth=2)
    
    ax.text(0.25, 1.75, "🔴 Important & Urgent", ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(1.75, 1.75, "🟡 Important mais Pas Urgent", ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(0.25, 0.25, "🔵 Pas Important mais Urgent", ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(1.75, 0.25, "⚪ Pas Important & Pas Urgent", ha='center', va='center', fontsize=12, fontweight='bold')

    # Remplir les quadrants avec les tâches
    for categorie, taches_liste in matrice.items():
        for tache in taches_liste:
            if categorie == '🔴 Important & Urgent':
                ax.text(0.25, 1.5, tache["nom"], ha='center', va='center', fontsize=10, color='red')
            elif categorie == '🟡 Important mais Pas Urgent':
                ax.text(1.75, 1.5, tache["nom"], ha='center', va='center', fontsize=10, color='orange')
            elif categorie == '🔵 Pas Important mais Urgent':
                ax.text(0.25, 0.25, tache["nom"], ha='center', va='center', fontsize=10, color='blue')
            elif categorie == '⚪ Pas Important & Pas Urgent':
                ax.text(1.75, 0.25, tache["nom"], ha='center', va='center', fontsize=10, color='gray')

    st.pyplot(fig)

# 📌 Affichage de la matrice d'Eisenhower
st.subheader("📊 Matrice d'Eisenhower")
matrice = classifier_taches_eisenhower(st.session_state.taches)
afficher_matrice(matrice)

# 📌 Modification de tâche existante
st.subheader("✏️ Modifier une tâche")
taches_existantes = [t["nom"] for t in st.session_state.taches]
tache_a_modifier = st.selectbox("Sélectionner une tâche à modifier", taches_existantes)

if tache_a_modifier:
    tache_modifiee = next(t for t in st.session_state.taches if t["nom"] == tache_a_modifier)
    
    # Récupérer les valeurs actuelles pour pré-remplir
    nom_modifie = st.text_input("Nom de la tâche", tache_modifiee["nom"])
    urgence_modifie = st.slider("Niveau d'urgence", 1, 5, tache_modifiee["urgence"], key="urgence_mod")
    importance_modifie = st.slider("Niveau d'importance", 1, 5, tache_modifiee["importance"], key="importance_mod")
    dependances_modifiees = st.multiselect("Tâches dont cette tâche dépend :", options_dependances, default=tache_modifiee["dependances"], key="dependances_mod")
    
    if st.button("Modifier la tâche"):
        tache_modifiee["nom"] = nom_modifie
        tache_modifiee["urgence"] = urgence_modifie
        tache_modifiee["importance"] = importance_modifie
        tache_modifiee["dependances"] = dependances_modifiees
        sauvegarder_taches()
        st.success(f"Tâche '{nom_modifie}' modifiée !")

# 📌 Suppression de tâche
st.subheader("🗑️ Supprimer une tâche")
tache_a_supprimer = st.selectbox("Sélectionner une tâche à supprimer", taches_existantes)

if st.button("Supprimer la tâche"):
    if tache_a_supprimer:
        st.session_state.taches = [t for t in st.session_state.taches if t["nom"] != tache_a_supprimer]
        sauvegarder_taches()
        st.success(f"Tâche '{tache_a_supprimer}' supprimée !")

# 📌 Réorganisation Manuelle
st.subheader("🔄 Réorganisation Manuelle")
nouvel_ordre = st.text_area("Réécris l’ordre des tâches en indiquant leur nom (séparés par des virgules)")

if st.button("Mettre à jour l'ordre"):
    noms_donnes = [nom.strip() for nom in nouvel_ordre.split(",") if nom.strip() in [t["nom"] for t in st.session_state.taches]]
    if len(noms_donnes) == len(st.session_state.taches):
        st.session_state.taches = sorted(st.session_state.taches, key=lambda x: noms_donnes.index(x["nom"]))
        sauvegarder_taches()
        st.success("Ordre mis à jour ! Rechargez la page pour voir l'effet.")
    else:
        st.error("Tous les noms ne correspondent pas aux tâches existantes.")
