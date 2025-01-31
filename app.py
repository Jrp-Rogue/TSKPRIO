import streamlit as st
import json

# 📌 Titre de l'application
st.title("📌 Gestionnaire de Tâches avec Priorisation")

# 📌 Sauvegarder les tâches dans un fichier JSON
def sauvegarder_taches():
    with open("taches.json", "w") as f:
        json.dump(st.session_state.taches, f)

# 📌 Charger les tâches depuis un fichier JSON
def charger_taches():
    try:
        with open("taches.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# 📌 Initialisation des tâches en session
if "taches" not in st.session_state:
    st.session_state.taches = charger_taches()

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
        sauvegarder_taches()  # Sauvegarder après ajout
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
    # Tri des tâches dans chaque catégorie par urgence et importance (d'abord urgence, puis importance)
    liste_triee = sorted(liste, key=lambda t: (t['urgence'], t['importance']), reverse=True)
    for tache in liste_triee:
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
        sauvegarder_taches()  # Sauvegarder après réorganisation
        st.success("Ordre mis à jour ! Rechargez la page pour voir l'effet.")
    else:
        st.error("Tous les noms ne correspondent pas aux tâches existantes.")

# 📌 Modifier une tâche
st.subheader("✏️ Modifier une tâche")
tache_a_modifier = st.selectbox("Sélectionner la tâche à modifier", [t["nom"] for t in st.session_state.taches])

if tache_a_modifier:
    # Trouver la tâche sélectionnée
    tache_selected = next((t for t in st.session_state.taches if t["nom"] == tache_a_modifier), None)
    
    if tache_selected:
        nom_modif = st.text_input("Nom de la tâche", value=tache_selected["nom"], key=f"nom_{tache_selected['nom']}")
        urgence_modif = st.slider("Niveau d'urgence", 1, 5, tache_selected["urgence"], key=f"urgence_{tache_selected['nom']}")
        importance_modif = st.slider("Niveau d'importance", 1, 5, tache_selected["importance"], key=f"importance_{tache_selected['nom']}")

        options_dependances_modif = [t["nom"] for t in st.session_state.taches]
        dependances_modif = st.multiselect("Tâches dont cette tâche dépend :", options_dependances_modif, default=tache_selected["dependances"], key=f"dependances_{tache_selected['nom']}")

        if st.button("Modifier la tâche"):
            if nom_modif:
                tache_selected["nom"] = nom_modif
                tache_selected["urgence"] = urgence_modif
                tache_selected["importance"] = importance_modif
                tache_selected["dependances"] = dependances_modif
                sauvegarder_taches()  # Sauvegarder après modification
                st.success(f"Tâche '{nom_modif}' modifiée !")
            else:
                st.error("Le nom de la tâche est requis.")





