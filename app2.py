import streamlit as st
import json
import os
import pandas as pd

# 📌 Nom du fichier pour stocker les tâches
FILE_NAME = "taches.json"

# 📌 Fonction pour charger les tâches depuis le fichier JSON
def charger_taches():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            try:
                # Tente de charger le contenu JSON
                return json.load(f)
            except json.JSONDecodeError:
                # Si le fichier est corrompu ou vide, retourne une liste vide
                st.error("Erreur de format JSON, le fichier est peut-être corrompu ou vide.")
                return []
    return []

# 📌 Fonction pour sauvegarder les tâches dans le fichier JSON
def sauvegarder_taches():
    with open(FILE_NAME, "w") as f:
        json.dump(st.session_state.taches, f)

# 📌 Nom du fichier pour stocker la planification
PLANIF_FILE = "planifications.json"

# 📌 Fonction pour charger la planification depuis le fichier JSON
def charger_planification():
    if os.path.exists(PLANIF_FILE):
        with open(PLANIF_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                st.error("Erreur de format JSON dans la planification.")
                return {jour: [] for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]}
    return {jour: [] for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]}

# 📌 Fonction pour sauvegarder la planification dans le fichier JSON
def sauvegarder_planification():
    with open(PLANIF_FILE, "w") as f:
        json.dump(st.session_state.planifications, f)
        
def upadate_json_files():
    with open(FILE_NAME, "W") as f:
        json.dump(st.session_state.taches, f)
    with open(PLANIF_FILE, "w") as f:
        json.dump(st.sessoin_state.planifications, f)
        
# 📌 Titre de l'application
st.title("📌 Gestionnaire de Tâches")

# 📌 Chargement des tâches depuis le fichier JSON (si elles existent)
if "taches" not in st.session_state:
    st.session_state.taches = charger_taches()

# 📌 Menu de navigation
menu = ["Ajouter une tâche", "Modifier ou supprimer une tâche", "Matrice d'Eisenhower", "Plan d'Action", "Planification Hebdomadaire"]
choix = st.sidebar.selectbox("Sélectionner une option", menu)

import streamlit as st

# 📌 Initialisation correcte des tâches dans session_state
if "taches" not in st.session_state:
    st.session_state.taches = []

# 📌 Ajouter une tâche
if choix == "Ajouter une tâche":
    st.subheader("➕ Ajouter une tâche")

    # 📌 Saisie du nom
    nom = st.text_input("Nom de la tâche :").strip()

    # 📌 Sélection des niveaux d'urgence et d'importance
    urgence = st.slider("Niveau d'urgence", 1, 5, 3, key="urgence_add")
    importance = st.slider("Niveau d'importance", 1, 5, 3, key="importance_add")

    # 📌 Sélection des dépendances parmi les tâches existantes
    options_dependances = [t["nom"] for t in st.session_state.taches]
    dependances = st.multiselect("Tâches dont cette tâche dépend :", options_dependances, key="dependances_add")

    # 🔍 Vérifications et feedback utilisateur
    erreur = None

    if not nom:
        erreur = "Le nom de la tâche est requis."
    elif any(dep not in options_dependances for dep in dependances):
        erreur = "Une ou plusieurs dépendances sélectionnées n'existent pas."
    elif any(t["nom"].strip().lower() == nom.lower() for t in st.session_state.taches):  # Vérifie existence sans espaces parasites
        erreur = f"Une tâche avec le nom '{nom}' existe déjà !"

    # 🔘 Bouton d'ajout (désactivé si erreur)
    if st.button("Ajouter la tâche", disabled=bool(erreur)):
        nouvelle_tache = {
            "nom": nom,
            "urgence": urgence,
            "importance": importance,
            "dependances": dependances
        }
        st.session_state.taches.append(nouvelle_tache)
        update_json_files()
        st.success(f"Tâche '{nom}' ajoutée !")
        
 

    # Affichage de l'erreur si besoin
    if erreur:
        st.error(erreur)



