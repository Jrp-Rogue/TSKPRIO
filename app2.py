import streamlit as st
import matplotlib.pyplot as plt
import json
import os

# 📌 Nom du fichier pour stocker les tâches
FILE_NAME = "taches.json"

# 📌 Fonction pour charger les tâches depuis le fichier JSON
def charger_taches():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []

# 📌 Fonction pour sauvegarder les tâches dans le fichier JSON
def sauvegarder_taches():
    with open(FILE_NAME, "w") as f:
        json.dump(st.session_state.taches, f)

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Tâches")

# 📌 Chargement des tâches depuis le fichier JSON (si elles existent)
if "taches" not in st.session_state:
    st.session_state.taches = charger_taches()

# 📌 Menu de navigation
menu = ["Dashboard", "Ajouter une tâche", "Modifier ou supprimer une tâche", "Matrice d'Eisenhower", "Plan d'Action"]
choix = st.sidebar.selectbox("Sélectionner une option", menu)

# 📌 Ajouter une tâche
if choix == "Ajouter une tâche":
    st.subheader("➕ Ajouter une tâche")
    nom = st.text_input("Nom de la tâche :")
    urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
    importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")
    
    # Sélection des dépendances parmi les tâches existantes
    options_dependances = [t["nom"] for t in st.session_state.taches]
    dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances, key="dependances_add")

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
            sauvegarder_taches()  # Sauvegarde après ajout
            st.success(f"Tâche '{nom}' ajoutée !")
        else:
            st.error("Le nom de la tâche est requis.")

# 📌 Modifier ou supprimer une tâche
elif choix == "Modifier ou supprimer une tâche":
    st.subheader("✏️ Modifier ou supprimer une tâche")
    taches_existantes = [t["nom"] for t in st.session_state.taches]
    tache_selectionnee = st.selectbox("Sélectionner une tâche", taches_existantes)

    if tache_selectionnee:
        tache_modifiee = next(t for t in st.session_state.taches if t["nom"] == tache_selectionnee)
        
        # Champs pour modifier la tâche
        nouveau_nom = st.text_input("Nom de la tâche", value=tache_modifiee["nom"], key="nom_modify")
        nouvelle_urgence = st.slider("Niveau d'urgence", 1, 5, tache_modifiee["urgence"], key="urgence_modify")
        nouvelle_importance = st.slider("Niveau d'importance", 1, 5, tache_modifiee["importance"], key="importance_modify")
        nouvelles_dependances = st.multiselect("Tâches dont cette tâche dépend", options_dependances, default=tache_modifiee["dependances"], key="dependances_modify")
        
        if any(dep not in options_dependances for dep in nouvelles_dependances):
            st.error("Une ou plusieurs dépendances n'existent pas dans les tâches actuelles.")
        
        if st.button("Modifier la tâche"):
            if nouveau_nom:
                tache_modifiee.update({"nom": nouveau_nom, "urgence": nouvelle_urgence, "importance": nouvelle_importance, "dependances": nouvelles_dependances})
                sauvegarder_taches()  # Sauvegarde après modification
                st.success(f"Tâche '{nouveau_nom}' modifiée !")
            else:
                st.error("Le nom de la tâche est requis.")
        
        if st.button("Supprimer la tâche"):
            st.session_state.taches = [t for t in st.session_state.taches if t["nom"] != tache_selectionnee]
            sauvegarder_taches()  # Sauvegarde après suppression
            st.success(f"Tâche '{tache_selectionnee}' supprimée !")

# 📌 Matrice d'Eisenhower
elif choix == "Matrice d'Eisenhower":
    st.subheader("📊 Matrice d'Eisenhower")
    
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
    
    def afficher_matrice(matrice):
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.axhline(y=1, color='black', linewidth=2)
        ax.axvline(x=1, color='black', linewidth=2)
        colors = {'Important & Urgent': 'red', 'Important mais Pas Urgent': 'orange', 'Pas Important mais Urgent': 'blue', 'Pas Important & Pas Urgent': 'gray'}
        
        for categorie, taches_liste in matrice.items():
            x, y = (0, 1) if categorie == 'Important & Urgent' else (1, 1) if categorie == 'Important mais Pas Urgent' else (0, 0) if categorie == 'Pas Important mais Urgent' else (1, 0)
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[categorie], alpha=0.3))
            ax.text(x + 0.5, y + 1.05, categorie, ha='center', va='center', fontsize=12, fontweight='bold', color='black')
            for i, tache in enumerate(taches_liste):
                ax.text(x + 0.5, y + 1.05 - (i + 1) * 0.15, tache["nom"], ha='center', va='center', fontsize=10, color='black')
        ax.set_xticks([0.5, 1.5])
        ax.set_yticks([0.5, 1.5])
        ax.axis('off')
        st.pyplot(fig)

    matrice = classifier_taches_eisenhower(st.session_state.taches)
    afficher_matrice(matrice)

# 📌 Plan d'action
elif choix == "Plan d'Action":
    st.subheader("📌 Plan d'Action")
    def prioriser_taches(taches):
    """Trie les tâches en prenant en compte la dépendance et la priorité."""
    taches_par_nom = {t['nom']: t for t in taches}

    def score(tache, visited=None):
        if visited is None:
            visited = set()
        if tache['nom'] in visited:
            return float('-inf')  # Évite les boucles infinies
        visited.add(tache['nom'])

        # Score basé sur la matrice d'Eisenhower
        if tache in matrice['🔴 Important & Urgent']:
            base_score = 4
        elif tache in matrice['🟡 Important mais Pas Urgent']:
            base_score = 3
        elif tache in matrice['🔵 Pas Important mais Urgent']:
            base_score = 2
        else:
            base_score = 1

        # Ajustement du score en fonction des dépendances
        if tache['dependances']:
            return min(score(taches_par_nom[d], visited) for d in tache['dependances']) - 1
        return base_score

    return sorted(taches, key=score, reverse=True)

st.subheader("📌 Plan d'Action Priorisé")
taches_ordonnee = prioriser_taches(st.session_state.taches)

for i, tache in enumerate(taches_ordonnee, 1):
    dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
    st.write(f"{i}. {tache['nom']} (🔴 Urgence: {tache['urgence']}, 🟢 Importance: {tache['importance']}){dependances_str}")
