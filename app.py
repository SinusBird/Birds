import dash
import os
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import plotly.express as px
import pandas as pd
import numpy as np
import flask
from auth import verify_login
from birddataload import load_csv_likabrow, load_birddatatodf, get_latest_euring_species_code_url
from datadupli import random_duplicate_and_increment_birdid, generate_additional_dates

# Load data to analyze
df = pd.read_csv('https://raw.githubusercontent.com/SinusBird/Birds/refs/heads/main/BirdCatches2.csv', encoding='unicode_escape')

# Load further bird data to display names
euring_species_url = get_latest_euring_species_code_url()
df_birdid = load_csv_likabrow(euring_species_url)
print("test test ", df_birdid.head())

# Load name translations --- from club500 URL, ask about usage before data publication!!!!
df_birdnames = load_birddatatodf('https://www.club300.de/publications/wp-bird-list.php', debug=True)

if df_birdnames is not None: 
    print("Bird names loaded")
    print(df_birdnames.head())  # Zeige die ersten Zeilen des DataFrames
else:
    print("No bird names available")

# Merge species ID with the original dataframe to add species names
# TBD

# add more birds for catching and more time variety
df, repeat_counts = random_duplicate_and_increment_birdid(df, max_duplicates=20, seed=42)
df = generate_additional_dates(df, period_start='2021-01-01', period_end='2023-12-31', n_extra=2000, seed=42)

# Ensure DateTimeID is in the correct datetime format, and remove rows with invalid dates
df['DateTimeID'] = pd.to_datetime(df['DateTimeID'], errors='coerce')

# Drop rows where DateTimeID could not be parsed
df = df.dropna(subset=['DateTimeID'])

# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

flask_key = os.getenv("FLASK_KEY")
app.server.secret_key = flask_key  # aus Systemumgebungsvariable lokal ok

#  Dynamisches Layout basierend auf Login-Status
app.layout = lambda: html.Div([
    dcc.Location(id="url", refresh=False),  # Für URL-Tracking & Initial-Callback
    html.Div(id="page-content")             # Wird dynamisch durch Callback gefüllt
])

login_layout = html.Div([
    html.H2("Login"),
    dcc.Input(id="input-username", type="text", placeholder="Benutzername"),
    dcc.Input(id="input-password", type="password", placeholder="Passwort"),
    html.Button("Einloggen", id="login-button"),
    html.Div(id="login-message")
])

# Layout der Hauptseite - bisher  ein Dashboard
main_layout = html.Div([
    html.H1(children='🦉 Willkomen zur lokalen Bird-Analytics App mit Dash', style={'textAlign': 'center'}),

    # Dropdown for Bird Type selection (with multiple selection enabled)
    dcc.Dropdown(
        options=[{'label': i, 'value': i} for i in df.BirdType.unique()] + [{'label': 'All Birds', 'value': 'all'}],
        value=df.BirdType.unique().tolist(),  # Default to all bird types selected
        id='dropdown-selection',
        multi=True,  # Enable multiple selection
        style={'fontFamily': 'Arial, sans-serif'}  # Same font as the axis labels
    ),

    # Dropdown for Aggregation level (Per month or per year)
    html.Div([
        dcc.Dropdown(
            options=[
                {'label': 'Per month', 'value': 'M'},
                {'label': 'Per year', 'value': 'Y'}
            ],
            value='M',  # Default to monthly aggregation
            id='aggregation-level',
            clearable=False,
            style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'fontFamily': 'Arial, sans-serif'}
        ),
        dcc.Dropdown(
            options=[
                {'label': 'Grouped bars', 'value': 'group'},
                {'label': 'Stacked bars', 'value': 'stack'}
            ],
            value='group',  # Default to grouped bars
            id='bar-mode',
            clearable=False,
            style={'width': '48%', 'display': 'inline-block', 'fontFamily': 'Arial, sans-serif'}
        )
    ], style={'marginTop': '20px'}),

    # Graph to display the results
    dcc.Graph(id='graph-content'),
    html.Button("Abmelden", id="logout-button")
])

# Initiale Seitenanzeige je nach Login-Status
@app.callback(
    Output("page-content", "children", allow_duplicate=True),
    Input("url", "pathname"),
    prevent_initial_call='initial_duplicate'  # Damit beim Start aufgerufen wird
)
def display_page(_):
    if flask.session.get("logged_in"):
        return main_layout
    else:
        return login_layout

