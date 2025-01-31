import streamlit as st

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Tâches")

# 📌 Initialisation des tâches en session
if "taches" not in st.session_state:
    st.session_state.taches = []

# 📌 Formulaire pour ajouter une tâche
st.subheader("➕ Ajouter une tâche")
nom = st.text_input("Nom de la tâche :")
urgence = st.slider("Niveau d'urgence", 1, 5, 3)
importance = st.slider("Niveau d'importance", 1, 5, 3)

# 📌 Sélection des dépendances parmi les tâches existantes
options_dependances = [t["nom"] for t in st.session_state.taches]
dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances)

if st.button("Ajouter la tâche"):
    if nom:
        nouvelle_tache = {
            "nom": nom,
            "urgence": urgence,
            "importance": importance,
            "dependances": dependances
        }
        st.session_state.taches.append(nouvelle_tache)
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

# 📌 Affichage de la matrice d'Eisenhower
st.subheader("📊 Matrice d'Eisenhower")
matrice = classifier_taches_eisenhower(st.session_state.taches)

for categorie, liste in matrice.items():
    st.markdown(f"### {categorie}")
    for tache in liste:
        dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
        st.write(f"- {tache['nom']} (🔴 Urgence: {tache['urgence']}, 🟢 Importance: {tache['importance']}){dependances_str}")

# 📌 Plan d'action priorisé
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

# 📌 Réorganisation Manuelle
st.subheader("🔄 Réorganisation Manuelle")
nouvel_ordre = st.text_area("Réécris l’ordre des tâches en indiquant leur nom (séparés par des virgules)")

if st.button("Mettre à jour l'ordre"):
    noms_donnes = [nom.strip() for nom in nouvel_ordre.split(",") if nom.strip() in [t["nom"] for t in st.session_state.taches]]
    if len(noms_donnes) == len(st.session_state.taches):
        st.session_state.taches = sorted(st.session_state.taches, key=lambda x: noms_donnes.index(x["nom"]))
        st.success("Ordre mis à jour ! Rechargez la page pour voir l'effet.")
    else:
        st.error("Tous les noms ne correspondent pas aux tâches existantes.")

# 📌 Ajouter d'autres tâches après coup
st.subheader("➕ Ajouter d'autres tâches")
if st.button("Ajouter une nouvelle tâche"):
    st.experimental_rerun()
