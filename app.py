from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('https://raw.githubusercontent.com/SinusBird/Birds/refs/heads/main/BirdCatches2.csv', encoding='unicode_escape')

# Function to randomly duplicate rows and increment BirdID
def random_duplicate_and_increment_birdid(df, max_duplicates=5, seed=None):
    if seed is not None:
        np.random.seed(seed)  # Optional: Set seed for reproducibility

    # Generate a random number of duplicates for each row
    repeat_counts = np.random.randint(1, max_duplicates + 1, size=len(df))
    
    # Repeat rows based on the random counts
    duplicated_df = df.loc[df.index.repeat(repeat_counts)].reset_index(drop=True)
    
    # Update BirdID with a continuous sequence
    duplicated_df['BirdID'] = np.arange(1, len(duplicated_df) + 1)
    
    return duplicated_df, repeat_counts

# Apply the function
df, repeat_counts = random_duplicate_and_increment_birdid(df, max_duplicates=5, seed=42)

# Ensure DateTimeID is in the correct datetime format
df['DateTimeID'] = pd.to_datetime(df['DateTimeID'], errors='coerce')

# Drop rows with invalid DateTimeID
df = df.dropna(subset=['DateTimeID'])

# Generate a list of unique bird types for dropdown
unique_bird_types = df['BirdType'].unique()

# Create a color map for bird types
color_palette = px.colors.qualitative.Safe  # Subtle but distinct colors
color_map = {bird: color_palette[i % len(color_palette)] for i, bird in enumerate(unique_bird_types)}

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Birds per Types', style={'textAlign': 'center'}),

    # Dropdown for selecting bird types (multiple options)
    dcc.Dropdown(
        options=[{'label': 'All', 'value': 'all'}] + [{'label': bird, 'value': bird} for bird in unique_bird_types],
        value=['all'],  # Default to "All"
        id='dropdown-selection',
        multi=True,  # Allow multiple selections
        placeholder='Select Bird Types'
    ),

    # Dropdown for selecting aggregation level (Month or Year)
    html.Div([
        dcc.Dropdown(
            options=[
                {'label': 'Per month', 'value': 'M'},
                {'label': 'Per year', 'value': 'Y'}
            ],
            value='M',  # Default to monthly aggregation
            id='aggregation-level',
            clearable=False,
            style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}
        ),
        dcc.Dropdown(
            options=[
                {'label': 'Stacked bars', 'value': 'stack'},
                {'label': 'Grouped bars', 'value': 'group'}
            ],
            value='group',  # Default to grouped bars
            id='bar-mode',
            clearable=False,
            style={'width': '48%', 'display': 'inline-block'}
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

    # If 'all' is selected or no bird types are selected, include all bird types
    if 'all' in bird_types or not bird_types:
        df_filtered = df
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

    # Ensure Aggregation is treated as categorical when 'Year' aggregation is selected
    if aggregation_level == 'Y':
        grouped['Aggregation'] = grouped['Aggregation'].astype(str)  # Convert to string for proper X-axis formatting

    # Create the bar plot
    fig = px.bar(grouped, 
                 x='Aggregation', 
                 y='UniqueBirdCount', 
                 color='BirdType', 
                 title='Birds First Catch for Ringing',
                 labels={'UniqueBirdCount': '', 'Aggregation': 'Date'},
                 color_discrete_map=color_map,  # Ensure consistent colors for bird types
                 barmode=bar_mode)  # Use stacked or grouped bars

    # Update layout for better readability
    fig.update_layout(
        plot_bgcolor='white',  # Set the background color to white
        xaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.5),  # Make x-axis grid lines medium gray
        yaxis=dict(showgrid=True, gridcolor='lightgray', gridwidth=0.5),  # Make y-axis grid lines medium gray
        title={'x': 0.5},  # Center the title
        legend_title_text='Bird Types:'
    )

    # Add bar labels if they fit
    fig.update_traces(
        texttemplate='%{y}',  # Text format
        textposition='inside',  # Position within the bar
        textangle=0,  # Set text orientation to horizontal
        insidetextanchor='middle'  # Keep text centered
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
