import plotly.graph_objects as go
def create_placeholder_figure(message="Please log in to view content"):
    """Erstellt eine Platzhalter-Figur für nicht-authentifizierte Benutzer"""
    fig = go.Figure()
    fig.add_annotation(
        x=0.5, y=0.5,
        text=message,
        showarrow=False,
        font=dict(size=20, color="gray"),
        xref="paper", yref="paper"
    )
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=400
    )
    return fig