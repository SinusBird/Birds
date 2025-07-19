import dash
##import dash_auth
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State

from auth import verify_login
from login import create_login_form

# Initialize Dash app
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                use_pages=True,
                suppress_callback_exceptions=True)

#with open('users.json') as json_file:
#    credentials = json.load(json_file)
#auth = dash_auth.BasicAuth( # do not use! non hashed pws!
#    app,
#    credentials
#)

#app.layout = html.Div([
    #dcc.Store(id="session", storage_type="session"),
    #dcc.Location(id="url", refresh=False),
    #html.Div([
    #    html.Div(
    #        dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    #    ) for page in dash.page_registry.values()
    #]),
    #dash.page_container
#])

# =============================================================================
# APP SETUP
# =============================================================================

# Main layout with authentication control
app.layout = html.Div([
    dcc.Store(id="session", storage_type="session"),
    dcc.Location(id="url", refresh=False),
    html.Div(id="page-content")  # This will show either login or your app
])

# =============================================================================
# MAIN APP LAYOUT (your existing multi-page setup)
# =============================================================================

def create_authenticated_layout():
    """Your existing app layout - only shown when authenticated"""
    return html.Div([
        html.Div([
            html.Div(
                dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
            ) for page in dash.page_registry.values()
        ]),
        # Add logout button to your navigation
        html.Div([
            dbc.Button("Logout", id="logout-button", color="danger", size="sm", className="m-2")
        ]),
        dash.page_container
    ])

# =============================================================================
# AUTHENTICATION CALLBACKS
# =============================================================================

@callback(
    Output("page-content", "children"),
    Input("session", "data"),
    Input("url", "pathname")
)
def display_page(session_data, pathname):
    """Control what content is shown based on authentication status"""
    if session_data and session_data.get("authenticated"):
        return create_authenticated_layout()  # Show your multi-page app
    else:
        return create_login_form()  # Show login form


@callback(
    [Output("session", "data"),
     Output("login-output", "children")],
    Input("login-button", "n_clicks"),
    [State("username", "value"),
     State("password", "value")]
)
def handle_login(n_clicks, username, password):
    """Handle login attempts"""
    if not n_clicks:
        return dash.no_update, ""

    if not username or not password:
        return dash.no_update, dbc.Alert("Please fill all fields", color="warning")

    if verify_login(username, password):
        return {"authenticated": True, "username": username}, ""
    else:
        return dash.no_update, dbc.Alert("Invalid credentials", color="danger")


@callback(
    Output("session", "data", allow_duplicate=True),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """Handle logout"""
    if n_clicks:
        return {"authenticated": False}
    return dash.no_update


# =============================================================================
# RUN APP
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True)