# 📌 Modifier ou supprimer une tâche
elif choix == "Modifier ou supprimer une tâche":
    st.subheader("✏️ Modifier ou supprimer une tâche")

    if not st.session_state.taches:
        st.warning("Aucune tâche disponible.")
        st.stop()

    taches_existantes = [t["nom"] for t in st.session_state.taches]
    tache_selectionnee = st.selectbox("Sélectionner une tâche", taches_existantes)

    if tache_selectionnee:
        # Copie de la tâche sélectionnée
        tache_modifiee = next(t for t in st.session_state.taches if t["nom"] == tache_selectionnee)
        tache_temp = tache_modifiee.copy()  # Éviter les modifications directes avant validation

        # Champs de modification
        tache_temp["nom"] = st.text_input("Nom de la tâche", value=tache_modifiee["nom"], key="nom_modify")
        tache_temp["urgence"] = st.slider("Niveau d'urgence", 1, 5, tache_modifiee["urgence"], key="urgence_modify")
        tache_temp["importance"] = st.slider("Niveau d'importance", 1, 5, tache_modifiee["importance"], key="importance_modify")

        # Dépendances
        options_dependances = [t["nom"] for t in st.session_state.taches if t["nom"] != tache_modifiee["nom"]]
        tache_temp["dependances"] = st.multiselect(
            "Tâches dont cette tâche dépend", 
            options_dependances, 
            default=tache_modifiee["dependances"], 
            key="dependances_modify"
        )

        if any(dep not in options_dependances for dep in tache_temp["dependances"]):
            st.error("Une ou plusieurs dépendances n'existent pas dans les tâches actuelles.")

        # Modification de la tâche
        if st.button("Modifier la tâche"):
            if tache_temp["nom"].strip():
                index = st.session_state.taches.index(tache_modifiee)
                st.session_state.taches[index] = tache_temp  # Remplacement dans la liste
                update_json_files()
                st.success(f"Tâche '{tache_temp['nom']}' modifiée !")
                st.rerun()
            else:
                st.error("Le nom de la tâche est requis.")

        # Suppression de la tâche (avec vérification des dépendances)
        if st.button("Supprimer la tâche"):
            taches_dependantes = [t["nom"] for t in st.session_state.taches if tache_selectionnee in t["dependances"]]

            if taches_dependantes:
                st.error(f"Impossible de supprimer cette tâche. Elle est une dépendance pour : {', '.join(taches_dependantes)}.")
            else:
                st.session_state.taches = [t for t in st.session_state.taches if t["nom"] != tache_selectionnee]
                update_json_files()
                st.success(f"Tâche '{tache_selectionnee}' supprimée !")
                st.rerun()


