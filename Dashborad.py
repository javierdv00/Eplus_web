import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
from dash.dash_table.Format import Format, Scheme

# Load the Excel sheet into a DataFrame
file_path = 'Resultados_Todos.xlsx'
df_model = pd.read_excel(file_path, sheet_name='BD_Modelo')

# Dictionary with the new column structure
columns = {
    "Normalizado_Consumo total [kWh]": ["Con,r", 1, [-0.1, 0, 0.02, 0.05, 0.1, 1]],
    "Normalizado_Carga Termica Total_anual [W]": ["CT,r", 1, [-0.1, 0, 0.04, 0.1, 0.2, 1]],
    "Entre 18 e 26_ocup": ["Top18-26", 1, [0, 0.4, 0.5, 0.6, 0.7, 1]],
    "sDA": ["sDA", 1, [0, 0.2, 0.4, 0.55, 0.75, 1]],
    "ASE": ["ASE", -1, [0, 0.07, 0.1, 0.2, 0.3, 1]]
}
size_column_ID = 20  # value in percentage

columns_for_chart = list(columns.keys())
renamed_columns = [columns[col][0] for col in columns_for_chart]

# Initialize the Dash app
app = Dash(__name__)

# Generate conditional styles based on thresholds
def generate_conditional_styles(df):
    styles = []
    for col, col_info in columns.items():
        colors = ["darkgreen", "lightgreen", "orange", "pink", "red"] if col_info[1] == -1 else ["red", "pink", "orange", "lightgreen", "darkgreen"]
        thresholds = col_info[2]
        for i in range(len(thresholds) - 1):
            styles.append({
                'if': {
                    'filter_query': f'{{{col}}} > {thresholds[i]} && {{{col}}} <= {thresholds[i+1]}',
                    'column_id': col
                },
                'backgroundColor': colors[i],
                'color': 'white'
            })
    return styles

# App Layout with left sidebar and main dashboard side-by-side
app.layout = html.Div([
    # Left Sidebar Section
    html.Div([
        html.H2("Information Section"),
        html.P("This section provides some background information and additional context for the dashboard."),
        html.Img(src='path_to_your_image.png', style={'width': '100%', 'padding-top': '20px'}),
    ], style={'width': '15%', 'padding': '20px', 'box-sizing': 'border-box'}),

    # Right Side (Existing Layout)
    html.Div([
        # Filters Row
        html.Div([
            html.Div([
                html.Label("Select Model:"),
                dcc.Dropdown(id='model-filter', options=[{'label': model, 'value': model} for model in df_model['ID Modelo'].unique()], multi=True, placeholder="Select Models")
            ], style={'width': '20%', 'display': 'inline-block', 'padding-right': '10px'}),

            html.Div([
                html.Label("Climatization:"),
                dcc.Checklist(id='climatizacao-filter', options=[{'label': climat, 'value': climat} for climat in df_model['Climatizacao'].unique()], labelStyle={'display': 'block'})
            ], style={'width': '20%', 'display': 'inline-block', 'padding-right': '10px'}),

            html.Div([
                html.Label("Glass Type:"),
                dcc.Checklist(id='vidro-filter', options=[{'label': vidro, 'value': vidro} for vidro in df_model['Vidro'].unique()], labelStyle={'display': 'block'})
            ], style={'width': '20%', 'display': 'inline-block', 'padding-right': '10px'}),

            html.Div([
                html.Label("Solar Protection:"),
                dcc.Checklist(id='solar-filter', options=[{'label': solar, 'value': solar} for solar in df_model['Protecao Solar - ID Modelo'].unique()], labelStyle={'display': 'block'})
            ], style={'width': '20%', 'display': 'inline-block'})
        ], style={'width': '100%', 'display': 'flex', 'justify-content': 'space-between', 'padding': '10px'}),

        # Line Chart
        html.Div([dcc.Graph(id='line-chart')], style={'position': 'relative','left': '15%','width': '95%', 'display': 'inline-block'}),

        # Color Filter Dropdowns Row
        html.Div([
            html.Div(
                html.Label("Seleciona a cor para filtrar:"),
                style={'width': f'{size_column_ID}%', 'display': 'inline-block', 'padding-right': '10px', 'textAlign': 'left'}
            ),
            *[
                html.Div([
                    html.Label(renamed_columns[i]),
                    dcc.Dropdown(
                        id=f'color-filter-{i}',
                        options=[
                            {'label': 'Verde escuro', 'value': 'darkgreen'},
                            {'label': 'Verde claro', 'value': 'lightgreen'},
                            {'label': 'Laranja', 'value': 'orange'},
                            {'label': 'Rosa', 'value': 'pink'},
                            {'label': 'Vermelho', 'value': 'red'}
                        ],
                        multi=True,
                        placeholder="Filtre pela cor"
                    )
                ], style={'width': f'{(100 - size_column_ID) / len(columns_for_chart)}%', 'textAlign': 'center', 'display': 'inline-block', 'padding-right': '10px'})
                for i in range(len(columns_for_chart))
            ]
        ], style={'width': '100%', 'display': 'flex', 'justify-content': 'space-between', 'padding': '10px'}),

        # Data Table
        html.Div([
            dash_table.DataTable(
                id='data-table',
                columns=[{'name': 'ID Modelo', 'id': 'ID Modelo'}] + [{'name': renamed_columns[i],
                    'id': columns_for_chart[i],
                    'type': 'numeric',
                    'format': Format(precision=2, scheme=Scheme.percentage)} for i in range(len(columns_for_chart))],
                
                # # Set the general cell style and width for all columns
                # style_cell={
                #     'textAlign': 'center',  # Center alignment for all cells by default
                #     'padding': '5px',
                #     'minWidth': '80px', 'maxWidth': '150px', 'width': 'auto'
                # },
                # Apply conditional styles for "ID Modelo" column width and alignment
                style_cell_conditional=[
                    {'if': {'column_id': 'ID Modelo'}, 'width': f'{size_column_ID}%', 'textAlign': 'left'},  # Right-align "ID Modelo"
                ] + [
                    {'if': {'column_id': col}, 'width': f'{(100 - size_column_ID) / len(columns_for_chart)}%', 'textAlign': 'center'} for col in columns_for_chart
                ],
                
                style_data_conditional=generate_conditional_styles(df_model),
                style_table={'height': '300px', 'overflowY': 'auto'}
            )
        ], style={'width': '101%', 'padding-top': '0px'})

    ], style={'width': '80%', 'display': 'inline-block', 'box-sizing': 'border-box'})
], style={'display': 'flex'})

