from django.shortcuts import render
from django.http import JsonResponse
import plotly.graph_objs as go
import pandas as pd
import json

# Define column categories
columns_select = {
    "Model": "ID Modelo",
    "Filter": ["Climatizacao", "Vidro", "Protecao Solar"],
    "Parameters": {"Con,r":[True, [-0.1, 0, 0.02, 0.05, 0.1, 1]],
                   "CT,r":[True, [-0.1, 0, 0.04, 0.1, 0.2, 1]],
                   "Top18-26": [True, [0, 0.4, 0.5, 0.6, 0.7, 1]],
                   "sDA":[True, [0, 0.2, 0.4, 0.55, 0.75, 1]],
                   "ASE":[False, [0, 0.07, 0.1, 0.2, 0.3, 1]]}
}
color_classes = ["red", "pink", "orange", "lightgreen", "darkgreen"]

keys_list = list(columns_select["Parameters"].keys())
def generate_data():

    file_path = 'Resultados_Todos.xlsx'
    df_model = pd.read_excel(file_path, sheet_name='BD_Modelo')
    rename_dict = {"Protecao Solar - ID Modelo": "Protecao Solar",
                   "Normalizado_Consumo total [kWh]": "Con,r",
                   "Normalizado_Carga Termica Total_anual [W]": "CT,r",
                   "Entre 18 e 26_ocup": "Top18-26"}
    df = df_model.rename(columns=rename_dict)
    
    # Select only relevant columns
    selected_columns = [columns_select["Model"]] + columns_select["Filter"] + list(columns_select["Parameters"].keys())
    return df[selected_columns]

def get_filtered_data(request):
    """Filter and return data in JSON format for AJAX requests."""
    df = generate_data()

    # Extract filters from request
    selected_models = request.GET.getlist(columns_select["Model"]+'[]')  # Model filter
    selected_filters = {col: request.GET.getlist(col + '[]') for col in columns_select["Filter"]}

    # Apply Model Filter
    if selected_models:
        df = df[df[columns_select["Model"]].isin(selected_models)]

    # Apply Other Filters
    for col, values in selected_filters.items():
        if values:
            df = df[df[col].isin(values)]

    # Prepare Chart Data
    traces = []

    # Add background bars (color-coded regions for each parameter)
    for param, (direction, thresholds) in columns_select["Parameters"].items():
        colors = color_classes if direction else color_classes[::-1]
        
        for i in range(len(thresholds) - 1):
            traces.append(go.Bar(
                x=[param],  # Bar centered on the parameter
                y=[thresholds[i + 1] - thresholds[i]],  # Bar height
                base=thresholds[i],  # Start from the lower threshold
                width=0.3,  # Adjust this value to make bars thinner
                marker=dict(color=colors[i], opacity=0.9),
                name=f"{param} range {i + 1}",
                showlegend=False
            ))

    # Add line plot on top
    for _, row in df.iterrows():
        traces.append(go.Scatter(
            x=list(columns_select["Parameters"].keys()),  # X-axis: Parameter names
            y=[row[param] for param in list(columns_select["Parameters"].keys())],  # Y-axis: Data values
            mode='lines+markers',
            name=row[columns_select["Model"]]  # Model Name
        ))

    # Create figure
    fig = go.Figure(data=traces)

    # Legend position
    legend_x_start = 1  # Position outside the main graph area
    legend_y_start = 0.9
    legend_height = 0.1  # Height for each legend bar
    legend_spacing = 0.0  # Space between bars

    # Legend shapes and annotations
    shapes = []
    annotations = []

    class_names = ["Class 1", "Class 2", "Class 3", "Class 4", "Class 5"]

    for i, color in enumerate(color_classes):
        y0 = legend_y_start - i * (legend_height + legend_spacing)
        y1 = y0 - legend_height

        # Add legend bar
        shapes.append(dict(
            type="rect",
            xref="paper", yref="paper",
            x0=legend_x_start, x1=legend_x_start + 0.07,
            y0=y0, y1=y1,
            fillcolor=color,
            line=dict(width=0),
        ))

        # Add label inside the bar
        annotations.append(dict(
            x=legend_x_start + 0.035,
            y=(y0 + y1) / 2,
            xref="paper", yref="paper",
            text=class_names[i],
            showarrow=False,
            font=dict(color="white", size=14, family="Arial Bold", weight="bold"),# dict(color="white" if i > 2 else "black", size=12),
            xanchor="center",
            yanchor="middle"
        ))
    
    # Update layout with the legend
    fig.update_layout(
        title="PBalance",
        width=1280,
        xaxis_title="Parameters",
        template="plotly_white",
        showlegend=False,
        barmode="overlay",
        shapes=shapes,
        margin=dict(l=270, r=80),  # Increased right margin
        annotations=annotations
    )


    return JsonResponse({
        'chart': fig.to_json(),
        'table': df[[columns_select["Model"]] + list(columns_select["Parameters"].keys())].to_dict(orient="records"),
        'columns': list(columns_select["Parameters"].keys())  # Send columns for table update
    })

def dashboard_view(request):
    df = generate_data()

    return render(request, 'p_balance/dashboard.html', {
        'filters': json.dumps({col: sorted(df[col].unique()) for col in columns_select["Filter"]}),
        'models': sorted(df[columns_select["Model"]].unique()),
        'models_name': columns_select["Model"],
        'columns_select': json.dumps(columns_select),
        'color_classes': json.dumps(color_classes)
    })
