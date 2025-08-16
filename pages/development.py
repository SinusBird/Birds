import dash
import pandas as pd
import plotly.express as px
import datetime
import dash_bootstrap_components as dbc

from sidebar import create_layout_with_sidebar
from style import main_title
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
from datetime import date
from birddataload import prep_birddata

dash.register_page(__name__)

df = prep_birddata()

# main page layout - currently a bar charts with number of ringings over time
main_layout = (
    html.Div([
        dbc.Row([
            dbc.Col([main_title('Lokale Bird-Analytics App mit Dash')],
                    width=12)
        ]),
        # Dropdown for Bird Type selection (with multiple selection enabled)
        dbc.Row([
            dbc.Col([dcc.Dropdown(
                options=[{'label': i, 'value': i} for i in df.Name.unique()] + [{'label': 'All Birds', 'value': 'all'}],
                value=df.Name.unique().tolist(),  # Default to all bird types selected
                id='dropdown-selection',
                multi=True)],  # Enable multiple selection
                width=12
            ),
        ], className="mb-3"),
        dbc.Row([
            # Dropdown for Aggregation level (Per month or per year) as well as time filter
            dbc.Col([dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(2000, 1, 1),
                max_date_allowed=date(2025, 12, 31),
                start_date=date(2023, 1, 1),
                end_date=date(2023, 12, 31))],
                width=4
            ),
            # oder '0.8em' für relative Größe
            dbc.Col([dcc.Dropdown(
                options=[
                    {'label': 'Pro Monat', 'value': 'M'},
                    {'label': 'Pro Jahr', 'value': 'J'}
                ],
                value='M',  # Default to monthly aggregation
                id='aggregation-level',
                clearable=False)], #,
                #style={'width': '33%', 'display': 'inline-block', 'marginRight': '2%', 'fontFamily': 'Leto, sans-serif'})
                width=4
            ),
            dbc.Col([dcc.Dropdown(
                options=[
                    {'label': 'Gruppierte Balken', 'value': 'group'},
                    {'label': 'Gestapelte Balken', 'value': 'stack'}
                ],
                value='group',  # Default to grouped bars
                id='bar-mode',
                clearable=False)],
                #style={'width': '33%', 'display': 'inline-block', 'fontFamily': 'Leto, sans-serif'}
                width=4
            )
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([dbc.Button(
                'Reset Zoom',
                id='reset-zoom-button',
                color="primary",
                style={'backgroundColor': '#A0522D', 'borderColor': '#A0522D'},
                size="sm")],
                width=12)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([dcc.Graph(id='graph-content-time')],width=12)
        ])
    ], style={'fontFamily': 'Lato, sans-serif', 'marginBottom': '5px'})
)

layout = create_layout_with_sidebar(main_layout)

