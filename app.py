from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
from birddataload import load_csv_likabrow, load_birddatatodf
from datadupli import random_duplicate_and_increment_birdid, generate_additional_dates

# Load data to analyze
df = pd.read_csv('https://raw.githubusercontent.com/SinusBird/Birds/refs/heads/main/BirdCatches2.csv', encoding='unicode_escape')

# Load further bird data to display
df_birdid = load_csv_likabrow('https://euring.org/files/documents/EURINGSpeciesCodesMay2024.csv')
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
app = Dash(__name__)  

app.layout = html.Div([
    html.H1(children='Number of ringing', style={'textAlign': 'center'}),

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
    dcc.Graph(id='graph-content')
])


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


if __name__ == '__main__':
    app.run(debug=True)