# 📌 Matrice d'Eisenhower
elif choix == "Matrice d'Eisenhower":
    import matplotlib.pyplot as plt
    import textwrap

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
        
        # Grille de la matrice
        ax.axhline(y=1, color='black', linewidth=2)
        ax.axvline(x=1, color='black', linewidth=2)
        
        colors = {
            'Important & Urgent': 'red',
            'Important mais Pas Urgent': 'orange',
            'Pas Important mais Urgent': 'blue',
            'Pas Important & Pas Urgent': 'gray'
        }
        
        positions = {
            'Important & Urgent': (0, 1),
            'Important mais Pas Urgent': (1, 1),
            'Pas Important mais Urgent': (0, 0),
            'Pas Important & Pas Urgent': (1, 0)
        }

        for categorie, taches_liste in matrice.items():
            x, y = positions[categorie]
            
            # Ajout des couleurs de fond
            ax.add_patch(plt.Rectangle((x, y), 1, 1, color=colors[categorie], alpha=0.3, edgecolor="black", linewidth=2))

            # Titre de chaque section
            ax.text(x + 0.5, y + 0.9, categorie, ha='center', va='center', fontsize=12, fontweight='bold', color='black')

            # 🔹 Gestion automatique du placement des tâches
            max_tasks = 6  # Nombre max de tâches affichées par case
            task_spacing = 0.12 if len(taches_liste) <= max_tasks else 0.08  # Ajustement de l'espace
            
            for i, tache in enumerate(taches_liste[:max_tasks]):  # Affiche max `max_tasks` tâches
                offset_y = 0.75 - (i * task_spacing)
                wrapped_text = "\n".join(textwrap.wrap(tache["nom"], width=20))  # Coupe les noms trop longs
                ax.text(x + 0.5, y + offset_y, wrapped_text, ha='center', va='center', fontsize=10, color='black')

            # Si trop de tâches, affiche "et X autres..."
            if len(taches_liste) > max_tasks:
                ax.text(x + 0.5, y + 0.75 - (max_tasks * task_spacing), f"...et {len(taches_liste) - max_tasks} autres",
                        ha='center', va='center', fontsize=9, color='black', fontweight='bold')

        # Masque les axes
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')

        # Ajout d'une légende
        legend_labels = [
            ("Rouge", "A faire"),
            ("Orange", "A planifier"),
            ("Bleu", "A déléguer"),
            ("Gris", "A abandonner")
        ]
        for i, (color, label) in enumerate(legend_labels):
            ax.text(0.5, -0.2 - (i * 0.08), f"{color} : {label}", ha="center", va="center", fontsize=10, color='black')

        st.pyplot(fig)

    if "taches" in st.session_state and len(st.session_state.taches) > 0:
        matrice = classifier_taches_eisenhower(st.session_state.taches)
        afficher_matrice(matrice)
    else:
        st.error("Aucune tâche disponible pour classer.")

# 📌 Plan d'Action
elif choix == "Plan d'Action":
    st.subheader("📌 Plan d'Action")

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

    def prioriser_taches(taches, matrice):
        """Trie les tâches en fonction de leur priorité Eisenhower et des dépendances"""
        taches_par_nom = {t['nom']: t for t in taches}

        # Score basé sur importance & urgence
        def score_eisenhower(tache):
            return tache['importance'] * 10 + tache['urgence']  # Pondération pour éviter égalités

        # Construire le graphe des dépendances
        dependencies = {t['nom']: set(t['dependances']) for t in taches}
        dependants = {t['nom']: set() for t in taches}
        for t in taches:
            for d in t['dependances']:
                dependants[d].add(t['nom'])

        # Liste des tâches triées en priorité Eisenhower
        taches_triees = sorted(taches, key=score_eisenhower, reverse=True)

        # Liste finale et tâches prêtes à être placées
        ordre_final = []
        pretes = [t for t in taches_triees if not dependencies[t['nom']]]

        while pretes:
            # Trier les tâches prêtes selon leur score Eisenhower (priorité absolue)
            pretes.sort(key=score_eisenhower, reverse=True)
            tache = pretes.pop(0)
            ordre_final.append(tache)

            # Libérer les tâches dépendantes maintenant que celle-ci est placée
            for dependant in dependants[tache['nom']]:
                dependencies[dependant].remove(tache['nom'])
                if not dependencies[dependant]:  # Si plus de dépendances, elle devient "prête"
                    pretes.append(taches_par_nom[dependant])

        if len(ordre_final) != len(taches):  # Détection de boucles de dépendances
            st.error("⚠️ Dépendances circulaires détectées ! Vérifiez les tâches.")
            return []

        return ordre_final

    # 📊 Génération de la matrice d'Eisenhower
    matrice = classifier_taches_eisenhower(st.session_state.taches)
    
    # 📋 Priorisation des tâches en fonction de la matrice d'Eisenhower et des dépendances
    taches_ordonnee = prioriser_taches(st.session_state.taches, matrice)

    # 📝 Affichage des tâches priorisées
    if taches_ordonnee:
        for i, tache in enumerate(taches_ordonnee, 1):
            dependances_str = f" (Dépend de: {', '.join(tache['dependances'])})" if tache['dependances'] else ""
            st.write(f"{i}. {tache['nom']} (🔴 Urgence: {tache['urgence']}, 🟢 Importance: {tache['importance']}){dependances_str}")
    else:
        st.warning("Aucune tâche à afficher ou problème détecté dans les dépendances.")