@callback(
    Output('graph-content-time', 'figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('dropdown-selection', 'value'),
    Input('aggregation-level', 'value'),
    Input('bar-mode', 'value'),
    Input('session', 'data'),
    Input('graph-content-time', 'relayoutData'),
    Input('reset-zoom-button', 'n_clicks')
)
def update_time_graph(start_date, end_date,bird_types, aggregation_level, bar_mode, session_data, relayout_data, reset_clicks):
    # Check if reset button was clicked
    if ctx.triggered_id == 'reset-zoom-button':
        relayout_data = None  # Reset zoom by setting relayout_data to None
    #if not session_data or not session_data.get('authenticated'):
    #    return create_placeholder_figure("🔒 Please log in to view bird analytics")

    # Ensure bird_types is always a list, even if 'all' is selected
    if 'all' in bird_types or not bird_types:  # If 'all' is selected or no bird types are selected
        df_filtered = df  # Include all bird types
    else:
        df_filtered = df[df['Name'].isin(bird_types)]  # Filter by selected bird types

    ## Ensure time filter is taken into account
    if start_date is not None and end_date is not None:
        df_filtered = df_filtered[(df_filtered['Fangtag'] >= start_date) & (df_filtered['Fangtag'] <= end_date)]
    elif start_date is not None:
        df_filtered = df_filtered[df_filtered['Fangtag'] >= start_date]
    elif end_date is not None:
        df_filtered = df_filtered[df_filtered['Fangtag'] <= end_date]

    # Filter data for first catch only - nessecary??
    #df_filtered['IsFirstCatch'] = pd.to_numeric(df_filtered['IsFirstCatch'], errors='coerce')
    dff = df_filtered #[df_filtered['IsFirstCatch'] == 1]

    # Add aggregation column (Month or Year)
    if aggregation_level == 'M':
        dff['Aggregation'] = dff['Fangtag'].dt.to_period('M').dt.strftime('%Y-%m')  # Group by month
    elif aggregation_level == 'Y':
        dff['Aggregation'] = dff['Fangtag'].dt.to_period('Y').dt.strftime('%Y')  # Group by year

    # Group by Aggregation and BirdType
    grouped = dff.groupby(['Aggregation', 'Name'])['strRingNr'].nunique().reset_index()

    # Rename BirdID to UniqueBirdCount
    grouped.rename(columns={'strRingNr': 'UniqueBirdCount'}, inplace=True)
    
    # Calculate total birds per month/year for the x-axis labels
    total_birds_per_period = dff.groupby('Aggregation')['strRingNr'].nunique().reset_index()
    total_birds_per_period.rename(columns={'strRingNr': 'TotalBirdsCount'}, inplace=True)

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
        else: # get date from selection if no zoom
            if start_date is not None:
                start_date = datetime.date.fromisoformat(start_date)
            if end_date is not None:
                end_date = datetime.date.fromisoformat(end_date)
            
        # Apply filter if we have valid dates
        if start_date and end_date:
            if aggregation_level == 'M':
                # For monthly aggregation, filter by the actual date
                zoom_filtered_dff = zoom_filtered_dff[
                    (zoom_filtered_dff['Fangtag'] >= start_date) &
                    (zoom_filtered_dff['Fangtag'] <= end_date)
                ]
            elif aggregation_level == 'Y':
                # For yearly aggregation, extract the year and filter
                start_year = start_date.year
                end_year = end_date.year
                zoom_filtered_dff = zoom_filtered_dff[
                    (zoom_filtered_dff['Fangtag'].dt.year >= start_year) &
                    (zoom_filtered_dff['Fangtag'].dt.year <= end_year)
                ]
    
    # Calculate total count per bird type for legend based on zoom-filtered data
    bird_totals = zoom_filtered_dff.groupby('Name')['strRingNr'].nunique().to_dict()

    # Convert Aggregation back to datetime for better plotting if monthly
    if aggregation_level == 'M':
        grouped['Aggregation'] = pd.to_datetime(grouped['Aggregation'], format='%Y-%m')
        total_birds_per_period['Aggregation'] = pd.to_datetime(total_birds_per_period['Aggregation'], format='%Y-%m')

    # Ensure that Aggregation is treated as categorical when 'Year' aggregation is selected
    if aggregation_level == 'J':
        grouped['Aggregation'] = grouped['Aggregation'].astype(str)  # Convert to string for proper X-axis formatting
        total_birds_per_period['Aggregation'] = total_birds_per_period['Aggregation'].astype(str)

    # Define a color scale with visually distinct but not too vibrant colors
    color_scale = px.colors.qualitative.Set3

    # Determine if we're in a zoomed view
    is_zoomed = relayout_data and ('xaxis.range' in relayout_data or 'xaxis.range[0]' in relayout_data)
    
    # Create title with zoom indicator
    title = 'Birds catches'
    if is_zoomed:
        title += ' (Zoomed View)'
    
    # Create the bar plot
    fig = px.bar(grouped,
                 x='Aggregation',
                 y='UniqueBirdCount',
                 color='Name',
                 title=title,
                 labels={'UniqueBirdCount': '', 'Aggregation': 'Date', 'Name': 'Bird type'},
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

    # Update tick format for X-axis and add total bird counts below the labels
    if aggregation_level == 'M':
        # Create a dictionary mapping dates to their total bird counts
        date_to_total = dict(zip(total_birds_per_period['Aggregation'], total_birds_per_period['TotalBirdsCount']))
        
        # Get all unique dates from the grouped dataframe
        all_dates = sorted(grouped['Aggregation'].unique())
        
        # Create custom tick texts with total counts below the month labels
        tick_texts = []
        for date in all_dates:
            month_year = date.strftime('%b %Y')
            total = date_to_total.get(date, 0)
            tick_texts.append(f"{month_year}<br>Total: {total}")
        
        fig.update_layout(
            xaxis=dict(
                # Use custom tick texts with total counts
                tickvals=all_dates,
                ticktext=tick_texts,
                title='Monat',
                # Show more ticks (labels) for months - display as many as possible
                nticks=50,  # Set a high number to show more ticks
                # Preserve any existing range settings
                **({"range": layout_updates['xaxis'].get('range')} if layout_updates['xaxis'].get('range') else {})
            )
        )
    elif aggregation_level == 'Y':
        # Create a dictionary mapping years to their total bird counts
        year_to_total = dict(zip(total_birds_per_period['Aggregation'], total_birds_per_period['TotalBirdsCount']))
        
        # Get all unique years from the grouped dataframe
        all_years = sorted(grouped['Aggregation'].unique())
        
        # Create custom tick texts with total counts below the year labels
        tick_texts = []
        for year in all_years:
            total = year_to_total.get(year, 0)
            tick_texts.append(f"{year}<br>Total: {total}")
        
        fig.update_layout(
            xaxis=dict(
                # Use custom tick texts with total counts
                tickvals=all_years,
                ticktext=tick_texts,
                title='Jahr',
                # Show all year labels
                nticks=50,  # Set a high number to show more ticks
                # Preserve any existing range settings
                **({"range": layout_updates['xaxis'].get('range')} if layout_updates['xaxis'].get('range') else {})
            )
        )

    return fig
