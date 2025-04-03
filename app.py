import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Initialisation de l'application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Chargement des données
df = pd.read_csv("supermarket_sales.csv")

# Transformation des dates
df['Date'] = pd.to_datetime(df['Date'])
df['Week'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)  

# Définition des options de sélection
genre_options = [
    {'label': 'Tout les genres', 'value': 'tout les genres'},
    {'label': 'Homme', 'value': 'Male'},
    {'label': 'Femme', 'value': 'Female'}    
]

ville_options = [
    {'label': 'Toutes les villes', 'value': 'toutes les villes'},
    {'label': 'Yangon', 'value': 'Yangon'},
    {'label': 'Naypyitaw', 'value': 'Naypyitaw'},
    {'label': 'Mandalay', 'value': 'Mandalay'}
]

# Layout
def etoiles_style(stars):
    return html.Span(stars, style={
        "color": "gold", "fontSize": "45px", "textShadow": "2px 2px 4px #000"
    })


# Layout de l'application
app.layout = dbc.Container(
    fluid=True,
    children=[
    # Titre
    dbc.Row([
        dbc.Col(html.H3("STORE ANALYSIS", className="text-left", style={
            "fontSize": "30px", "color": "lightgreen", "fontWeight": "bold"}), md=6,
            style={"height": "7vh", "display": "flex", "alignItems": "center", 
                   "justifyContent": "flex-start", "backgroundColor": "darkgreen", "paddingLeft": "15px"}),

        dbc.Col([
            dcc.Dropdown(id="genre", options=genre_options, value="tout les genres", placeholder="Choisissez un genre",
                         style={"fontSize": "16px", "height": "40px", "width": "100%", "borderRadius": "50px",
                                "backgroundColor": "khaki", "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.2)"}),

            dcc.Dropdown(id="ville", options=ville_options, value="toutes les villes", placeholder="Choisissez une ville",
                         style={"fontSize": "16px", "height": "40px", "width": "100%", "borderRadius": "50px",
                                "backgroundColor": "khaki", "boxShadow": "4px 4px 8px rgba(0, 0, 0, 0.2)"})
        ], md=6, style={"height": "7vh", "display": "flex", "alignItems": "center", "backgroundColor": "darkgreen"}),
    ], style={"marginBottom": "10px"}),

    # Indicateur d'étoiles
    dbc.Row([
        dbc.Col(html.Div(id="etoiles_output", style={"fontSize": "30px", "textAlign": "center", "marginBottom": "15px"}))
    ]),

    # Graphique
    dbc.Row([ # ligne pour afficher 'montant_tot'
        dbc.Row([
        dbc.Col(dcc.Graph(id='montant_tot'), style={
            "min-height": "100px",
            "textAlign": "center",
            "border": "8px solid darkgreen",
            "borderRadius": "10px",
            "margin": "0px 10px 10px 10px", # Ajoute une marge de 10 px en bas et à  droite et gauche
            "padding": "0",
            "boxShadow": "0px 4px 16px black"  
        }, md=12)])
        ]),

        dbc.Row([ # ligne s'éparer en 2 colonnes pour que chacunne affiche un graphique
        dbc.Col(dcc.Graph(id='histo_fig'), style={
            "min-height": "100px",
            "textAlign": "center",
            "border": "8px solid darkgreen",
            "borderRadius": "10px",
            "margin": "0 50px", 
            "padding": "0",
            "boxShadow": "4px 4px 8px black"   
        }, md=5),
        dbc.Col(dcc.Graph(id='S_achat'), style={
            "min-height": "100px",
            "textAlign": "center",
            "border": "8px solid darkgreen",
            "borderRadius": "10px",
            "margin": "0 50px", 
            "padding": "0",
            "boxShadow": "4px 4px 8px black"   
        }, md=5)
    ]),

    dbc.Row([
        dbc.Row([
        dbc.Col(dcc.Graph(id='diagramme_achat'), style={
            "min-height": "100px",
            "textAlign": "center",
            "border": "8px solid darkgreen",
            "borderRadius": "10px",
            "margin": "10px 10px", # Ajoute une marge de 50px à gauche et à droite
            "padding": "0",
            "boxShadow": "0px 4px 16px black"  
        }, md=12)])
        ])
    

], style={"backgroundColor": "tan"})


# Callback pour mettre à jour les étoiles
@app.callback(
    Output("etoiles_output", "children"),
    [Input("genre", "value"),
     Input("ville", "value")]
)
def update_etoiles(selected_genre, selected_ville):
    filtered_df = df if selected_ville == "toutes les villes" else df[df['City'] == selected_ville]
    df_genre_ville = filtered_df if selected_genre == "tout les genres" else filtered_df[filtered_df['Gender'] == selected_genre]

    if df_genre_ville.empty or "Rating" not in df_genre_ville.columns:
        return "Note indisponible"

    avg_rating = df_genre_ville["Rating"].mean()
    full_stars = int(avg_rating)
    half_star = 1 if (avg_rating - full_stars) >= 0.5 else 0
    empty_stars = 10 - full_stars - half_star

    stars_display = "★" * full_stars + "⯨" * half_star + "☆" * empty_stars
    return html.Div([
        html.Span(f"Note moyenne de {selected_ville} et {selected_genre} : {round(avg_rating, 1)}/10 "),
        html.Br(), # pour faire un retour à la ligne
        etoiles_style(stars_display)
    ])



