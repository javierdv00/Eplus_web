import plotly.graph_objects as go
from dash import dcc, html
from django_plotly_dash import DjangoDash
import logging

# Create the Dash app
chart_app = DjangoDash('chart_section')

# Log app creation to confirm it's working
logging.basicConfig(level=logging.DEBUG)
logging.debug("Dash app created")

# Create a simple figure
fig = go.Figure(data=[go.Scatter(x=[1, 2, 3, 4, 5], y=[10, 15, 7, 20, 12], mode='lines+markers')])
fig.update_layout(title="Test Chart", xaxis_title="X Axis", yaxis_title="Y Axis", template="plotly_white")

# Define Layout
chart_app.layout = html.Div([
    dcc.Graph(figure=fig, style={'height': '100vh', 'width': '100%'})
])
