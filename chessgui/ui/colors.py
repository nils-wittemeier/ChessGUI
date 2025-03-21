"""Define color theme for ChessGUI"""

_COLORS = {
    "board": {
        "background": {
            "none": {"light": "#E3E1CE", "dark": "#88684E"},
            "selected": {"light": "#F1CA1E", "dark": "#F1CA1E"},
            "moved": {"light": "#F5E07F", "dark": "#C8A60E"},
            "selector": "#FFFFFF",
        },
        "foreground": {"light": "#88684E", "dark": "#E3E1CE"},
        "dot": {"light": "#9b9a8dff", "dark": "#5d4735ff"},
    },
    "evalbar": {"light": "#FFFFFF", "dark": "#272932"},
    "pieces": {"light": "#FFFFFF", "dark": "#272932"},
}
