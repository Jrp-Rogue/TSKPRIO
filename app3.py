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

    # Appel du script de push GitHub
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

# 📌 Menu Parent pour choisir et gérer les projets
st.sidebar.title("Menu Principal")
menu_principal = st.sidebar.selectbox("Sélectionner une option", ["Projets", "Gestion des tâches"])

if menu_principal == "Projets":
    st.subheader("📂 Choisir ou créer un projet")

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

    # Charger les projets sauvegardés
    if st.button("Charger les projets sauvegardés"):
        charger_projets()

    # Modification du projet sélectionné
    if projet_selectionne:
        st.subheader(f"Modification du projet: {projet_selectionne}")
        
        # Modification du nom du projet
        nouveau_nom_projet = st.text_input("Modifier le nom du projet", projet_selectionne)
        if st.button("Modifier le nom du projet"):
            if nouveau_nom_projet and nouveau_nom_projet != projet_selectionne:
                st.session_state.projets[nouveau_nom_projet] = st.session_state.projets.pop(projet_selectionne)
                sauvegarder_projets()
                st.success(f"Nom du projet modifié en '{nouveau_nom_projet}'!")
        
        # Suppression du projet
        if st.button("Supprimer le projet"):
            if st.radio("Êtes-vous sûr de vouloir supprimer ce projet ?", ["Non", "Oui"]) == "Oui":
                del st.session_state.projets[projet_selectionne]
                sauvegarder_projets()
                st.success(f"Projet '{projet_selectionne}' supprimé!")
                projet_selectionne = None  # Désélectionner le projet supprimé
                # Recharger les projets après suppression
                charger_projets()

# 📌 Gestion des tâches pour un projet sélectionné
if menu_principal == "Gestion des tâches" and projet_selectionne:
    st.subheader(f"Gestion du projet: {projet_selectionne}")

    # Initialiser les tâches du projet sélectionné
    if projet_selectionne not in st.session_state.projets:
        st.session_state.projets[projet_selectionne] = []

    # Formulaire pour ajouter une tâche
    st.subheader("➕ Ajouter une tâche")
    nom = st.text_input("Nom de la tâche :")
    urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
    importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")

    # Sélection des dépendances parmi les tâches existantes
    options_dependances = [t["nom"] for t in st.session_state.projets[projet_selectionne]]
    dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances, key="dependances_add")

    if st.button("Ajouter la tâche"):
        if nom:
            nouvelle_tache = {
                "nom": nom,
                "urgence": urgence,
                "importance": importance,
                "dependances": dependances
            }
            st.session_state.projets[projet_selectionne].append(nouvelle_tache)
            sauvegarder_projets()
            st.success(f"Tâche '{nom}' ajoutée au projet '{projet_selectionne}'!")
        else:
            st.error("Le nom de la tâche est requis.")

    # Suppression d'une tâche
    st.subheader("🗑️ Supprimer une tâche")
    taches_a_supprimer = [t["nom"] for t in st.session_state.projets[projet_selectionne]]
    tache_a_supprimer = st.selectbox("Sélectionner une tâche à supprimer", taches_a_supprimer)

    if st.button("Supprimer la tâche"):
        if tache_a_supprimer:
            st.session_state.projets[projet_selectionne] = [t for t in st.session_state.projets[projet_selectionne] if t["nom"] != tache_a_supprimer]
            sauvegarder_projets()
            st.success(f"Tâche '{tache_a_supprimer}' supprimée du projet '{projet_selectionne}'!")
        else:
            st.error("Aucune tâche sélectionnée.")

    # Modification d'une tâche
    st.subheader("✏️ Modifier une tâche")
    tache_a_modifier = st.selectbox("Sélectionner une tâche à modifier", taches_a_supprimer)

    if tache_a_modifier:
        # Récupérer la tâche à modifier
        tache_modifiee = next(t for t in st.session_state.projets[projet_selectionne] if t["nom"] == tache_a_modifier)

        # Champs pour modifier les détails de la tâche
        nouveau_nom = st.text_input("Nom de la tâche", value=tache_modifiee["nom"], key="nom_modify")
        nouvelle_urgence = st.slider("Niveau d'urgence", 1, 5, tache_modifiee["urgence"], key="urgence_modify")
        nouvelle_importance = st.slider("Niveau d'importance", 1, 5, tache_modifiee["importance"], key="importance_modify")
        nouvelles_dependances = st.multiselect("Tâches dont cette tâche dépend", options_dependances, default=tache_modifiee["dependances"], key="dependances_modify")

        if st.button("Modifier la tâche"):
            if nouveau_nom:
                tache_modifiee["nom"] = nouveau_nom
                tache_modifiee["urgence"] = nouvelle_urgence
                tache_modifiee["importance"] = nouvelle_importance
                tache_modifiee["dependances"] = nouvelles_dependances
                sauvegarder_projets()
                st.success(f"Tâche '{nouveau_nom}' modifiée dans le projet '{projet_selectionne}'!")
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
    
    # 📌 Plan d'action
    def generer_plan_action(matrice):
        plan = []
        for categorie, taches_liste in matrice.items():
            if categorie == "Important & Urgent":
                plan.append(f"Prioriser les tâches dans '{categorie}'")
            elif categorie == "Important mais Pas Urgent":
                plan.append(f"Planifier les tâches dans '{categorie}'")
            else:
                plan.append(f"Éviter les tâches dans '{categorie}'")
        return plan

    plan_action = generer_plan_action(matrice)
    st.subheader("Plan d'Action")
    st.write("\n".join(plan_action))

