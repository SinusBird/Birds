import html
import dash
import pandas as pd
import plotly.express as px

from birddataload import get_latest_euring_species_code_url, load_csv_likabrow, load_birddatatodf
from datadupli import random_duplicate_and_increment_birdid, generate_additional_dates
from placeholder import create_placeholder_figure
from sidebar import create_layout_with_sidebar
from style import main_title
from dash import Dash, html, dcc, callback, Output, Input, State, ctx

dash.register_page(__name__)

# Load data to analyze
df = pd.read_csv('https://raw.githubusercontent.com/SinusBird/Birds/refs/heads/main/BirdCatches2.csv', encoding='unicode_escape')

# Load further bird data to display names
euring_species_url = get_latest_euring_species_code_url()
df_birdid = load_csv_likabrow(euring_species_url)
#print("test test ", df_birdid.head())

# Load name translations --- from club500 URL, ask about usage before data publication!!!!
df_birdnames = load_birddatatodf('https://www.club300.de/publications/wp-bird-list.php', debug=False)

if df_birdnames is not None:
    print("Bird names loaded")
    #print(df_birdnames.head())  # Zeige die ersten Zeilen des DataFrames
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
#print("Data", df.head())

# main page layout - currently a bar charts with number of ringings over time
main_layout = (

    html.Div([
    main_title('Lokale Bird-Analytics App mit Dash'),


    # Dropdown for Bird Type selection (with multiple selection enabled)
    dcc.Dropdown(
        options=[{'label': i, 'value': i} for i in df.BirdType.unique()] + [{'label': 'All Birds', 'value': 'all'}],
        value=df.BirdType.unique().tolist(),  # Default to all bird types selected
        id='dropdown-selection',
        multi=True,  # Enable multiple selection
        style={'fontFamily': 'Leto, sans-serif'}  # Same font as the axis labels
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
            style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%', 'fontFamily': 'Leto, sans-serif'}
        ),
        dcc.Dropdown(
            options=[
                {'label': 'Grouped bars', 'value': 'group'},
                {'label': 'Stacked bars', 'value': 'stack'}
            ],
            value='group',  # Default to grouped bars
            id='bar-mode',
            clearable=False,
            style={'width': '48%', 'display': 'inline-block', 'fontFamily': 'Leto, sans-serif'}
        ),
        html.Button(
            'Reset Zoom', 
            id='reset-zoom-button',
            style={
                'marginTop': '10px',
                'marginBottom': '10px',
                'fontFamily': 'Leto, sans-serif',
                'backgroundColor': '#f8f9fa',
                'border': '1px solid #ddd',
                'borderRadius': '4px',
                'padding': '5px 10px'
            }
        ),
        dcc.Graph(id='graph-content')
    ], style={'marginTop': '20px'})
]))

