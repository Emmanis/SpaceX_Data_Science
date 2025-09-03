import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# -------- Data --------
# Make sure spacex_launch_dash.csv is in the same folder
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Compute slider bounds
min_payload = int(spacex_df['Payload Mass (kg)'].min())
max_payload = int(spacex_df['Payload Mass (kg)'].max())

# Build dropdown options dynamically from the data
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
]

# -------- Dash App --------
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}
    ),

    # === TASK 1: Launch Site Drop-down ===
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',  # default = all sites
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # === TASK 2: Pie chart (success counts) ===
    dcc.Graph(id='success-pie-chart'),

    html.Br(),

    html.P("Payload range (Kg):"),

    # === TASK 3: Range Slider ===
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={
            0: '0',
            2500: '2.5k',
            5000: '5k',
            7500: '7.5k',
            10000: '10k'
        }
    ),

    html.Br(),

    # === TASK 4: Scatter chart (payload vs class, colored by booster) ===
    dcc.Graph(id='success-payload-scatter-chart')
])

# === TASK 2: Callback for pie chart ===
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Sum of successes (class=1) per site
        df_all = spacex_df.groupby('Launch Site', as_index=False)['class'].sum()
        fig = px.pie(
            df_all,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Filter for the selected site and show success vs failure counts
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = df_site['class'].value_counts().rename_axis('Outcome').reset_index(name='Count')
        # Map 1->Success, 0->Failure for nicer labels
        outcome_counts['Outcome'] = outcome_counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            outcome_counts,
            values='Count',
            names='Outcome',
            title=f'Launch Outcomes for {selected_site}'
        )
    return fig

# === TASK 4: Callback for scatter chart ===
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=('Payload vs. Outcome for All Sites'
               if selected_site == 'ALL'
               else f'Payload vs. Outcome for {selected_site}'),
        hover_data=['Launch Site']
    )
    return fig

# -------- Run --------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)