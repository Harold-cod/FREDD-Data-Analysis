# 🧬 Projet FREDD – Analyse des données cliniques et génétiques

Ce projet s’inscrit dans le cadre d’un stage réalisé au **Centre de Recherche en Biomédecine de Strasbourg (CRBS)**, et vise à explorer les données de santé pour l'exploration de l’entrepôt de données FREDD (French Rare Eye Disease Database).  
Il inclut des étapes de contrôle qualité, d’analyse descriptive et de visualisation via un tableau de bord interactif.

---

## 📁 Structure du projet

```
├── project_Fredd.ipynb        # Analyse initiale en Jupyter Notebook
├── project_Fredd.qmd          # Version Quarto du rapport
├── projet_stage.py            # Application Streamlit
├── requirements.txt           # Dépendances Python
├── README.md                  # Ce fichier
├── .gitignore                 # Fichiers exclus de Git
```

---

## 🚀 Installation

1. **Clonez le dépôt** – à exécuter dans votre terminal :
```bash
git clone https://github.com/Harold-cod/FREDD-Data-Analysis.git
cd FREDD-Data-Analysis
```

2. **Installez les dépendances** :
```bash
pip install -r requirements.txt
```

3. **(Facultatif)** Si vous utilisez Quarto pour générer un rapport :
```bash
quarto render project_Fredd.qmd --to html
```

4. **Exécution du tableau de bord** :
```bash
streamlit run projet_stage.py
```

---

## 🔧 Technologies utilisées

- **Python 3**
- **Pandas** & **Plotly** – analyse de données
- **Streamlit** – création du tableau de bord
- **Quarto** – génération de rapports HTML/PDF
- **Jupyter Notebook** – exploration initiale

---

## 🧾 Auteur

**Harold Kouekam Siewe**  
Stage 2025 – Centre de Recherche en Biomédecine de Strasbourg
Université de Strasbourg – Master Ingénierie de la Santé