# 📅 Planification hebdomadaire
elif choix == "Planification Hebdomadaire":
    st.subheader("📅 Planification Hebdomadaire")

    jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    # Initialisation de l'état si non existant
    if "planifications" not in st.session_state:
        st.session_state.planifications = charger_planification()

    # Interface pour assigner les tâches aux jours
    for jour in jours_semaine:
        # Liste des tâches disponibles
        options_taches = [t["nom"] for t in st.session_state.taches]
        
        # Récupère les tâches sélectionnées pour ce jour, et filtre les tâches supprimées
        taches_selectionnees = st.session_state.planifications[jour]
        taches_selectionnees_valides = [tache for tache in taches_selectionnees if tache in options_taches]
    
        # Met à jour les tâches sélectionnées dans le multiselect avec la liste des options valides
        taches_selectionnees = st.multiselect(
            f"Tâches pour {jour}",
            options=options_taches,
            default=taches_selectionnees_valides,  # Valeurs actuelles, uniquement celles valides
            key=f"planif_{jour}"
        )
    
        # Mise à jour de la planification
        st.session_state.planifications[jour] = taches_selectionnees
        update_json_files()  # Sauvegarde après modification

    # 📌 Affichage de la planification sous forme de tableau
    st.subheader("🗓️ Vue hebdomadaire")

    # Pour afficher le tableau en tenant compte de la priorisation (dépendances comprises),
    # on définit ici les mêmes fonctions que dans "Plan d'Action".
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

    def prioriser_taches(taches, matrice):
        """Trie les tâches en fonction de leur priorité Eisenhower et des dépendances"""
        taches_par_nom = {t['nom']: t for t in taches}

        def score_eisenhower(tache):
            return tache['importance'] * 10 + tache['urgence']

        dependencies = {t['nom']: set(t['dependances']) for t in taches}
        dependants = {t['nom']: set() for t in taches}
        for t in taches:
            for d in t['dependances']:
                dependants[d].add(t['nom'])

        taches_triees = sorted(taches, key=score_eisenhower, reverse=True)
        ordre_final = []
        pretes = [t for t in taches_triees if not dependencies[t['nom']]]

        while pretes:
            pretes.sort(key=score_eisenhower, reverse=True)
            tache = pretes.pop(0)
            ordre_final.append(tache)
            for dependant in dependants[tache['nom']]:
                dependencies[dependant].remove(tache['nom'])
                if not dependencies[dependant]:
                    pretes.append(taches_par_nom[dependant])

        if len(ordre_final) != len(taches):
            st.error("⚠️ Dépendances circulaires détectées ! Vérifiez les tâches.")
            return []

        return ordre_final

    # Calcul de l'ordre global de priorisation pour toutes les tâches
    matrice = classifier_taches_eisenhower(st.session_state.taches)
    taches_ordonnee = prioriser_taches(st.session_state.taches, matrice)

    # Pour chaque jour, trier les tâches planifiées selon leur ordre dans taches_ordonnee
    planif_priorisee = {}
    # Création d'un dictionnaire pour connaître l'indice de chaque tâche dans l'ordre prioritaire
    ordre_global = {t['nom']: i for i, t in enumerate(taches_ordonnee)}
    for jour in jours_semaine:
        taches_jour = st.session_state.planifications[jour]
        taches_jour_triees = sorted(taches_jour, key=lambda nom: ordre_global.get(nom, float('inf')))
        planif_priorisee[jour] = taches_jour_triees

    # Création du tableau à partir des tâches planifiées triées
    max_tasks = max(len(taches) for taches in planif_priorisee.values())
    table = {jour: (planif_priorisee[jour] + [""] * (max_tasks - len(planif_priorisee[jour]))) for jour in jours_semaine}
    df = pd.DataFrame(table)
    st.dataframe(df)
