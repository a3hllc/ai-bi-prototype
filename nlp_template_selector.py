# 📁 nlp_template_selector.py
# Copyright A3H LLC
# This script classifies user phrases into Jinja2 template paths based on intent

def classify_template_intent(user_input: str) -> str:
    """
    Classifies input command into template name.
    Args:
        user_input (str): The user's phrase like "use dashboard layout"
    Returns:
        str: Path to the corresponding Jinja2 template file
    """
    user_input = user_input.lower()

    if "kpi" in user_input:
        return "templates/kpi_cards.rdl.j2"
    elif "bar chart" in user_input or "graph" in user_input:
        return "templates/bar_chart.rdl.j2"
    elif "dashboard" in user_input:
        return "templates/dashboard_layout.rdl.j2"
    elif "table" in user_input or "detailed list" in user_input:
        return "templates/tabular.rdl.j2"
    else:
        # Default fallback template
        return "templates/default_table.rdl.j2"
