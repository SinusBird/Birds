from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('https://raw.githubusercontent.com/SinusBird/Birds/refs/heads/main/BirdCatches.csv', encoding='unicode_escape')

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

# Initialize Dash app
app = Dash()

app.layout = [
    html.H1(children='Birds per Types', style={'textAlign': 'center'}),
    dcc.Dropdown(
        options=[{'label': i, 'value': i} for i in df.BirdType.unique()],
        value=df.BirdType.iloc[0],  # Default to the first bird type
        id='dropdown-selection'
    ),
    dcc.Graph(id='graph-content')
]

@app.callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    # Filter data based on the selected BirdType
    dff = df[df.BirdType == value]

    # Ensure DateTimeID is in the correct datetime format
    dff['DateTimeID'] = pd.to_datetime(dff['DateTimeID'], errors='coerce')
    dff = dff.dropna(subset=['DateTimeID'])  # Remove rows with invalid DateTimeID

    # Sort values by DateTimeID
    dff = dff.sort_values(by='DateTimeID')

    # Group by DateTimeID and count unique BirdID values
    grouped = dff.groupby('DateTimeID')['BirdID'].nunique().reset_index()

    # Rename BirdID to UniqueBirdCount
    grouped.rename(columns={'BirdID': 'UniqueBirdCount'}, inplace=True)

    # Create line plot
    return px.line(grouped, x='DateTimeID', y='UniqueBirdCount', title='Number of Unique Birds')

if __name__ == '__main__':
    app.run(debug=True)