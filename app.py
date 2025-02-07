import streamlit as st
import sqlite3
import os

# Configuration de la page et affichage du logo de SMADIRE
st.set_page_config(page_title="SMADIRE - Gestion des Articles", page_icon=":clipboard:", layout="centered")
if os.path.exists("logo_smadiire.png"):
    st.image("logo_smadiire.png", width=200)
else:
    st.write("Logo non trouvé.")

# Connexion à la base de données SQLite (création du fichier articles.db s'il n'existe pas)
conn = sqlite3.connect('articles.db', check_same_thread=False)
c = conn.cursor()

# Création de la table articles si elle n'existe pas déjà
c.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        designation TEXT NOT NULL,
        prix_achat REAL NOT NULL,
        temps_pose REAL NOT NULL
    )
""")
conn.commit()

# --- Fonctions de gestion de la base de données ---

def add_article(designation, prix_achat, temps_pose):
    c.execute("INSERT INTO articles (designation, prix_achat, temps_pose) VALUES (?, ?, ?)",
              (designation, prix_achat, temps_pose))
    conn.commit()

def get_articles():
    c.execute("SELECT * FROM articles")
    return c.fetchall()

def update_article(article_id, designation, prix_achat, temps_pose):
    c.execute("UPDATE articles SET designation = ?, prix_achat = ?, temps_pose = ? WHERE id = ?",
              (designation, prix_achat, temps_pose, article_id))
    conn.commit()

def search_articles(keyword):
    # Recherche par mot-clé dans la désignation (insensible à la casse)
    c.execute("SELECT * FROM articles WHERE LOWER(designation) LIKE ?", ('%' + keyword.lower() + '%',))
    return c.fetchall()

# --- Interface utilisateur avec Streamlit ---

# Menu latéral de navigation
menu = st.sidebar.selectbox("Menu", ["Afficher les articles", "Ajouter un article", "Modifier un article", "Rechercher un article"])

if menu == "Afficher les articles":
    st.header("Liste des Articles")
    articles = get_articles()
    if articles:
        # Affichage sous forme de liste déroulante
        article_options = {f"{article[0]} - {article[1]}": article for article in articles}
        selected_key = st.selectbox("Sélectionnez un article", list(article_options.keys()))
        selected_article = article_options[selected_key]
        st.subheader("Détails de l'article sélectionné")
        st.write("**Prix Unitaire Achat (HT) :**", selected_article[2])
        st.write("**Temps de pose (Heure Équipe) :**", selected_article[3])
    else:
        st.info("Aucun article enregistré.")

elif menu == "Ajouter un article":
    st.header("Ajouter un Nouvel Article")
    with st.form("ajouter_article_form"):
        designation = st.text_input("Désignation de l'article")
        prix_achat = st.number_input("Prix Unitaire Achat (HT)", min_value=0.0, format="%.2f")
        temps_pose = st.number_input("Temps de pose (Heure Équipe)", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Ajouter l'article")
        if submitted:
            if designation:
                add_article(designation, prix_achat, temps_pose)
                st.success("Article ajouté avec succès !")
            else:
                st.error("Veuillez saisir la désignation de l'article.")

elif menu == "Modifier un article":
    st.header("Modifier un Article")
    articles = get_articles()
    if articles:
        # Sélection d'un article à modifier
        article_options = {f"{article[0]} - {article[1]}": article for article in articles}
        selected_key = st.selectbox("Sélectionnez un article à modifier", list(article_options.keys()))
        selected_article = article_options[selected_key]
        # Formulaire pré-rempli pour la modification
        with st.form("modifier_article_form"):
            new_designation = st.text_input("Nouvelle désignation", value=selected_article[1])
            new_prix_achat = st.number_input("Nouveau Prix Unitaire Achat (HT)", min_value=0.0, value=selected_article[2], format="%.2f")
            new_temps_pose = st.number_input("Nouveau Temps de pose (Heure Équipe)", min_value=0.0, value=selected_article[3], format="%.2f")
            submitted = st.form_submit_button("Modifier l'article")
            if submitted:
                update_article(selected_article[0], new_designation, new_prix_achat, new_temps_pose)
                st.success("Article modifié avec succès !")
    else:
        st.info("Aucun article disponible à modifier.")

elif menu == "Rechercher un article":
    st.header("Recherche d'Articles")
    keyword = st.text_input("Entrez un mot-clé pour rechercher dans la désignation")
    if st.button("Rechercher"):
        results = search_articles(keyword)
        if results:
            st.write(f"{len(results)} article(s) trouvé(s) :")
            for article in results:
                st.write(f"**ID :** {article[0]}  |  **Désignation :** {article[1]}")
                st.write(f"**Prix Unitaire Achat (HT) :** {article[2]}  |  **Temps de pose (Heure Équipe) :** {article[3]}")
                st.write("---")
        else:
            st.info("Aucun article correspondant trouvé.")