# Login / Logout Handling
@app.callback(
    Output("page-content", "children", allow_duplicate=True),
    Output("login-message", "children"),
    Input("login-button", "n_clicks"),
    Input("logout-button", "n_clicks"),
    State("input-username", "value"),
    State("input-password", "value"),
    prevent_initial_call=True
)
def login_logout(n_login, n_logout, username, password):
    triggered_id = ctx.triggered_id

    if triggered_id == "logout-button":
        flask.session["logged_in"] = False
        return login_layout, ""

    if triggered_id == "login-button":
        # Beispiel: hartkodierte Nutzerprüfung
        if username == "testuser" and password == "geheim":
            flask.session["logged_in"] = True
            return main_layout, ""
        else:
            return login_layout, "❌ Falscher Benutzername oder Passwort"

    raise dash.exceptions.PreventUpdate


@app.callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('aggregation-level', 'value'),
    Input('bar-mode', 'value')
)
def update_graph(bird_types, aggregation_level, bar_mode):
    # Ensure bird_types is always a list, even if 'all' is selected
    if 'all' in bird_types or not bird_types:  # If 'all' is selected or no bird types are selected
        df_filtered = df  # Include all bird types
    else:
        df_filtered = df[df['BirdType'].isin(bird_types)]  # Filter by selected bird types

    # Filter data for first catch only
    df_filtered['IsFirstCatch'] = pd.to_numeric(df_filtered['IsFirstCatch'], errors='coerce')
    dff = df_filtered[df_filtered['IsFirstCatch'] == 1]

    # Add aggregation column (Month or Year)
    if aggregation_level == 'M':
        dff['Aggregation'] = dff['DateTimeID'].dt.to_period('M').dt.strftime('%Y-%m')  # Group by month
    elif aggregation_level == 'Y':
        dff['Aggregation'] = dff['DateTimeID'].dt.to_period('Y').dt.strftime('%Y')  # Group by year

    # Group by Aggregation and BirdType
    grouped = dff.groupby(['Aggregation', 'BirdType'])['BirdID'].nunique().reset_index()

    # Rename BirdID to UniqueBirdCount
    grouped.rename(columns={'BirdID': 'UniqueBirdCount'}, inplace=True)

    # Convert Aggregation back to datetime for better plotting if monthly
    if aggregation_level == 'M':
        grouped['Aggregation'] = pd.to_datetime(grouped['Aggregation'], format='%Y-%m')

    # Ensure that Aggregation is treated as categorical when 'Year' aggregation is selected
    if aggregation_level == 'Y':
        grouped['Aggregation'] = grouped['Aggregation'].astype(str)  # Convert to string for proper X-axis formatting

    # Define a color scale with visually distinct but not too vibrant colors
    color_scale = px.colors.qualitative.Set3

    # Create the bar plot
    fig = px.bar(grouped,
                 x='Aggregation',
                 y='UniqueBirdCount',
                 color='BirdType',
                 title='Birds first catches for ringing',
                 labels={'UniqueBirdCount': '', 'Aggregation': 'Date', 'BirdType': 'Bird type'},
                 barmode=bar_mode,  # Use stacked or grouped bars
                 color_discrete_sequence=color_scale)  # Use a custom, less vibrant color scale

    # Update layout for better readability and remove axis label for y-axis
    fig.update_layout(
        plot_bgcolor='white',  # Set the background color to white
        xaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.5),  # Make x-axis grid lines medium gray
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.5, showticklabels=False),  # Remove Y-axis labels
        title={'x': 0.5},  # Center the title
        legend_title_text='Bird type',
        height=600  # Increase height by 30% to create more space for labels
    )

    # Add bar labels if they fit
    fig.update_traces(
        texttemplate='%{y}',  # Text format
        textposition='outside',  # Position at the top outside the bars
        insidetextanchor='middle',  # Keep text centered
        textfont=dict(size=12, color='black'),  # Set font size and color for text
    )

    # Automatically hide text labels when there's not enough space
    fig.update_traces(
        texttemplate='%{y}',  # Add the value above each bar
        textposition='outside',  # Place text above the bars
        textangle=0,  # Set text orientation to horizontal
        textfont=dict(size=12, color='black')  # Use consistent font size
    )

    # Update tick format for X-axis
    if aggregation_level == 'M':
        fig.update_layout(
            xaxis=dict(
                tickformat='%b %Y',
                title='Month'
            )
        )
    elif aggregation_level == 'Y':
        fig.update_layout(
            xaxis=dict(
                tickformat='%Y',
                title='Year'
            )
        )

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)