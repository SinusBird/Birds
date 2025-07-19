# =============================================================================
# SECURITY HELPER
# =============================================================================
import dash
from dash import dcc, html, Input, Output, State, callback

def require_auth(func):
    """Decorator für Callbacks - erfordert Authentifizierung"""

    def wrapper(*args, **kwargs):
        # Session-Data ist normalerweise der erste Input
        session_data = args[0] if args else None

        if not session_data or not session_data.get("authenticated"):
            return dash.no_update

        return func(*args, **kwargs)

    return wrapper