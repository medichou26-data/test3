import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json

# Title
st.set_page_config(page_title="Système Universitaire Azure", layout="wide")
st.title("🎓 Système Universitaire - Déploiement Azure")

# Health check
st.text("✅ Application en cours d'exécution")

# Configuration
CSV_PATH = "data/db.csv"
CONFIG_PATH = "config/config.json"

# Créer les dossiers nécessaires
os.makedirs("data", exist_ok=True)
os.makedirs("config", exist_ok=True)

# Charger la configuration
def load_config():
    """Charger la configuration depuis un fichier JSON"""
    default_config = {
        "university_name": "Université Azure",
        "max_students": 1000,
        "min_age": 16,
        "max_age": 70,
        "specialties": [
            "Informatique", "Mathématiques", "Physique", 
            "Chimie", "Biologie", "Économie", "Droit", "Médecine"
        ],
        "version": "1.0.0"
    }
    
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            return default_config
    else:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

# Fonctions CRUD
def load_data():
    """Charger les données depuis le CSV"""
    if os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH)
            # S'assurer que toutes les colonnes nécessaires existent
            required_columns = ['id', 'nom', 'prenom', 'specialite', 'moyenne_generale', 'age', 'date_inscription', 'email']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            return df
        except:
            return create_empty_dataframe()
    else:
        return create_empty_dataframe()

def create_empty_dataframe():
    """Créer un DataFrame vide avec la structure attendue"""
    return pd.DataFrame(columns=[
        'id', 'nom', 'prenom', 'specialite', 'moyenne_generale',
        'age', 'date_inscription', 'email', 'credits', 'statut'
    ])

def save_data(df):
    """Sauvegarder les données dans le CSV"""
    # S'assurer que le dossier existe
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    df.to_csv(CSV_PATH, index=False)

# Initialisation
config = load_config()
df = load_data()

# Sidebar pour la configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    university_name = st.text_input("Nom de l'université", config['university_name'])
    
    # Mettre à jour la configuration
    if st.button("Enregistrer la configuration"):
        config['university_name'] = university_name
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        st.success("Configuration enregistrée !")
    
    st.divider()
    
    st.header("📝 Opérations CRUD")
    
    crud_operation = st.selectbox(
        "Choisir une opération",
        ["Afficher", "Créer", "Lire", "Mettre à jour", "Supprimer", "Rechercher", "Statistiques"]
    )
    
    # Recherche rapide
    st.subheader("🔍 Recherche rapide")
    search_term = st.text_input("Rechercher un étudiant", placeholder="Nom, spécialité...")

# Header avec le nom de l'université
st.header(f"📊 {config['university_name']} - Données des étudiants")