# Callback to update charts and table based on filters
@app.callback(
    [Output('line-chart', 'figure'), Output('data-table', 'data')],
    [Input('model-filter', 'value'),
     Input('climatizacao-filter', 'value'),
     Input('vidro-filter', 'value'),
     Input('solar-filter', 'value')] +
    [Input(f'color-filter-{i}', 'value') for i in range(len(columns_for_chart))]  # Color filters as inputs
)
def update_dashboard(selected_models, selected_climatizacao, selected_vidro, selected_solar, *color_filters):
    filtered_df = df_model.copy()
    if selected_models:
        filtered_df = filtered_df[filtered_df['ID Modelo'].isin(selected_models)]
    if selected_climatizacao:
        filtered_df = filtered_df[filtered_df['Climatizacao'].isin(selected_climatizacao)]
    if selected_vidro:
        filtered_df = filtered_df[filtered_df['Vidro'].isin(selected_vidro)]
    if selected_solar:
        filtered_df = filtered_df[filtered_df['Protecao Solar - ID Modelo'].isin(selected_solar)]

    # Apply color filters
    for i, selected_colors in enumerate(color_filters):
        if selected_colors:
            col = columns_for_chart[i]
            thresholds = columns[col][2]
            colors = ["darkgreen", "lightgreen", "orange", "pink", "red"] if columns[col][1] == -1 else ["red", "pink", "orange", "lightgreen", "darkgreen"]

            color_mask = pd.Series(False, index=filtered_df.index)
            for j, color in enumerate(colors):
                if color in selected_colors:
                    color_mask |= (filtered_df[col] > thresholds[j]) & (filtered_df[col] <= thresholds[j+1])
            filtered_df = filtered_df[color_mask]

    # Create Line Chart
    fig = go.Figure()
    for _, row in filtered_df.iterrows():
        fig.add_trace(go.Scatter(
            x=renamed_columns,
            y=row[columns_for_chart],
            mode='lines',
            showlegend=False,
            #name=row['ID Modelo'],
        ))
    custom_legend = ["darkgreen", "lightgreen", "orange", "pink", "red"]
    for idx,color in enumerate(custom_legend):
        # fig.add_trace(go.Scatter(
        #     x=[None], y=[None],
        #     mode='markers',
        #     marker=dict(color=color, size=20),
        #     legendgroup="color",
        #     showlegend=True,
        #     name="Classe "+str(idx+1)#color.capitalize()
        # ))
        
        # Add colored rectangle
        fig.add_shape(
            type="rect",
            xref="paper", yref="paper",
            x0=1.01, x1=1.065,  # Width of the rectangle
            y0=1-idx*0.1, y1=1-idx*0.1 - 0.1,  # Height and spacing
            fillcolor=color,
            line=dict(width=0),
        )
        # Add text centered on the rectangle
        fig.add_annotation(
            x=1.06,  # Center text horizontally
            y=1-idx*0.1-0.01 if idx!=len(custom_legend)-1 else 1-idx*0.1 - 0.05, #- 0.025,  # Center text vertically
            xref="paper", yref="paper",
            text="Classe "+str(idx+1),#color.capitalize(),
            showarrow=False,
            font=dict(color="white", size=13),  # Text color and size
            align="center",
        )
    # Adjust layout to ensure custom legend is visible and properly positioned
    fig.update_layout(
        margin=dict(r=150),  # Add space for the custom legend on the right
    )
    # Add color-coded bars for thresholds, ending at the last threshold value
    for i, col in enumerate(columns_for_chart):
        thresholds = columns[col][2]
        colors = ["darkgreen", "lightgreen", "orange", "pink", "red"] if columns[col][1] == -1 else ["red", "pink", "orange", "lightgreen", "darkgreen"]
        for j in range(len(thresholds) - 1):
            start = thresholds[j]
            end = thresholds[j + 1]
            fig.add_trace(go.Bar(
                x=[renamed_columns[i]],
                y=[end - start],
                base=start,
                name=f"{renamed_columns[i]} Threshold",
                marker_color=colors[j],
                width=0.2,
                showlegend=False
            ))

    fig.update_layout(
        yaxis=dict(range=[-0.1, max([max(col[2]) for col in columns.values()])]),
        title='P-Balance',
        xaxis_title="Parameters",
        barmode='overlay'
    )

    table_data = filtered_df[['ID Modelo'] + list(columns_for_chart)].to_dict('records')
    return fig, table_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
