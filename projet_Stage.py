import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.set_page_config(layout="wide")
# Style des differents onglets
st.markdown("""
    <style>
        .sidebar .sidebar-content {
            background-color: #004080;
            padding: 20px;
            border-radius: 10px;
        }
        .sidebar .sidebar-content h2, .sidebar .sidebar-content h3, .sidebar .sidebar-content h4 {
            color: #004080;
        }
        .sidebar .stMultiSelect > label, .sidebar .stSlider > label {
            font-weight: bold;
        }
        .main-title {
            text-align: center;
            font-size: 50px;
            font-weight: bold;
            color: #d62728;
            margin-bottom: 40px;
        }  
         .section-title {
            text-align: left;
            font-size: 34px;
            font-weight: bold;
            color: #0055a0;
            margin-top: 20px;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)
# st.title("Tableau de bord 🩺 Clinique et 🧬 Génétique")
st.markdown("<div class='main-title'>Tableau de bord 🩺 Clinique et 🧬 Génétique</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("📁 Chargement des données")

    # Chargement interactif de plusieurs fichiers CSV
    uploaded_files = st.file_uploader("Charger un ou plusieurs fichiers CSV", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        dataframes = []
        for file in uploaded_files:
            df = pd.read_csv(file, sep=';', low_memory=False)
            df["source_file"] = file.name
            dataframes.append(df)
        st.session_state['data'] = pd.concat(dataframes, ignore_index=True)

    # Chargement du glossaire
    glossaire_file = st.file_uploader("Charger le glossaire des variables (CSV ou Excel)", type=["csv", "xlsx"])
    if glossaire_file:
        try:
            if glossaire_file.name.endswith(".csv"):
                glossaire = pd.read_csv(glossaire_file)
            else:
                glossaire = pd.read_excel(glossaire_file)
            st.session_state['glossaire'] = glossaire
        except Exception as e:
            st.error(f"Erreur de lecture du glossaire : {e}")
            glossaire = None
    else:
        glossaire = None

if "data" in st.session_state:
    df_final = st.session_state["data"]

    # Prétraitement des données
    df_final['leg_date_incFREDD'] = pd.to_datetime(df_final['leg_date_incFREDD'], errors='coerce', dayfirst=True)
    df_final['adm_date_naissance'] = pd.to_datetime(df_final['adm_date_naissance'], errors='coerce', dayfirst=True)
    df_final['diaGen_CR_date'] = pd.to_datetime(df_final['diaGen_CR_date'], errors='coerce', dayfirst=True)
    df_final['his_date_MR'] = pd.to_datetime(df_final['his_date_MR'], errors='coerce', dayfirst=True)
    df_final['exaAcu_date'] = pd.to_datetime(df_final['exaAcu_date'], errors='coerce', dayfirst=True)
    df_final['exaChv_date'] = pd.to_datetime(df_final['exaChv_date'], errors='coerce', dayfirst=True)

    # Age à l'inclusion dans FREDD
    df_final['leg_age_patientFREDD'] = (df_final['leg_date_incFREDD'] - df_final['adm_date_naissance']).dt.days / 365.25

    # Age au moment du dernier compte rendu génétique (juste patients ayant statut confirmé)
    df_final['age_diagnostic'] = (df_final['diaGen_CR_date'] - df_final['adm_date_naissance']).dt.days / 365.25

    # Onglets principaux
    tabs = st.tabs(["📊 Vue globale", "🧍 Analyse par patient", "🏥 Analyse comparative entre sites", "📚 Glossaire"])

    # Onglet Vue globale
    with tabs[0]:
        # st.title("Tableau de bord: Vue globale")
        st.markdown("<div class='section-title'>Vue globale (ensemble des données)</div>", unsafe_allow_html=True)

        # Indicateurs principaux type Snowflake : pour les couleurs adapter en fonction de l'affiche de l'user #ffffff white et #000000 black
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown("""
            <div style='background-color:#ffffff; padding:10px; border-radius:10px; text-align:center'>
                <h3>👤 Patients</h3>
                <h1 style='color:#1f77b4; font-size:50px'>{}</h1>
            </div>
        """.format(len(df_final)), unsafe_allow_html=True)
        col2.markdown("""
            <div style='background-color:#ffffff; padding:10px; border-radius:10px; text-align:center'>
                <h3>🩺 Maladies</h3>
                <h1 style='color:#2ca02c; font-size:50px'>{}</h1>
            </div>
        """.format(df_final['diaCli_diagMR_nom'].nunique()), unsafe_allow_html=True)
        col3.markdown("""
            <div style='background-color:#ffffff; padding:10px; border-radius:10px; text-align:center'>
                <h3>🧬 Gènes</h3>
                <h1 style='color:#d62728; font-size:50px'>{}</h1>
            </div>
        """.format(df_final['diaGen_var_hgcn_1'].nunique()), unsafe_allow_html=True)
        col4.markdown("""
            <div style='background-color:#ffffff; padding:10px; border-radius:10px; text-align:center'>
                <h3>🏥 Sites</h3>
                <h1 style='color:#9467bd; font-size:50px'>{}</h1>
            </div>
        """.format(df_final['leg_site_inc_nom'].nunique()), unsafe_allow_html=True)

        # Détail par site
        st.markdown("### 🏥 Indicateurs par site")
        site_summary = df_final.groupby("leg_site_inc_nom").agg({
            'id': 'count',
            'diaCli_diagMR_nom': pd.Series.nunique,
            'diaGen_var_hgcn_1': pd.Series.nunique
        }).reset_index()
        site_summary.columns = ['Site', 'Patients', 'Maladies identifiées', 'Gènes identifiés']
        # Liste d’icônes et couleurs par site (à adapter selon les noms de sites connus)
        site_styles = {
            "Hôpital National des 15-20": {"color": "#d9f2ff", "icon": "🏥"},
            "Hôpitaux universitaires de Strasbourg": {"color": "#e6ffe6", "icon": "🏛️"},
        }

        cols = st.columns(len(site_summary))

        for i, row in site_summary.iterrows():
            site_name = row['Site']
            icon = site_styles.get(site_name, {}).get("icon", "🏬")

            with cols[i]:
                st.markdown(f"""
                    <div style='background-color:#ffffff; padding:10px; border-radius:10px; text-align:center; box-shadow: 1px 1px 5px rgba(0,0,0,0.1);'>
                        <h4 style='color:#d62728; font-size:22px;'>{icon} {site_name}</h4>
                        <p style='margin:0; font-size:15px;'>👤 Patients : <strong style='color:#1f77b4'>{row['Patients']}</strong></p>
                        <p style='margin:0; font-size:15px;'>🩺 Maladies : <strong style='color:#2ca02c'>{row['Maladies identifiées']}</strong></p>
                        <p style='margin:0; font-size:15px;'>🧬 Gènes : <strong style='color:#d62728'>{row['Gènes identifiés']}</strong></p>
                    </div>
                """, unsafe_allow_html=True)

        with st.sidebar:
            # Filtres
            diag_filter = st.multiselect("Filtrer par diagnostic clinique :", options=df_final['diaCli_diagMR_nom'].dropna().unique())
            gene_filter = st.multiselect("Filtrer par gène identifié :", options=df_final['diaGen_var_hgcn_1'].dropna().unique())
            site_filter = st.multiselect("Filtrer par site d'inclusion :", options=df_final['leg_site_inc_nom'].dropna().unique())
            age_min, age_max = st.slider("Filtrer par âge à l'inclusion(années)", 0, 100, (0, 100))

        filtered_data = df_final.copy()
        if diag_filter:
            filtered_data = filtered_data[filtered_data['diaCli_diagMR_nom'].isin(diag_filter)]
        if gene_filter:
            filtered_data = filtered_data[filtered_data['diaGen_var_hgcn_1'].isin(gene_filter)]
        filtered_data = filtered_data[(filtered_data['leg_age_patientFREDD'] >= age_min) & (filtered_data['leg_age_patientFREDD'] <= age_max)]

        # st.metric("Nombre total de patients", len(filtered_data))
        st.markdown("---")
        st.subheader("📊 Visualisations globales")
        # Cammenbert sexe des patients
        proportions = filtered_data['adm_sexe'].value_counts().reset_index()
        proportions.columns = ['adm_sexe', 'proportion']
        totals_counts = proportions['proportion'].sum()
        proportions['Percentage'] = (proportions['proportion'] / totals_counts * 100).round(1)

        proportions['adm_sexe'] = proportions['adm_sexe'].astype(str)
        proportions['label'] = proportions['adm_sexe'].replace({'1': 'Homme', '2': 'Femme'})

        fig1 = px.pie(
            proportions,
            names='label',
            values='proportion',
            title=f"<b>Sexe des patients",
            color_discrete_sequence=px.colors.qualitative.Bold

        )
        fig1.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig1)

        # ****************** Histogramme age des patients à l'inclusion dans FREDD *********************
        fig2 = px.histogram(filtered_data,
                            x="leg_age_patientFREDD",
                            nbins=20,
                            title="<b>Age des patients à l'inclusion dans FREDD",
                            labels={"age": "Âge",
                                    "count": "Nombre de personnes"}
                            )

        fig2.update_layout(
            xaxis_title="Âge",
            yaxis_title="Nombre de personnes",
            title_font_size=17
        )
        st.plotly_chart(fig2)

        # ************** Diagnostic clinique *******************
        diagnosis_counts = filtered_data['diaCli_diagMR_nom'].value_counts(dropna=False).reset_index()
        diagnosis_counts.columns = ['Diagnosis', 'Number of cases']
        diagnosis_counts['Diagnosis'] = diagnosis_counts['Diagnosis'].fillna('Missing')
        total_cases = diagnosis_counts['Number of cases'].sum()
        diagnosis_counts['Percentage'] = (diagnosis_counts['Number of cases'] / total_cases * 100).round(1)

        st.subheader("🩺 Répartition des maladies selon le diagnostic clinique ")
        mode = st.selectbox("Afficher :", ["Toutes les maladies", "Top 10"])
        if mode == "Top 10":
            data_to_plot = diagnosis_counts.head(10)
        else:
            data_to_plot = diagnosis_counts
        fig3 = px.bar(
            data_to_plot,
            y='Diagnosis',
            x='Number of cases',
            color='Number of cases',
            orientation='h',
            color_continuous_scale='Plasma',
            text='Number of cases',
            title='<b>Maladies</b>',
            labels={'Number of cases': 'Nombre de cas', 'Diagnosis': 'Maladies'},
            height=900
        )

        fig3.update_layout(
            yaxis={'categoryorder':'total ascending'}, 
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='y unified',
            title_font={'size': 17},
            uniformtext_minsize=8,
            margin=dict(r=150),
            bargap=0.1
        )

        fig3.update_traces(
            texttemplate='<b>%{x}</b><br>(%{customdata[0]}%)',
            hovertemplate="<b>%{y}</b><br>Cases: %{x}<br>Proportion: %{customdata[0]}%",
            textposition='auto',
            customdata=diagnosis_counts[['Percentage']]
        )
        st.plotly_chart(fig3)
        
        # ***************** Signes cliniques associés aux patients *************************
        st.subheader("🔍 Visualisation des combinaisons de signes cliniques")
        variables = [f'diaCli_signes_ass{i}' for i in range(1, 10)]

        # Matrice binaire
        df_signes = filtered_data[variables].fillna('missing').astype(str)
        unique_signes = pd.unique(df_signes.values.ravel())
        unique_signes = [s for s in unique_signes if s != 'missing']

        # Création de la matrice binaire
        binary_df = pd.DataFrame(False, index=df_signes.index, columns=unique_signes)
        for sign in unique_signes:
            binary_df[sign] = df_signes.apply(lambda row: sign in row.values, axis=1)

        # Groupe par combinaison
        combos = binary_df.groupby(list(binary_df.columns)).size().reset_index(name='count')
        combos['combination'] = combos[binary_df.columns].apply(
            lambda row: ', '.join([col for col, val in row.items() if val]), axis=1
        )
        combos = combos.sort_values('count', ascending=False)
        # Ajuster le nombre de combinaison
        top_n = st.slider("Nombre de combinaisons à afficher", 5, 50, 10)

        fig = px.bar(
            combos.head(top_n),
            x='combination',
            y='count',
            text='count',
            color='count',
            color_continuous_scale='Plasma',
            labels={'combination': 'Combinaison de signes cliniques', 'count': 'Nombre de patients'},
            title=f"{top_n} combinaisons les plus fréquentes",
            height=800 if top_n <= 25 else 1200
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            height=1000,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=20)
        )
        fig.update_traces(
            textposition='auto',
            hovertemplate="<b>%{y}</b><br>Cases: %{x}",
        )

        st.plotly_chart(fig, use_container_width=True)

        # ****************** Graphique Listes des gènes *************************
        diagnosis_counts = filtered_data['diaGen_var_hgcn_1'].value_counts(dropna=False).reset_index()
        diagnosis_counts.columns = ['Diagnosis', 'Number of cases']
        diagnosis_counts['Diagnosis'] = diagnosis_counts['Diagnosis'].fillna('Missing')
        total_cases = diagnosis_counts['Number of cases'].sum()
        diagnosis_counts['Percentage'] = (diagnosis_counts['Number of cases'] / total_cases * 100).round(1)

        st.subheader("🧬Répartition des gènes selon le test génétique ")
        mode = st.selectbox("Afficher :", ["Tous les gènes", "Top 10"])
        if mode == "Top 10":
            data_to_plot = diagnosis_counts.head(10)
        else:
            data_to_plot = diagnosis_counts

        fig4 = px.bar(
            data_to_plot,
            y='Diagnosis',
            x='Number of cases',
            color='Number of cases',
            orientation='h',
            color_continuous_scale='Plasma',
            text='Number of cases',
            title='<b>Gènes</b>',
            labels={'Number of cases': 'Nombre de cas', 'Diagnosis': 'Genes'},
            height=800 if mode == "Top 10" else 1200
        )

        fig4.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode='y unified',
            height=1000,
            title_font={'size': 20},
            uniformtext_minsize=20
        )

        fig4.update_traces(
            texttemplate='<b>%{x}</b><br>(%{customdata[0]}%)',
            hovertemplate="<b>%{y}</b><br>Cases: %{x}<br>Proportion: %{customdata[0]}%",
            textposition='auto',
            customdata=diagnosis_counts[['Percentage']],
            textfont_size=17
        )
        st.plotly_chart(fig4, use_container_width=True)

        # ********* Correlation entre les variables *************
        st.markdown("## 🔄 Corrélation entre maladies et gènes")
        sankey_df = df_final[["diaCli_diagMR_nom", "diaGen_var_hgcn_1"]].dropna()

        # Encodage des labels
        labels = pd.Series(pd.concat([sankey_df['diaCli_diagMR_nom'], sankey_df['diaGen_var_hgcn_1']])).unique().tolist()
        label_to_index = {label: i for i, label in enumerate(labels)}
        import matplotlib.pyplot as plt

        # Construction des liens (source-target-value)
        sankey_links = sankey_df.groupby(['diaCli_diagMR_nom', 'diaGen_var_hgcn_1']).size().reset_index(name='count')
        n_diag = sankey_df['diaCli_diagMR_nom'].nunique()
        n_gene = sankey_df['diaGen_var_hgcn_1'].nunique()
        # colors
        node_colors = ['#1f77b4'] * n_diag + ['red'] * n_gene
        unique_sources = sankey_links['diaCli_diagMR_nom'].unique()
        color_map = plt.cm.get_cmap('tab20', len(unique_sources))
        source_to_color = {src: f'rgba{tuple(int(c*255) for c in color_map(i)[:3]) + (0.7,)}' for i, src in enumerate(unique_sources)}

        link_colors = sankey_links['diaCli_diagMR_nom'].map(source_to_color).tolist()
        fig = go.Figure(data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=labels,
                    color=node_colors
                ),
                link=dict(
                    source=[label_to_index[src] for src in sankey_links['diaCli_diagMR_nom']],
                    target=[label_to_index[tgt] for tgt in sankey_links['diaGen_var_hgcn_1']],
                    value=sankey_links['count'],
                    color=link_colors,
                    hovertemplate='Source: %{source.label}<br />Target: %{target.label}<br />Count: %{value}<extra></extra>'
                )
            )
        ])

        fig.update_layout(
            title_text="Flux entre les maladies diagnostiquées et les gènes identifiés",
            font_size=12,
            width=1000,     
            height=700)
        st.plotly_chart(fig, use_container_width=False)

        # ***************** Onglet Analyse par patient ************************
    with tabs[1]:
        st.markdown("<div class='section-title'>Analyse par patient</div>", unsafe_allow_html=True)
        st.metric("Nombre total de patients", len(df_final))
        selected_id = st.selectbox("Sélectionner un identifiant patient :", df_final['id'].dropna().unique())
        patient_data = df_final[df_final['id'] == selected_id]
        st.subheader("Fiche patient")
        st.write("Informations cliniques principales :")
        st.dataframe(patient_data[['leg_site_inc_nom', 'adm_sexe', 'adm_date_naissance', 'adm_occupation', 'diaCli_diagMR_nom',
                                'diaGen_var_hgcn_1', 'diaGen_var_nature_1_1', 'exaAcu_date',
                                'exaAcu_quant_OD', 'exaAcu_quant_OG', 'exaChv_date', 'exaChv_type']].T)
    
    # ************** Onglet Analyse comparative entre sites ******************
    with tabs[2]:
        st.markdown("<div class='section-title'>🏥 Analyse comparative entre sites</div>", unsafe_allow_html=True)
        with st.expander("▶️ Afficher la section Comparaison des sites", expanded=True):

            site_filter = st.selectbox("Choisir un site spécifique ou comparer tous les sites :", ["Tous les sites"] + sorted(df_final['leg_site_inc_nom'].dropna().unique()))

            if site_filter != "Tous les sites":
                site_data = df_final[df_final['leg_site_inc_nom'] == site_filter]
                st.metric(label="👥 Nombre de patients", value=len(site_data))

                st.subheader("📊 Heatmap des données")
                fig_map = px.imshow(site_data.isna(), text_auto=False)
                fig_map.update_layout(width=1000, height=800)
                st.plotly_chart(fig_map)

                st.subheader("📅 Répartition par âge à l’inclusion")
                st.write(f"Âge moyen : {site_data['leg_age_patientFREDD'].mean():.1f} ans")
                fig_age = px.histogram(site_data, x='leg_age_patientFREDD', nbins=20,labels={"age": "Âge",
                                    "leg_age_patientFREDD": "Âge"})
                st.plotly_chart(fig_age)
                
                # ************ Graphique des maladies identifiées pour chaque site ********************
                st.subheader("🎯 Répartition des maladies identifiées")
                fig_diag = px.histogram(site_data, x='diaCli_diagMR_nom', title="Distribution des diagnostics", labels={'diaCli_diagMR_nom': 'Maladie'})
                fig_diag.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_diag)

                st.subheader("🧬 Répartition des gènes identifiés")
                fig_genes = px.bar(site_data, x='diaGen_var_hgcn_1', title="Variants génétiques", labels={'diaGen_var_hgcn_1': 'Gène'})
                fig_genes.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_genes)

            else:
                # *************** Graphique Maladies identifiées pour tous les sites*****************
                st.subheader("🔎 Comparaison des maladies identifiées entre sites")

                df_final['diaCli_diagMR_nom'] = df_final['diaCli_diagMR_nom'].fillna('Missing')
                grouped = df_final.groupby(['leg_site_inc_nom', 'diaCli_diagMR_nom']).size().reset_index(name='count')

                # Regrouper les maladies < 10 en "Autres", par site
                def regrouper_maladies_rare(df_site):
                    df_site['maladie_affichée'] = df_site['diaCli_diagMR_nom']
                    rare_mask = df_site['count'] < 10
                    df_site.loc[rare_mask, 'maladie_affichée'] = 'Autres'
                    return df_site.groupby('maladie_affichée', as_index=False)['count'].sum()

                sites = grouped['leg_site_inc_nom'].unique()
                data_par_site = {site: regrouper_maladies_rare(grouped[grouped['leg_site_inc_nom'] == site]) for site in sites}

                fig = make_subplots(
                    rows=1, cols=len(sites),
                    specs=[[{'type': 'domain'}]*len(sites)],
                    subplot_titles=[f"Site : {site}" for site in sites]
                )

                colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

                for i, site in enumerate(sites):
                    df_site = data_par_site[site]
                    fig.add_trace(
                        go.Pie(
                            labels=df_site['maladie_affichée'],
                            values=df_site['count'],
                            name=site,
                            textinfo='percent+label+value',
                            showlegend=False,
                            marker=dict(colors=colors)
                        ),
                        row=1, col=i+1
                    )

                fig.update_layout(
                    title_text="<b>Répartition des maladies par site [maladies < 10 regroupées]</b>",
                    height=400,
                    width=800,
                    margin=dict(t=80, b=50)
                )
                st.plotly_chart(fig)

                # ************* Graphique des Gènes ***************
                st.subheader("🧬 Comparaison gènes, classes entre sites")
                grouped = df_final.groupby(['diaGen_var_hgcn_1', 'leg_site_inc_nom']).size().reset_index(name='count')
                color_mapping = {
                    'HNV15-20': 'red',
                    'HUV': 'blue'
                }
                fig_global_genes = px.bar(
                    grouped,
                    x='diaGen_var_hgcn_1',
                    y='count',
                    color='leg_site_inc_nom',
                    barmode='group',
                    text='count',
                    # color_discrete_map=color_mapping,
                    labels={'diaGen_var_hgcn_1': 'Gènes', 'count': 'Nombre de cas', 'leg_site_inc_nom': 'Site'},
                    title="🧬 Comparaison des gènes identifiés entre sites",
                    height=1200
                )
                fig_global_genes.update_traces(
                    textposition='outside',
                    hovertemplate="<b>%{y}</b><br>Cases: %{x}",)
                fig_global_genes.update_layout(xaxis_tickangle=-45)

                # ****************** Graphique Gène ↔ Nb de variants ***********************
                gene_var_count_all = df_final.groupby(['diaGen_var_hgcn_1', 'leg_site_inc_nom'])['diaGen_var_nbvar_1'].sum().reset_index().dropna()
                gene_var_count_all.columns = ['Gène', 'Site', 'Total variants']

                fig_gene_grouped = px.bar(
                    gene_var_count_all,
                    x='Gène',
                    y='Total variants',
                    color='Site',
                    text='Total variants',
                    barmode='group',
                    # color_discrete_map=color_mapping,
                    labels={'diaGen_var_hgcn_1': 'Gènes', 'leg_site_inc_nom': 'Site'},
                    title="🧬 Comparaison du nombre total de variants détectés par gène entre les sites",
                    height=1200)
                
                fig_gene_grouped.update_traces(
                    textposition='outside',
                    hovertemplate="<b>%{y}</b><br>Cases: %{x}",)
                fig_gene_grouped.update_layout(xaxis_tickangle=-45)

                tab1, tab2 = st.tabs(["Gènes entre les deux sites", "Variant par gène entre les sites"])
                with tab1:
                    st.plotly_chart(fig_global_genes, theme="streamlit", use_container_width=True)
                with tab2:
                    st.plotly_chart(fig_gene_grouped, theme="streamlit", use_container_width=True)
                
                # ************ Graphique Gène ↔ Classe du variant *********************
                st.subheader("🧪 Classe des variants par gène sur le top 10 des gènes")
                classe_labels = {
                1: "Inconnu",
                2: "Indéterminé",
                3: "Signification incertaine",
                4: "Probablement pathogène",
                5: "Pathogène"
                }

                gene_class = df_final.groupby(['diaGen_var_hgcn_1', 'diaGen_var_classe_1_1', 'leg_site_inc_nom'])\
                                    .size().reset_index(name='Occurrences').dropna()

                # Mapper les classes
                gene_class['Classe_label'] = gene_class['diaGen_var_classe_1_1'].map(classe_labels)

                # Filtrer sur les 10 gènes les plus fréquents
                top_genes = gene_class['diaGen_var_hgcn_1'].value_counts().nlargest(10).index
                gene_class = gene_class[gene_class['diaGen_var_hgcn_1'].isin(top_genes)]

                # Barplot groupé avec facettes verticales
                fig_gene_class = px.bar(
                    gene_class,
                    x='diaGen_var_hgcn_1',
                    y='Occurrences',
                    text='Occurrences',
                    color='leg_site_inc_nom',
                    barmode='group',
                    facet_row='Classe_label',
                    labels={
                        'diaGen_var_hgcn_1': 'Gène',
                        'leg_site_inc_nom': 'Site',
                        'Occurrences': 'Nombre de variants',
                        'Classe_label': 'Classe'
                    },
                    title="📊 Répartition des classes de variants sur le top 10 des gènes par site"
                )

                fig_gene_class.update_layout(
                    height=1200,
                    margin=dict(t=100),
                    xaxis_tickangle=-45,
                    legend_title_text='Site'
                )
                fig_gene_class.update_traces(
                    textposition='outside',
                    hovertemplate="<b>%{y}</b><br>Cases: %{x}",)
                fig_gene_class.update_layout(xaxis_tickangle=-45)

                st.plotly_chart(fig_gene_class, use_container_width=True)

                # 6. Sunburst Gène ↔ Classe ↔ Nature
                st.subheader("🌞 Vue hiérarchique des variants (gène → classe → nature)")
                sunburst_df = df_final.dropna(subset=['diaGen_var_hgcn_1', 'diaGen_var_classe_1_1', 'diaGen_var_nature_1_1'])
                fig_sunburst = px.sunburst(sunburst_df, path=['diaGen_var_hgcn_1', 'diaGen_var_classe_1_1', 'diaGen_var_nature_1_1'],
                                        title="Hiérarchie des gènes, classes et natures de mutation")
                # Augmenter la taille du graphique
                fig_sunburst.update_layout(
                    width=1000,   # Largeur en pixels
                    height=800    # Hauteur en pixels
)
                st.plotly_chart(fig_sunburst, use_container_width=True)
                # *************** Examen de l'acuité visuelle *******************
                st.subheader("👓 Comparaison des types d'examen d'acuité visuelle")
                variables = ['exaAcu_type_examen_OG', 'exaAcu_type_examen_OD']
                variable_labels = {
                    'exaAcu_type_examen_OG': "Type d'examen OG",
                    'exaAcu_type_examen_OD': "Type d'examen OD"
                }
                label_map = {
                    '1.0': 'Monoyer',
                    '2.0': 'Pigassou',
                    '3.0': 'Bébé vision',
                    '4.0': 'Cardiff',
                    '5.0': 'EDTRS',
                    '6.0': 'Autre',
                    'nan': 'Inconnu'
                }
                selected_sites = st.multiselect("Sélectionner les sites à comparer :", df_final['leg_site_inc_nom'].dropna().unique(), default=df_final['leg_site_inc_nom'].dropna().unique())

                for site in selected_sites:
                    st.markdown(f"### 🏥 Site : {site}")
                    df_site = df_final[df_final['leg_site_inc_nom'] == site]
                    fig = make_subplots(
                        rows=1, cols=2,
                        subplot_titles=[variable_labels[var] for var in variables],
                        specs=[[{'type': 'domain'}, {'type': 'domain'}]])
                    for i, col in enumerate(variables):
                        counts = df_site[col].value_counts(dropna=False).reset_index()
                        counts.columns = ['category', 'count']
                        counts['category'] = counts['category'].astype(str)
                        counts['label'] = counts['category'].replace(label_map)
                        fig.add_trace(go.Pie(labels=counts['label'], values=counts['count'], textinfo='percent+value+label'), row=1, col=i+1)
                    fig.update_layout(
                        height=400,
                        width=800,
                        margin=dict(t=80, b=50))
                    st.plotly_chart(fig, use_container_width=True)

    # ************ Onglet glossaire des variables *****************
    with tabs[3]:
        st.markdown("<div class='section-title'>📚 Glossaire des variables</div>", unsafe_allow_html=True)
        if glossaire_file and glossaire is not None:
            st.write("Ci-dessous la liste des variables avec leurs définitions :")
            st.dataframe(glossaire)
        else:
            st.info("Veuillez charger un fichier de glossaire pour afficher les définitions des variables.")
else:
    st.warning("Veuillez charger au moins un fichier CSV pour continuer.")
