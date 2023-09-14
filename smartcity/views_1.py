from django.shortcuts import render
from django.core.paginator import Paginator
import json
from .smartcity_modules import *
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as p
from django_plotly_dash import DjangoDash

df, sensors, location_names, areas = display_table()

dataset_json, chart_ar_year_pass = chart_bar_pivot(df)
dataset = json.dumps(dataset_json)

# data = df.head(10).to_json(orient='records')

# Create your views here.

def index(request):
    return render(request, "smartcity/index.html", {
        "df_length":df.shape[0],
        "areas":areas,
        "sensors":sensors,
        "chart_ar_year_pass":chart_ar_year_pass, 
        "dataset":dataset
    })

def passengers_tbl(request, page=1):
    
    data = json.loads(df.to_json(orient='records'))
    
    paginator = Paginator(data, 10)  # Set the number of rows per page
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'smartcity/passengers_tbl.html', {
        'sensors': sensors,
        'location_names': location_names,
        'areas': areas,
        # 'data':data,
        'page_obj': page_obj,
        'page': page,
        'num_pages': 10
    })

def maps(request):
    
    maps = create_html_map(df)
    
    return render(request, 'smartcity/maps.html', {'maps': maps._repr_html_()})

# Add the following code

app = DjangoDash('anime_visuals')

# df=data[data['Date'] == datetime.date(x, y, z)].copy()

app.layout = html.Div([
    
    # Chart Title
    html.H4('Animated GDP and population over decades'),

    # Message
    html.P("Select an animation:"),

    # Creating a radio selector with options "Passers - Scatter" and "Passers - Bar"
    dcc.RadioItems(
        id='animations-x-selection',
        options=["Passers - Scatter", "Passers - Bar"],
        value='Passers - Scatter',
    ),

    # Creating  an axes system
    dcc.Loading(dcc.Graph(id="animations-x-graph"), type="cube")
],  style={'width': '100%'})


# app.css.append_css({'external_url': '/static/css/your_styles.css'})  # Add any custom CSS file you want to use

@app.callback(
    Output("animations-x-graph", "figure"), 
    Input("animations-x-selection", "value"))

def display_animated_graph(selection):
    df = px.data.gapminder() # replace with df=pd.read_csv("dataset_short.csv")
    animations = {
        'Passers - Scatter': px.scatter(
            df, x="gdpPercap", y="lifeExp", animation_frame="year", 
            animation_group="country", size="pop", color="continent", 
            hover_name="country", log_x=True, size_max=55, 
            range_x=[100,100000], range_y=[25,90]),
        'Passers - Bar': px.bar(
            df, x="continent", y="pop", color="continent", 
            animation_frame="year", animation_group="country", 
            range_y=[0,4000000000]),
        
    }
    
    return animations[selection]

def anime_visuals(request):
    return render(request, 'smartcity/anime_visuals.html', {
        'dash_app': app, 'container_id': 'container'
    })
