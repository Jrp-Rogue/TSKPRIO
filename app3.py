import streamlit as st
import json
import matplotlib.pyplot as plt
import os
import subprocess

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Projets et Tâches avec Priorisation")

# 📌 Initialisation des projets en session
if "projets" not in st.session_state:
    st.session_state.projets = {}
if "projet_selectionne" not in st.session_state:
    st.session_state.projet_selectionne = None

# 📌 Fichiers JSON pour la sauvegarde
FICHIER_PROJETS = "projets.json"

# 📌 Fonction pour sauvegarder les projets

def sauvegarder_projets():
    """Sauvegarde les projets dans un fichier JSON et pousse sur GitHub"""
    with open(FICHIER_PROJETS, "w") as f:
        json.dump(st.session_state.projets, f)
    st.success("Projets sauvegardés !")
    
    # Exécuter le script de push GitHub en arrière-plan
    subprocess.Popen(["python", "auto_push.py"])

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

# 📌 Barre latérale pour la gestion des projets
st.sidebar.header("📂 Gestion des Projets")
projets_existants = list(st.session_state.projets.keys())
st.session_state.projet_selectionne = st.sidebar.selectbox("Sélectionner un projet", [None] + projets_existants, index=0)

# 📌 Création d'un nouveau projet
nouveau_projet = st.sidebar.text_input("Nom du nouveau projet")
if st.sidebar.button("Créer un projet") and nouveau_projet:
    if nouveau_projet not in st.session_state.projets:
        st.session_state.projets[nouveau_projet] = []
        st.session_state.projet_selectionne = nouveau_projet
        sauvegarder_projets()
        st.success(f"Projet '{nouveau_projet}' créé!")
    else:
        st.sidebar.warning(f"Le projet '{nouveau_projet}' existe déjà!")

# 📌 Bouton pour charger les projets
if st.sidebar.button("Charger les projets sauvegardés"):
    charger_projets()

# 📌 Affichage des tâches du projet sélectionné
if st.session_state.projet_selectionne:
    projet_selectionne = st.session_state.projet_selectionne
    st.subheader(f"Gestion du projet: {projet_selectionne}")

    # 📌 Ajout d'une tâche
    st.subheader("➕ Ajouter une tâche")
    nom = st.text_input("Nom de la tâche :")
    urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
    importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")
    options_dependances = [t["nom"] for t in st.session_state.projets[projet_selectionne]]
    dependances = st.multiselect("Tâches dépendantes:", options_dependances, key="dependances_add")

    if st.button("Ajouter la tâche"):
        if nom:
            nouvelle_tache = {"nom": nom, "urgence": urgence, "importance": importance, "dependances": dependances}
            st.session_state.projets[projet_selectionne].append(nouvelle_tache)
            sauvegarder_projets()
            st.success(f"Tâche '{nom}' ajoutée!")
        else:
            st.error("Le nom de la tâche est requis.")

    # 📌 Affichage et gestion des tâches sous forme de Matrice d'Eisenhower
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

    matrice = classifier_taches_eisenhower(st.session_state.projets[projet_selectionne])
    categorie_affichage = st.selectbox("Filtrer par catégorie", ["Toutes"] + list(matrice.keys()))

    for categorie, taches in matrice.items():
        if categorie_affichage == "Toutes" or categorie_affichage == categorie:
            st.subheader(categorie)
            for tache in taches:
                st.write(f"- {tache['nom']} (Urgence: {tache['urgence']}, Importance: {tache['importance']})")

    # 📌 Plan d'action priorisé
    st.subheader("📋 Plan d'Action Priorisé")
    taches_ordonnee = sorted(st.session_state.projets[projet_selectionne], key=lambda t: (t['urgence'] * 2 + t['importance']), reverse=True)
    for i, tache in enumerate(taches_ordonnee, 1):
        dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
        st.write(f"{i}. {tache['nom']} (Urgence: {tache['urgence']}, Importance: {tache['importance']}){dependances_str}")
