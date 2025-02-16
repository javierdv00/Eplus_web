from django.shortcuts import render
from django.http import JsonResponse
import plotly.graph_objs as go
import pandas as pd
import numpy as np
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
    df = generate_data()  # Load full dataset
    #print("Request GET:", request.GET)
    selected_filters = request.GET.dict()  # .dict() converts QueryDict to a normal dict
    
    ## 1. Extract Model Filters
    selected_models = request.GET.getlist(columns_select["Model"] + '[]')
    if selected_models:
        df = df[df[columns_select["Model"]].isin(selected_models)]

    ## 2. Extract Checkbox Filters
    selected_filters = {col: request.GET.getlist(col + '[]') for col in columns_select["Filter"]}
    for col, values in selected_filters.items():
        if values:
            df = df[df[col].isin(values)]

    selected_color_filtered = {col: request.GET.getlist(col + '[]') for col in columns_select["Parameters"]}
    print(selected_color_filtered)
    ## 3. Extract and Apply Color Filters
    for col, values in selected_color_filtered.items():
        if values:
            limits = []
            for value in values:
                if columns_select["Parameters"][col][0]: # if True take the position of the color from red to darkgreen
                    pos = color_classes.index(value)
                else:                                    # if False take the position of the color from darkgreen to red
                    pos = color_classes[::-1].index(value)
                if pos == 0:
                    # include the lower value also in the range. reducing 0.0001 of this value
                    limit = [columns_select["Parameters"][col][1][pos]-0.0001,columns_select["Parameters"][col][1][pos+1]]
                    limits.append(limit)
                else:
                    limit = [columns_select["Parameters"][col][1][pos],columns_select["Parameters"][col][1][pos+1]]
                    limits.append(limit)
            if limits:
                # include the higher number but not the lower (for position 0, was reduce 0.0001 to the value to include the lowest value)
                mask = np.logical_or.reduce([(df[col] > low) & (df[col] <= high) for low, high in limits])
                df = df[mask]
    
    ## 4. Prepare Chart Data (No change here)
    traces = []
    for param, (direction, thresholds) in columns_select["Parameters"].items():
        colors = color_classes if direction else color_classes[::-1]

        for i in range(len(thresholds) - 1):
            traces.append(go.Bar(
                x=[param],
                y=[thresholds[i + 1] - thresholds[i]],
                base=thresholds[i],
                width=0.3,
                marker=dict(color=colors[i], opacity=0.9),
                name=f"{param} range {i + 1}",
                showlegend=False
            ))

    for _, row in df.iterrows():
        traces.append(go.Scatter(
            x=list(columns_select["Parameters"].keys()),
            y=[row[param] for param in columns_select["Parameters"].keys()],
            mode='lines+markers',
            name=row[columns_select["Model"]]
        ))

    ## 5. Update Legend
    legend_x_start = 1  
    legend_y_start = 0.9
    legend_height = 0.1  
    legend_spacing = 0.0  

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
            font=dict(color="white", size=14, family="Arial Bold", weight="bold"),
            xanchor="center",
            yanchor="middle"
        ))

    ## 6. Update Plotly Layout
    fig = go.Figure(data=traces)
    fig.update_layout(
        title="PBalance",
        width=1280,
        xaxis_title="Parameters",
        template="plotly_white",
        showlegend=False,
        barmode="overlay",
        shapes=shapes,
        margin=dict(l=270, r=80),
        annotations=annotations
    )

    return JsonResponse({
        'chart': fig.to_json(),
        'table': df[[columns_select["Model"]] + list(columns_select["Parameters"].keys())].to_dict(orient="records"),
        'columns': list(columns_select["Parameters"].keys())
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

def get_color_for_value(parameter, value):
    """
    Determines the color for a given parameter value based on predefined thresholds.
    """
    param_data = columns_select["Parameters"].get(parameter)
    if not param_data:
        return "white"  # Default if parameter not found

    direction, thresholds = param_data  # Extract direction and threshold values

    # Choose color order based on direction
    colors = color_classes if direction else color_classes[::-1]

    for i in range(len(thresholds) - 1):
        if thresholds[i] <= value <= thresholds[i + 1]:
            return colors[i]  # Return corresponding color

    return "white"  # Default color if no match