# Callback pour mettre à jour le graphique
@app.callback(
    [Output('montant_tot', 'figure'),
    Output('histo_fig', 'figure'),
    Output('S_achat', 'figure'),
    Output('diagramme_achat', 'figure')],
    [Input('genre', 'value'),
     Input('ville', 'value')]
)
def update_graphs(selected_genre, selected_ville):
    # Filtrage des données
    if selected_ville == "toutes les villes":
        # Agréger les données pour toutes les villes
        df_genre_ville = df if selected_genre == "tout les genres" else df[df['Gender'] == selected_genre]
        montant_tot = df_genre_ville.groupby(['Date'], as_index=False)['Total'].sum()
    else:
        # Filtrer par ville spécifique
        df_ville = df[df['City'] == selected_ville]
        df_genre_ville = df_ville if selected_genre == "tout les genres" else df_ville[df_ville['Gender'] == selected_genre]
        montant_tot = df_genre_ville.groupby(['Date', 'City'], as_index=False)['Total'].sum()

    # Dictionnaire des couleurs personnalisées
    colors_city = {
        'Yangon': 'red',
        'Naypyitaw': 'blue',
        'Mandalay': 'green'
    }

    colors_gender = {
        'Male': 'skyblue',
        'Female': 'pink'
    }

    # Création de la figure
    fig = go.Figure()

    if selected_ville == "toutes les villes":
        # Ajouter une seule courbe pour la somme de toutes les villes
        fig.add_trace(go.Scatter(
            x=montant_tot['Date'],
            y=montant_tot['Total'],
            mode='lines',
            name='toutes les villes',
            line=dict(width=3, color='purple'),
            opacity=1
        ))
    else:
        # Ajouter une courbe pour chaque ville avec ajustement d'opacité
        villes = df['City'].unique()
        for ville in villes:
            ville_df = df[df['City'] == ville]
            ville_df = ville_df if selected_genre == "tout les genres" else ville_df[ville_df['Gender'] == selected_genre]
            ville_tot = ville_df.groupby('Date', as_index=False)['Total'].sum()

            if ville == selected_ville:
                opacity = 1
                line_width = 3
            else:
                opacity = 0.3
                line_width = 1

            fig.add_trace(go.Scatter(
                x=ville_tot['Date'],
                y=ville_tot['Total'],
                mode='lines',
                name=ville,
                line=dict(width=line_width, color=colors_city.get(ville, 'black')),
                opacity=opacity
            ))

    couleur_fond_tracer = 'peachpuff'
    couleur_fond_papier = 'peachpuff'

    # Mise en page du graphique
    fig.update_layout(
        title=f"Évolution du montant des achats pour {selected_ville} et {selected_genre} en semaines",
        xaxis_title="Date d'achat (semaine)",
        yaxis_title="Montant total des achats",
        legend_title="Ville",
        plot_bgcolor=couleur_fond_tracer,  # Couleur de fond de la zone de traçage
        paper_bgcolor=couleur_fond_papier # Couleur de fond de la zone papier
        
    )

    # Histogramme de la répartition des montants totaux des achats par sexe et par ville
    histo_fig = px.histogram(df_genre_ville, x="Total", color='Gender',  color_discrete_map=colors_gender)

    # Mise en page de l'histogramme
    histo_fig.update_layout(
        title=f"Répartition des montants totaux des achats par sexe et <br> par ville pour {selected_ville}",
        xaxis_title="Montant d'achat",
        yaxis_title="Quantité total",
        legend_title="Genre",
        plot_bgcolor=couleur_fond_tracer,  
        paper_bgcolor=couleur_fond_papier
    )


    S_achat = go.Figure(
        go.Indicator(
            mode="number+delta",
            value=montant_tot['Total'].sum(),
            title=f"Somme du montant total des achats <br> par ville pour {selected_ville} et {selected_genre}"
        )
    ).update_layout(
        plot_bgcolor=couleur_fond_tracer,  
        paper_bgcolor=couleur_fond_papier
    )

    diagramme_achat = px.bar(
        df_genre_ville.groupby(['City', 'Gender'], as_index=False)['Total'].count(),
        x='City',
        y='Total',
        color='Gender',
        color_discrete_map=colors_gender,
        barmode='group',
        title=f"Nombre total d'achats par sexe et par {selected_ville}"
    ).update_layout(
        xaxis_title="Ville d'achat",
        yaxis_title="Nombre total d'achats",
        legend_title="Genre",
        plot_bgcolor=couleur_fond_tracer,  
        paper_bgcolor=couleur_fond_papier
    )

    return fig, histo_fig, S_achat, diagramme_achat


# Lancement de l'application
if __name__ == '__main__':
    app.run_server(debug=True)