if not df.empty:
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Nombre d'étudiants", len(df))
    with col2:
        st.metric("Spécialités uniques", df['specialite'].nunique())
    with col3:
        avg_grade = df['moyenne_generale'].mean() if 'moyenne_generale' in df.columns and not df['moyenne_generale'].isna().all() else 0
        st.metric("Moyenne générale", f"{avg_grade:.2f}")
    with col4:
        avg_age = df['age'].mean() if 'age' in df.columns and not df['age'].isna().all() else 0
        st.metric("Âge moyen", f"{avg_age:.1f}")
    
    # Dataframe principal
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Graphiques
    if crud_operation == "Statistiques" or st.checkbox("Afficher les statistiques"):
        tab1, tab2, tab3 = st.tabs(["📈 Répartition", "📊 Performances", "👥 Démographie"])
        
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                if 'specialite' in df.columns:
                    spec_count = df['specialite'].value_counts()
                    fig1 = px.pie(
                        values=spec_count.values,
                        names=spec_count.index,
                        title="Répartition par spécialité"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                if 'age' in df.columns:
                    fig2 = px.histogram(df, x='age', title="Distribution des âges")
                    st.plotly_chart(fig2, use_container_width=True)
        
        with tab2:
            if 'moyenne_generale' in df.columns:
                fig3 = px.box(df, y='moyenne_generale', title="Distribution des moyennes")
                st.plotly_chart(fig3, use_container_width=True)
        
        with tab3:
            if 'specialite' in df.columns and 'moyenne_generale' in df.columns:
                fig4 = px.scatter(
                    df, 
                    x='age', 
                    y='moyenne_generale',
                    color='specialite',
                    title="Âge vs Moyenne par spécialité",
                    hover_data=['nom', 'prenom']
                )
                st.plotly_chart(fig4, use_container_width=True)
    
    # Graphique : moyenne par filière
    if 'specialite' in df.columns and 'moyenne_generale' in df.columns:
        if not df['moyenne_generale'].isna().all():
            fig = px.bar(
                df.groupby('specialite')['moyenne_generale'].mean().reset_index(),
                x='specialite', 
                y='moyenne_generale',
                title="📈 Moyenne générale par filière",
                color='moyenne_generale'
            )
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune donnée disponible. Commencez par ajouter des étudiants.")

# Opérations CRUD
st.divider()

if crud_operation == "Créer":
    st.subheader("➕ Ajouter un nouvel étudiant")
    
    with st.form("create_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom*", placeholder="Dupont")
            prenom = st.text_input("Prénom*", placeholder="Jean")
            specialite = st.selectbox(
                "Spécialité*",
                config['specialties']
            )
        
        with col2:
            moyenne = st.slider("Moyenne générale*", 0.0, 20.0, 12.0, 0.5)
            age = st.number_input("Âge*", config['min_age'], config['max_age'], 20)
            email = st.text_input("Email", placeholder="jean.dupont@email.com")
            credits = st.number_input("Crédits ECTS", 0, 300, 180)
        
        submitted = st.form_submit_button("Ajouter l'étudiant")
        
        if submitted:
            if nom and prenom and specialite:
                new_id = df['id'].max() + 1 if 'id' in df.columns and len(df) > 0 else 1
                new_student = {
                    'id': new_id,
                    'nom': nom,
                    'prenom': prenom,
                    'specialite': specialite,
                    'moyenne_generale': moyenne,
                    'age': age,
                    'date_inscription': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'email': email if email else f"{prenom.lower()}.{nom.lower()}@{university_name.lower().replace(' ', '')}.fr",
                    'credits': credits,
                    'statut': 'Actif'
                }
                
                # Ajouter le nouvel étudiant
                new_df = pd.DataFrame([new_student])
                df = pd.concat([df, new_df], ignore_index=True)
                save_data(df)
                
                st.success(f"✅ Étudiant {prenom} {nom} ajouté avec succès ! (ID: {new_id})")
                st.balloons()
            else:
                st.error("⚠️ Les champs marqués d'un * sont obligatoires")

elif crud_operation == "Mettre à jour":
    st.subheader("✏️ Mettre à jour un étudiant")
    
    if not df.empty:
        # Sélectionner un étudiant
        student_names = df.apply(lambda x: f"{x['id']} - {x['prenom']} {x['nom']} ({x['specialite']})", axis=1)
        selected_student = st.selectbox(
            "Sélectionner un étudiant à modifier",
            student_names
        )
        
        if selected_student:
            student_id = int(selected_student.split(" - ")[0])
            student_data = df[df['id'] == student_id].iloc[0]
            
            with st.form("update_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nom = st.text_input("Nom*", value=student_data['nom'])
                    prenom = st.text_input("Prénom*", value=student_data['prenom'])
                    specialite = st.selectbox(
                        "Spécialité*",
                        config['specialties'],
                        index=config['specialties'].index(student_data['specialite']) 
                        if student_data['specialite'] in config['specialties'] 
                        else 0
                    )
                
                with col2:
                    moyenne = st.slider(
                        "Moyenne générale*", 
                        0.0, 20.0, 
                        float(student_data['moyenne_generale']), 
                        0.5
                    )
                    age = st.number_input(
                        "Âge*", 
                        config['min_age'], config['max_age'], 
                        int(student_data['age'])
                    )
                    email = st.text_input("Email", value=student_data['email'])
                    credits = st.number_input(
                        "Crédits ECTS", 
                        0, 300, 
                        int(student_data['credits']) if 'credits' in student_data and not pd.isna(student_data['credits']) else 180
                    )
                    statut = st.selectbox(
                        "Statut",
                        ["Actif", "Inactif", "Diplômé", "Abandon"],
                        index=["Actif", "Inactif", "Diplômé", "Abandon"].index(student_data['statut']) 
                        if 'statut' in student_data and student_data['statut'] in ["Actif", "Inactif", "Diplômé", "Abandon"] 
                        else 0
                    )
                
                submitted = st.form_submit_button("Mettre à jour")
                
                if submitted:
                    # Mettre à jour les données
                    update_cols = ['nom', 'prenom', 'specialite', 'moyenne_generale', 'age', 'email', 'credits', 'statut']
                    update_values = [nom, prenom, specialite, moyenne, age, email, credits, statut]
                    
                    for col, val in zip(update_cols, update_values):
                        df.loc[df['id'] == student_id, col] = val
                    
                    save_data(df)
                    st.success(f"✅ Étudiant {prenom} {nom} mis à jour avec succès !")
                    st.rerun()
    else:
        st.info("ℹ️ Aucun étudiant à mettre à jour")

elif crud_operation == "Supprimer":
    st.subheader("🗑️ Supprimer un étudiant")
    
    if not df.empty:
        # Sélectionner un étudiant
        student_names = df.apply(lambda x: f"{x['id']} - {x['prenom']} {x['nom']} ({x['specialite']})", axis=1)
        selected_student = st.selectbox(
            "Sélectionner un étudiant à supprimer",
            student_names
        )
        
        if selected_student:
            student_id = int(selected_student.split(" - ")[0])
            student_data = df[df['id'] == student_id].iloc[0]
            
            st.warning(f"⚠️ Vous allez supprimer : **{student_data['prenom']} {student_data['nom']}**")
            st.write(f"**Spécialité :** {student_data['specialite']}")
            st.write(f"**Moyenne :** {student_data['moyenne_generale']}")
            st.write(f"**Âge :** {student_data['age']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Confirmer la suppression", type="primary"):
                    # Supprimer l'étudiant
                    df = df[df['id'] != student_id]
                    save_data(df)
                    
                    st.success("✅ Étudiant supprimé avec succès !")
                    st.rerun()
            with col2:
                if st.button("Annuler"):
                    st.rerun()
    else:
        st.info("ℹ️ Aucun étudiant à supprimer")

elif crud_operation == "Rechercher" or search_term:
    st.subheader("🔍 Résultats de recherche")
    
    search_query = search_term if search_term else st.text_input("Entrez votre recherche", key="search_input")
    
    if search_query:
        search_query_lower = search_query.lower()
        # Rechercher dans toutes les colonnes
        mask = pd.Series(False, index=df.index)
        for col in df.columns:
            if df[col].dtype == 'object':
                mask = mask | df[col].astype(str).str.lower().str.contains(search_query_lower, na=False)
        
        results = df[mask]
        
        if not results.empty:
            st.write(f"**{len(results)}** résultat(s) trouvé(s) pour '{search_query}'")
            
            # Options d'affichage
            view_option = st.radio(
                "Mode d'affichage",
                ["Tableau", "Cartes"],
                horizontal=True
            )
            
            if view_option == "Tableau":
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                cols = st.columns(3)
                for idx, (_, row) in enumerate(results.iterrows()):
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{row['prenom']} {row['nom']}**")
                            st.caption(f"ID: {row['id']}")
                            st.write(f"Spécialité: {row['specialite']}")
                            st.write(f"Moyenne: {row['moyenne_generale']}")
                            st.write(f"Âge: {row['age']}")
                            st.write(f"Statut: {row['statut'] if 'statut' in row else 'Actif'}")
            
            # Télécharger les résultats
            csv = results.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les résultats (CSV)",
                data=csv,
                file_name=f"recherche_{search_query}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info(f"🔍 Aucun résultat trouvé pour '{search_query}'")

elif crud_operation == "Lire":
    st.subheader("👁️ Détails d'un étudiant")
    
    if not df.empty:
        # Sélectionner un étudiant
        student_names = df.apply(lambda x: f"{x['id']} - {x['prenom']} {x['nom']}", axis=1)
        selected_student = st.selectbox(
            "Sélectionner un étudiant pour voir les détails",
            student_names
        )
        
        if selected_student:
            student_id = int(selected_student.split(" - ")[0])
            student_data = df[df['id'] == student_id].iloc[0]
            
            # Afficher les détails dans des colonnes
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**ID :** {student_data['id']}")
                st.info(f"**Nom complet :** {student_data['prenom']} {student_data['nom']}")
                st.info(f"**Spécialité :** {student_data['specialite']}")
                st.info(f"**Moyenne générale :** {student_data['moyenne_generale']}")
            
            with col2:
                st.info(f"**Âge :** {student_data['age']}")
                st.info(f"**Email :** {student_data['email']}")
                st.info(f"**Crédits ECTS :** {student_data.get('credits', 'N/A')}")
                st.info(f"**Statut :** {student_data.get('statut', 'Actif')}")
            
            if 'date_inscription' in student_data:
                st.info(f"**Date d'inscription :** {student_data['date_inscription']}")
            
            # Note graphique
            if 'moyenne_generale' in student_data:
                grade = float(student_data['moyenne_generale'])
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=grade,
                    title={'text': "Moyenne"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    gauge={
                        'axis': {'range': [0, 20]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 10], 'color': "lightgray"},
                            {'range': [10, 15], 'color': "gray"},
                            {'range': [15, 20], 'color': "lightblue"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 16
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

# Section d'exportation
st.divider()
st.subheader("📁 Gestion des données")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Exporter toutes les données"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Télécharger CSV complet",
            data=csv,
            file_name=f"etudiants_{config['university_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("🔄 Rafraîchir les données"):
        df = load_data()
        st.rerun()

with col3:
    if st.button("🗑️ Supprimer TOUTES les données"):
        st.warning("⚠️ Cette action est irréversible !")
        password = st.text_input("Entrez 'SUPPRIMER' pour confirmer", type="password")
        if st.button("Confirmer la suppression totale"):
            if password == "SUPPRIMER":
                df = create_empty_dataframe()
                save_data(df)
                st.error("💥 Toutes les données ont été supprimées !")
                st.rerun()
            else:
                st.error("Mot de passe incorrect")

# Section avancée
with st.expander("🔧 Outils avancés"):
    tab1, tab2, tab3 = st.tabs(["Données brutes", "Import CSV", "Système"])
    
    with tab1:
        st.write("**Données brutes :**")
        st.dataframe(df, use_container_width=True)
        
        # Statistiques détaillées
        if not df.empty:
            st.write("**Statistiques descriptives :**")
            st.dataframe(df.describe(), use_container_width=True)
    
    with tab2:
        st.write("**Importer un fichier CSV :**")
        uploaded_file = st.file_uploader(
            "Choisir un fichier CSV", 
            type=['csv'],
            help="Le fichier doit contenir les colonnes: id, nom, prenom, specialite, moyenne_generale, age, email"
        )
        
        if uploaded_file is not None:
            try:
                new_df = pd.read_csv(uploaded_file)
                st.write("**Aperçu du fichier :**")
                st.dataframe(new_df.head(), use_container_width=True)
                
                # Options d'importation
                import_option = st.radio(
                    "Option d'importation",
                    ["Remplacer toutes les données", "Ajouter aux données existantes"],
                    horizontal=True
                )
                
                if st.button("Importer les données"):
                    if import_option == "Remplacer toutes les données":
                        df = new_df
                        st.success("✅ Données remplacées avec succès !")
                    else:
                        df = pd.concat([df, new_df], ignore_index=True)
                        st.success("✅ Données ajoutées avec succès !")
                    
                    save_data(df)
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
    
    with tab3:
        st.write("**Informations système :**")
        st.write(f"- Version de l'application: {config['version']}")
        st.write(f"- Nombre d'étudiants: {len(df)}")
        st.write(f"- Taille du fichier de données: {os.path.getsize(CSV_PATH) if os.path.exists(CSV_PATH) else 0} octets")
        st.write(f"- Dernière modification: {datetime.fromtimestamp(os.path.getmtime(CSV_PATH)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(CSV_PATH) else 'N/A'}")
        
        # Bouton de réinitialisation
        if st.button("🔄 Réinitialiser l'application"):
            for file in [CSV_PATH, CONFIG_PATH]:
                if os.path.exists(file):
                    os.remove(file)
            st.success("✅ Application réinitialisée !")
            st.rerun()

# Footer
st.divider()
st.caption(f"📱 {config['university_name']} - Version {config['version']} | {len(df)} étudiants | Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")