import dash_bootstrap_components as dbc
from dash import html

# =============================================================================
# LOGIN COMPONENT
# =============================================================================

def create_login_form():
    """Erstellt Login-Formular"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H3("🦉 Bird Analytics - Login", className="text-center")),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Label("Benutzername", html_for="username"),
                                dbc.Input(
                                    type="text",
                                    id="username",
                                    placeholder="Benutzername eingeben"
                                ),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Label("Passwort", html_for="password"),
                                dbc.Input(
                                    type="password",
                                    id="password",
                                    placeholder="Passwort eingeben"
                                ),
                            ], className="mb-3"),
                            dbc.Button(
                                "Anmelden",
                                id="login-button",
                                color="primary",
                                className="w-100"
                            )
                        ])
                    ])
                ], style={"maxWidth": "400px"}),
                html.Div(id="login-output", className="mt-3")
            ], width=12, className="d-flex justify-content-center")
        ], className="min-vh-100 align-items-center")
    ])
