import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

# =============================================================================
# SIDEBAR COMPONENT
# =============================================================================

def create_sidebar():
    """Erstellt eine einfache Sidebar mit Navigation"""
    return html.Div([
        html.H4("Navigation", style={'margin': '20px'}),
        dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.I(className="fas fa-home me-2"),  # Haus Icon
                        "Intro Beringung"
                    ],
                    href="/",
                    active="exact",
                    id="nav-intro",
                    style={
                        'border': '1px solid #dee2e6',
                        'border-radius': '5px',
                        'padding': '10px',
                        'margin-bottom': '10px',
                        'color': '#6c757d'
                    }
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-chart-line me-2"),  # Zeitverlauf Icon
                        "Zeitverlauf"
                    ],
                    href="/development",
                    active="exact",
                    id="nav-zeitverlauf",
                    style={
                        'border': '1px solid #dee2e6',
                        'border-radius': '5px',
                        'padding': '10px',
                        'margin-bottom': '10px',
                        'color': '#6c757d'
                    }
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-map-marker-alt me-2"),  # Ort Icon
                        "Fangorte"
                    ],
                    href="/places",
                    active="exact",
                    id="nav-fangorte",
                    style={
                        'border': '1px solid #dee2e6',
                        'border-radius': '5px',
                        'padding': '10px',
                        'margin-bottom': '10px',
                        'color': '#6c757d'
                    }
                ),
                dbc.Button("Logout", id="logout-button", style={'backgroundColor': '#A0522D', 'borderColor': '#A0522D', 'color': 'white'},  size="sm")
            ],
            vertical=True,
            pills=True,
        )
    ], style={
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '250px',
        'padding': '20px 10px',
        'background-color': '#f8f9fa',
        'border-right': '1px solid #dee2e6'
        ,'color': '#6c757d'
    })

def create_layout_with_sidebar(content):
    """Wrapper für Content mit Sidebar"""
    return html.Div([
        create_sidebar(),
        html.Div(
            content,
            style={
                'margin-left': '270px',  # Platz für Sidebar
                'padding': '20px'
            }
        )
    ])

