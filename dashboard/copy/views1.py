from django.shortcuts import render
from django.http import JsonResponse
import plotly.graph_objs as go
import json

def generate_data():
    """Generate the dataset for models."""
    data = {
        'id_model': ['model 1', 'model 2', 'model 3', 'model 4', 'model 5', 'model 6', 'model 7', 'model 8', 'model 9', 'model 10'],
        'climatization': ['HVAC', 'VN', 'HVAC_dia', 'HVAC', 'VN', 'HVAC_dia', 'HVAC', 'VN', 'HVAC_dia', 'HVAC'],
        'Glass_type': ['V25', 'V25', 'V25', 'V29', 'V29', 'V29', 'V35', 'V35', 'V35', 'V35'],
        'Shading': ['No', 'No', 'No', 'ST3', 'No', 'ST3', 'ST3', 'ST6', 'No', 'ST6'],
        'Cons': [125, 34, 187, 134, 36, 194, 145, 42, 201, 265],
        'Conf_t': [100, 67, 100, 100, 61, 100, 100, 52, 100, 100],
        'Conf_v': [76, 76, 76, 98, 76, 98, 98, 98, 76, 100],
        'Temp_radiante': [30, 35, 34, 29, 34, 33, 31, 31, 30, 34],
    }
    return data

def get_filtered_data(request):
    """Filter and return data in JSON format for AJAX requests."""
    data = generate_data()

    # Get selected filters
    selected_models = request.GET.getlist('id_model[]') or []
    selected_climatization = request.GET.getlist('climatization[]') or []
    selected_glass_type = request.GET.getlist('Glass_type[]') or []
    selected_shading = request.GET.getlist('Shading[]') or []

    # Apply filters
    index_filter = list(range(len(data['id_model'])))

    if selected_models:
        index_filter = [i for i in index_filter if data['id_model'][i] in selected_models]
    if selected_climatization:
        index_filter = [i for i in index_filter if data['climatization'][i] in selected_climatization]
    if selected_glass_type:
        index_filter = [i for i in index_filter if data['Glass_type'][i] in selected_glass_type]
    if selected_shading:
        index_filter = [i for i in index_filter if data['Shading'][i] in selected_shading]

    # Filtered Data
    filtered_data = {key: [data[key][i] for i in index_filter] for key in data}

    # Prepare data for Plotly
    categories = ['Cons', 'Conf_t', 'Conf_v']  # X-axis labels
    traces = []

    for i, model in enumerate(filtered_data['id_model']):
        traces.append(go.Scatter(
            x=categories,
            y=[filtered_data['Cons'][i], filtered_data['Conf_t'][i], filtered_data['Conf_v'][i]],
            mode='lines+markers',
            name=model
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        title="Model Comparison",
        xaxis_title="Metrics",
        yaxis_title="Values",
        template="plotly_white"
    )

    # Prepare table data
    table_data = []
    for i in range(len(filtered_data['id_model'])):
        row = {
            'id_model': filtered_data['id_model'][i],
            'Cons': filtered_data['Cons'][i],
            'Conf_t': filtered_data['Conf_t'][i],
            'Conf_v': filtered_data['Conf_v'][i]
        }
        table_data.append(row)

    response_data = {
        'chart': fig.to_json(),  # Chart data
        'table': table_data  # Table data
    }

    return JsonResponse(response_data)

def dashboard_view(request):
    data = generate_data()
    
    return render(request, 'dashboard/dashboard.html', {
        'unique_models': sorted(set(data['id_model'])),
        'unique_climatizations': sorted(set(data['climatization'])),
        'unique_glass_types': sorted(set(data['Glass_type'])),
        'unique_shadings': sorted(set(data['Shading'])),
    })