layout = create_layout_with_sidebar(main_layout)

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('aggregation-level', 'value'),
    Input('bar-mode', 'value'),
    Input('session', 'data'),
    Input('graph-content', 'relayoutData'),
    Input('reset-zoom-button', 'n_clicks')
)
def update_graph(bird_types, aggregation_level, bar_mode, session_data, relayout_data, reset_clicks):
    # Check if reset button was clicked
    if ctx.triggered_id == 'reset-zoom-button':
        relayout_data = None  # Reset zoom by setting relayout_data to None
    #if not session_data or not session_data.get('authenticated'):
    #    return create_placeholder_figure("🔒 Please log in to view bird analytics")

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
    
    # Filter data based on zoom range if available
    zoom_filtered_dff = dff.copy()
    if relayout_data and ('xaxis.range' in relayout_data or 'xaxis.range[0]' in relayout_data):
        # Get zoom range
        if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
            start_date = pd.to_datetime(relayout_data['xaxis.range[0]'])
            end_date = pd.to_datetime(relayout_data['xaxis.range[1]'])
        elif 'xaxis.range' in relayout_data:
            start_date = pd.to_datetime(relayout_data['xaxis.range'][0])
            end_date = pd.to_datetime(relayout_data['xaxis.range'][1])
        else:
            start_date = None
            end_date = None
            
        # Apply filter if we have valid dates
        if start_date and end_date:
            if aggregation_level == 'M':
                # For monthly aggregation, filter by the actual date
                zoom_filtered_dff = zoom_filtered_dff[
                    (zoom_filtered_dff['DateTimeID'] >= start_date) & 
                    (zoom_filtered_dff['DateTimeID'] <= end_date)
                ]
            elif aggregation_level == 'Y':
                # For yearly aggregation, extract the year and filter
                start_year = start_date.year
                end_year = end_date.year
                zoom_filtered_dff = zoom_filtered_dff[
                    (zoom_filtered_dff['DateTimeID'].dt.year >= start_year) & 
                    (zoom_filtered_dff['DateTimeID'].dt.year <= end_year)
                ]
    
    # Calculate total count per bird type for legend based on zoom-filtered data
    bird_totals = zoom_filtered_dff.groupby('BirdType')['BirdID'].nunique().to_dict()

    # Convert Aggregation back to datetime for better plotting if monthly
    if aggregation_level == 'M':
        grouped['Aggregation'] = pd.to_datetime(grouped['Aggregation'], format='%Y-%m')

    # Ensure that Aggregation is treated as categorical when 'Year' aggregation is selected
    if aggregation_level == 'Y':
        grouped['Aggregation'] = grouped['Aggregation'].astype(str)  # Convert to string for proper X-axis formatting

    # Define a color scale with visually distinct but not too vibrant colors
    color_scale = px.colors.qualitative.Set3

    # Determine if we're in a zoomed view
    is_zoomed = relayout_data and ('xaxis.range' in relayout_data or 'xaxis.range[0]' in relayout_data)
    
    # Create title with zoom indicator
    title = 'Birds first catches for ringing'
    if is_zoomed:
        title += ' (Zoomed View)'
    
    # Create the bar plot
    fig = px.bar(grouped,
                 x='Aggregation',
                 y='UniqueBirdCount',
                 color='BirdType',
                 title=title,
                 labels={'UniqueBirdCount': '', 'Aggregation': 'Date', 'BirdType': 'Bird type'},
                 barmode=bar_mode,  # Use stacked or grouped bars
                 color_discrete_sequence=color_scale)  # Use a custom, less vibrant color scale

    # Update layout for better readability and remove axis label for y-axis
    layout_updates = {
        'plot_bgcolor': 'white',  # Set the background color to white
        'xaxis': dict(showgrid=True, gridcolor='lightgray', gridwidth=0.5),  # Make x-axis grid lines medium gray
        'yaxis': dict(showgrid=True, gridcolor='lightgray', gridwidth=0.5, showticklabels=False),  # Remove Y-axis labels
        'title': {'x': 0.5},  # Center the title
        'legend_title_text': 'Bird type',
        'height': 600  # Increase height by 30% to create more space for labels
    }
    
    # Preserve zoom state if we're zoomed in
    if is_zoomed and not ctx.triggered_id == 'reset-zoom-button':
        # Extract the zoom range from relayoutData
        if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
            layout_updates['xaxis']['range'] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
        elif 'xaxis.range' in relayout_data:
            layout_updates['xaxis']['range'] = relayout_data['xaxis.range']
    
    fig.update_layout(**layout_updates)
    
    # Update legend to include total counts
    for i, bird_type in enumerate(fig.data):
        if bird_type.name in bird_totals:
            # Add a 👁️ symbol to indicate counts are for visible (zoomed) area only
            prefix = "👁️ " if is_zoomed else ""
            fig.data[i].name = f"{prefix}{bird_type.name} ({bird_totals[bird_type.name]})"

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
                title='Month',
                # Preserve any existing range settings
                **({"range": layout_updates['xaxis'].get('range')} if layout_updates['xaxis'].get('range') else {})
            )
        )
    elif aggregation_level == 'Y':
        fig.update_layout(
            xaxis=dict(
                tickformat='%Y',
                title='Year',
                # Preserve any existing range settings
                **({"range": layout_updates['xaxis'].get('range')} if layout_updates['xaxis'].get('range') else {})
            )
        )

    return fig
