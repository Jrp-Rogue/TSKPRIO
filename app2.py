import streamlit as st
import json
import matplotlib.pyplot as plt
import numpy as np

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Tâches avec Priorisation")

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
    """Trie les tâches en prenant en compte la priorité et les dépendances."""
    taches_par_nom = {t['nom']: t for t in taches}

    def score(tache, visited=None):
        if visited is None:
            visited = set()
        if tache['nom'] in visited:
            return float('-inf')  # Évite les boucles infinies
        visited.add(tache['nom'])

        # Score basé sur la matrice d'Eisenhower
        if tache in matrice['Important & Urgent']:
            base_score = 4
        elif tache in matrice['Important mais Pas Urgent']:
            base_score = 3
        elif tache in matrice['Pas Important mais Urgent']:
            base_score = 2
        else:
            base_score = 1

        # Ajustement du score en fonction des dépendances
        if tache['dependances']:
            return min(score(taches_par_nom[d], visited) for d in tache['dependances']) - 1
        return base_score

    return sorted(taches, key=score, reverse=True)

# 📌 Affichage du plan d'action priorisé
st.subheader("📋 Plan d'Action Priorisé")
taches_ordonnee = prioriser_taches(st.session_state.taches)

for i, tache in enumerate(taches_ordonnee, 1):
    dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
    st.write(f"{i}. {tache['nom']} (Urgence: {tache['urgence']}, Importance: {tache['importance']}){dependances_str}")



