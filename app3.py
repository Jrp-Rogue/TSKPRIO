import streamlit as st
import json
import matplotlib.pyplot as plt

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Projets et Tâches")

# 📌 Initialisation des projets en session
if "projets" not in st.session_state:
    st.session_state.projets = {}

# 📌 Fonction pour sauvegarder les projets dans un fichier JSON
def sauvegarder_projets():
    with open("projets.json", "w") as f:
        json.dump(st.session_state.projets, f)
    st.success("Projets sauvegardés dans projets.json!")

# 📌 Fonction pour charger les projets depuis un fichier JSON
def charger_projets():
    try:
        with open("projets.json", "r") as f:
            st.session_state.projets = json.load(f)
        st.success("Projets chargés depuis projets.json!")
    except FileNotFoundError:
        st.warning("Aucun fichier projets.json trouvé.")

# 📌 Menu pour choisir ou créer un projet
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

# 📌 Charger les projets sauvegardés
if st.button("Charger les projets sauvegardés"):
    charger_projets()

# 📌 Sélectionner un projet pour gérer les tâches
if projet_selectionne:
    st.subheader(f"Gestion du projet: {projet_selectionne}")

    # 📌 Initialiser les tâches du projet sélectionné
    if projet_selectionne not in st.session_state.projets:
        st.session_state.projets[projet_selectionne] = []

    # 📌 Formulaire pour ajouter une tâche
    st.subheader("➕ Ajouter une tâche")
    nom = st.text_input("Nom de la tâche :")
    urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
    importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")

    # 📌 Sélection des dépendances parmi les tâches existantes
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

    # 📌 Suppression d'une tâche
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

    # 📌 Modification d'une tâche
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

    # 📌 Affichage de la matrice d'Eisenhower
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

    # 📌 Affichage de la matrice d'Eisenhower
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

    matrice = classifier_taches_eisenhower(st.session_state.projets[projet_selectionne])
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
    taches_ordonnee = prioriser_taches(st.session_state.projets[projet_selectionne])

    for i, tache in enumerate(taches_ordonnee, 1):
        dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
        st.write(f"{i}. {tache['nom']} (Urgence: {tache['urgence']}, Importance: {tache['importance']}){dependances_str}")

