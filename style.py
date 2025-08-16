# Reusable header components
import dash
from dash import html

# =============================================================================
# Define header style
# =============================================================================

# Basic style
BASE_HEADER_STYLE = {
    'textAlign': 'center',
    'color': '#2c3e50',
    'fontFamily': 'Leto, sans-serif',
    'marginBottom': '20px',
    'marginTop': '-80px'
}

# Specific per level
HEADER_STYLES = {
    'h1': {
        **BASE_HEADER_STYLE,
        'fontSize': '2rem',
        'fontWeight': 'bold',
        'borderBottom': '3px solid #5b3a29'
    },
    'h2': {
        **BASE_HEADER_STYLE,
        'fontSize': '1.5rem',
        'fontWeight': '600',
        'color': '#34495e'
    },
    'h3': {
        **BASE_HEADER_STYLE,
        'fontSize': '1rem',
        'fontWeight': '500',
        'color': '#5a6c7d'
    },
    'h4': {
        **BASE_HEADER_STYLE,
        'fontSize': '0.9rem',
        'fontWeight': '400',
        'color': '#7f8c8d'
    }
}


# =============================================================================
# Header functions
# =============================================================================

def create_header(text, level='h1', emoji=None, custom_style=None):
    """
    Erstellt eine formatierte Überschrift

    Args:
        text (str): Der Überschriftentext
        level (str): Überschrift-Level ('h1', 'h2', 'h3', 'h4')
        emoji (str): Optional - Emoji am Anfang
        custom_style (dict): Optional - zusätzliche Stil-Anpassungen

    Returns:
        html-Element: Die formatierte Überschrift
    """
    # Add Emoji
    display_text = f"{emoji} {text}" if emoji else text

    # Combine
    style = HEADER_STYLES.get(level, HEADER_STYLES['h1']).copy()
    if custom_style:
        style.update(custom_style)

    # Hand over html element
    header_map = {
        'h1': html.H1,
        'h2': html.H2,
        'h3': html.H3,
        'h4': html.H4
    }

    HeaderComponent = header_map.get(level, html.H1)
    return HeaderComponent(children=display_text, style=style)


# Convenience-Funktionen für häufig verwendete Überschriften
def main_title(text, emoji='🦉'):
    """Haupttitel der App"""
    return create_header(text, 'h1', emoji)


def section_title(text, emoji=None):
    """Sektion-Überschrift"""
    return create_header(text, 'h2', emoji)


def subsection_title(text, emoji=None):
    """Untersektion-Überschrift"""
    return create_header(text, 'h3', emoji)


def card_title(text, emoji=None):
    """Titel für Cards/Komponenten"""
    return create_header(text, 'h4', emoji)