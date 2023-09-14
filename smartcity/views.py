from django.shortcuts import render
from django.core.paginator import Paginator
import json
from django_plotly_dash import DjangoDash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from .smartcity_modules import *

# Κλήση της συνάρτησης display_table() η οποία επιστρέφει φιλτραρισμένο daraframe 
# και τις λίστες sensors, location_names και areas
df, sensors, location_names, areas = display_table()

# Κλήση της συνάρτησηςchart_bar_pivot() με όρισμα το DataFrame df του συνόλου δεδομένων dataset.csv
# και επιστροφή του συνόλου δεδομένων και του γραφήματος οπτικοποιώντας με Chart.js
dataset_json, chart_ar_year_pass = chart_bar_pivot(df)

# Μετατροπή του 'dataset_json' σε συμβολοσειρά JSON.
dataset = json.dumps(dataset_json)

# ----------------------------------------------------- First page -----------------------------------------------------
def index(request):

    # Κλήση της συνάρτησης create_sensors_map() με όρισμα το DataFrame df του συνόλου δεδομένων dataset.csv
    # και επιστροφή του χάρτη που περίεχει τα σημεία εγκατάστασης των αισθητήρων
    sensors_map = create_sensors_map(df)

    # Κλήση της συνάρτησηςpassers_on_today_year() με όρρισμα τη συνάρτηση read_csv_file() που επιστρέφει 
    # το DataFrame df του συνόλου δεδομένων dataset.csv
    # και επιστροφή του τρέχοντος έτους και των DataFrame σε μορφή JSON για την οπτικοποίηση με D3.js
    year, data, passers_per_day = passers_on_today_year(read_csv_file())

    return render(request, "smartcity/index.html", {
        'sensors_map': sensors_map._repr_html_(),
        "df_length":df.shape[0],
        "areas":areas,
        "location_names":location_names,
        "sensors":sensors,
        "chart_ar_year_pass":chart_ar_year_pass, 
        "dataset":dataset,
        "data":data,
        "passers_per_day": passers_per_day,
        "year":year
    })

# ----------------------------------------------------- Create tables -----------------------------------------------------
def passengers_tbl(request, page=1):
    # Αρχικοποιούνται οι προεπιλεγμένες τιμές των μεταβλητών που χρησιμοποιούνται στα φίλτρα
    area, location_name, sensor = 'all', 'all', 'all'  
    
    # Ανάκτηση της φόρμας φίλτρων
    if request.method == 'POST':
        area = request.POST.get('area')
        location_name = request.POST.get('location_name')
        sensor = request.POST.get('sensor')
        
        # Φιλτράρισμα του dataframe με βάση τις τιμές που έχουν ανακτηθεί
        df_filter = filter_dataframe(df, area, location_name, sensor)

        # Μετατροπή του dataframe df_filter σε τύπο json
        request.session['filtered_data'] = df_filter.to_json(orient='records')

        filtered = True  # Ορίζεται σε True η τιμή της σημαίας για αφιλτράριστα δεδομένα
    # Δεν έχει υποβληθεί φόρμα
    else:
        # Eλέγχεται εάν το κλειδί 'filtered_data' υπάρχει στο λεξικό request.session.
        if 'filtered_data' in request.session:
            # Μετατροπή του dataframe σε τύπο json
            df_filter = pd.read_json(request.session['filtered_data'])

            filtered = True  # H τιμή της σημαίας γίνεται True για αφιλτράριστα δεδομένα
        else:
            filtered = False  # H τιμή της σημαίας γίνεται False για φιλτραρισμένα δεδομένα
            
            df_filter = filter_dataframe(df, area, location_name, sensor)
        sensor, location_name, area='all', 'all', 'all'
    
    # Μετατροπή του dataframe df_filter σε τύπο json
    data = json.loads(df_filter.to_json(orient='records'))
    
    paginator = Paginator(data, 10)  # Ορίζεται ο αριθμός των γραμμών/σελίδα που εμφανίζεται στο πίνακα
    
    if filtered:
        # Εάν τα δεδομένα έχουν φιλτραριστεί, ανάκτησε τον αριθμό της σελίδας από το request
        page_number = request.GET.get('page')
    else:
        # Εάν τα δεδομένα δεν έχουν φιλτραριστεί, χρησιμοποιήσε ως αριθμό σελίδας την προεπιλογή
        page_number = page

    # Aνακτάται η σελίδα page_number tvn σελιδοποιημένων δεδομένων. 
    # Με τη κλάση Paginator χωρίζεται μια λίστα αντικειμένων σε πολλές σελίδες. Κάθε σελίδα περιέχει καθορισμένο αριθμό αντικειμένων, 10.
    page_obj = paginator.get_page(page_number)
    
    # Φόρτωση του template 'smartcity/passengers_tbl.html' με τις παραμέτρους που θα χρησιμοποιηθούν
    return render(request, 'smartcity/passengers_tbl.html', {
        'sensors': sensors,
        'location_names': location_names,
        'areas': areas,
        'selected_sensor':sensor,
        'selected_location_name': location_name,
        'selected_area':area,
        'page_obj': page_obj,
        'page': page,
        'num_pages': 10
    })

# ----------------------------------------------------- Create Visualizations -----------------------------------------------------
def maps(request): # Ενότητα HORECA

    # Δημιουργία διαδρομής στο σύνολο δεδομένων 'horeca_data.csv'
    horeca_file_name = request.GET.get('horeca_file', 'horeca_data.csv')

    # Κλήση της συνάρτησης create_horeca_map() με όρισμα της συνάρτηση get_horeca_data(horeca_file_name)
    # η οποία δημιουργεί το αναγκαίο σύνολο δεδομένων και επιστροφή του χάρτη HORECA
    horeca_map = create_horeca_map(get_horeca_data(horeca_file_name))
   
    # Φόρτωση του template 'smartcity/maps.html' με παραμέτρ το χάρτη horeca_map
    return render(request, 'smartcity/maps.html', {'horeca_map': horeca_map._repr_html_()})  

def maps1(request): # Ενότητα προσβάσιμου δικτύου 

    # Δημιουργία διαδρομής στο σύνολο δεδομένων 'osm_platform.csv'
    mobility_file_name = request.GET.get('mobility_file', 'osm_platform.csv')

    # Κλήση της συνάρτησης create_create_interactive_mobility_map() με όρισμα της συνάρτηση get_roads(mobility_file_name)
    # η οποία δημιουργεί το αναγκαίο σύνολο δεδομένων και επιστροφή του χάρτη mobility_map
    mobility_map = create_interactive_mobility_map(get_roads(mobility_file_name))
    
    # Φόρτωση του template 'smartcity/maps1.html' με παραμέτρ το χάρτη mobility_map
    return render(request, 'smartcity/maps1.html', {'mobility_map': mobility_map._repr_html_()}) 

def plot1(request):

    year = request.GET.get('year', '2021')  
    year_filter = f'Year=={year}'

    # Ανάκτηση του απαραίτητου συνόλου δεδομένων (dataset.csv)
    data = read_csv_file()

    # Φιλτράρισμα σύμφωνα με τη συνθήκη ['Period']=='week'
    data_week = data[data['Period']=='week']

    # Έλεγχος για αστοχία στην ανάκτηση του έτους
    try:
        year_int = int(year)
    except ValueError:
        year_int = 2023

    # Δημιουργία λίστας με τις περιοχές που καταγράφεται κίνηση πλήθους στο επιλεγχθέν έτος
    area = list(data_week[data_week['Year']==year_int]['Area'].unique())
    
    # Κλήση της συνάρτησης bubble_plot() με τα απαραίτητα ορίσματα για τη δημιουργιά του γραφήματος
    # 'Μέτρηση πλήθους ανά έτος και περιοχή'
    fig2 = bubble_plot(data_week, year_filter, "Passers", "Date", "Month", "Area", "LocationName", area[0])

    # Φόρτωση του template 'smartcity/plot1.html' με παραμέτρ το γράφημα τύπου bubble fig2
    return render(request, 'smartcity/plot1.html', {'plot1': fig2._repr_html_()}) 

def map_areas_passers(request):

    # Δημιουργία του χάρτη 
    map = areas_passers_map (get_areas_crowd_sens(), get_areas_polygons_of_amsterdam())

    # Φόρτωση του template 'smartcity/map_areas_passers.html' με παράμετρο την 'map'
    return render(request, 'smartcity/map_areas_passers.html', {'map': map._repr_html_()})

def plot2(request):

    # Κλήση της συνάρτησης create_areas_pass_per_week() με όρισμα το σύνολο δεδομένων dataset.csv 
    # για τη δημιουργία του γραφήματος με τη βιβλιοθήκη vega-lite 
    vega_json = create_areas_pass_per_week(read_csv_file())

    # Φόρτωση του template 'smartcity/plot2.html' με παράμετρο την 'vega_json'
    return render(request, 'smartcity/plot2.html', {'vega_json': vega_json})

def overview(request):
     
     # Φόρτωση του template 'smartcity/overview.html'.
     return render(request, 'smartcity/overview.html')

# ----------------------------------------------------- Create Animations -----------------------------------------------------
app = DjangoDash('anime_visuals')

def create_df_for_animate(filename):
    dtypes = {
            'id': str,
            'Sensor': str,
            'Periode': str,
            'Naamlocatie': str,
            'Datumuur': str,
            'Aantalpassanten': int,
            'Gebied': str,
            'Geometrie': str,
            'Year': int,
            'Month': int,
            'Date': int,
            'Hour': int
        }

    # Read csv
    file_path = os.path.join(os.path.dirname(__file__), 'datasets/'+ filename)
    data = pd.read_csv(file_path, dtype=dtypes)

    # Μετονομασία στηλών
    data.columns=['id','Sensor', 'Period', 'LocationName', 'DateHour', 'Passers', 'Area', 'Geometry', 'Year', 'Month', 'Date', 'Hour']

    # Δημιουργείται DataFrame με τις γραμμές που ισχύει data.Period=='uur' 
    data_uur=data[data.Period=='uur'].copy()

    # Δημιουργείται DataFrame με τις γραμμές που ισχύει ata.Period=='week' 
    data_week=data[data.Period=='week'].copy()

    # Διαγράφονται τα διπλοτυπα με βάση το υποσύνολο ['LocationName', 'Area', 'Geometry']
    df_deduplicated = data_uur.drop_duplicates(subset=['LocationName', 'Area', 'Geometry'])

    # Δημιουργείται το Dataframe 'merged_df', με συγχώνευση, εκτελώντας μια αριστερή ένωση μεταξύ
    # των Dataframeσ data_week και df_deduplicated, χρησιμοποιώντας τη στήλη "LocationName"
    # ως κλειδί συγχώνευσης.
    merged_df = pd.merge(data_week, df_deduplicated, on='LocationName', how='left')

    # Συμπληρώνουμε τις NaN τιμές στη στήλη 'Area_x' του DataFrame merged_df χρησιμοποιώντας τη μέθοδο fillna()od 
    merged_df['Area_x'] = merged_df['Area_x'].fillna(merged_df['Area_y'])

    # Συμπληρώνουμε τις NaN τιμές στη στήλη 'Geometry_x' του DataFrame merged_df 
    merged_df['Geometry_x'] = merged_df['Geometry_x'].fillna(merged_df['Geometry_y'])

    # Διαγράφουμε τις τιμές που δε θα χρησιμοποιηθούν από το DataFrame merged_df
    merged_df = merged_df.drop(['id_y', 'Sensor_y', 'Period_y', 'DateHour_y', 'Passers_y', 'Area_y', 'Geometry_y', 'Year_y', 'Month_y', 'Date_y', 'Hour_y'], axis=1)

    # Μετονομάζουμε τις στήλες του DataFrame merged_df
    merged_df.columns=['id','Sensor', 'Period', 'LocationName', 'DateHour', 'Passers', 'Area', 'Geometry', 'Year', 'Month', 'Date','Hour']

    # Προσθέτουμε στο τελικό DataFrame τη στήλη με το όνομα Week που περιέχει τον αριθμό της εβδομάδας της στήλης 'DateHour'
    merged_df['Week'] = pd.to_datetime(merged_df['DateHour']).dt.isocalendar().week

    return merged_df

app.layout = html.Div([
    
    html.Div([
        
        # Μηνύματα προς το χρήστη
        html.Div(
            "Select an animation (Move your mouse over from a parallelogram / circle to see more informations. Disable one or more sensors. Use the menu buttons to the right of the diagram for more interaction.",
            style={"color": "red", "font-size": "10px", "normal": "bold", "height": "20px"}),
        # Δημιουργία επιλογέα τύπoυ radio με τις επιλογές "Passers - Scatter" και "Passers - Bar"
        dcc.RadioItems(
            id='animations-x-selection',
            options=["Passers - Scatter", "Passers - Bar"],
            value='Passers - Scatter',
        )
        ]),

    # Δημιουργία συστήματος αξόνων
    dcc.Loading(dcc.Graph(id="animations-x-graph"), type="cube"),
])

@app.callback(
    Output("animations-x-graph", "figure"), 
    Input("animations-x-selection", "value"))

def display_animated_graph(selection):
    # Επεξεργασία του συνόλου δεδομένων 'dataset.csv' 
    df_anime = create_df_for_animate('dataset.csv') 
    df_anime = df_anime.sort_values('Week')  # Ταξινόμηση του ΔataΦrame  κατά τη στήλη "Year".

    # Δημιουργία animations
    animations = {
        'Passers - Scatter': px.scatter(
            df_anime, x="Year", y="Area", animation_frame="Week", 
            animation_group="LocationName", size="Passers", color="Sensor", 
            hover_name="LocationName", log_x=True, size_max=55),
        'Passers - Bar': px.bar(
            df_anime, x="Area", y="Passers", color="LocationName",
            animation_frame="Week", animation_group="Sensor", 
            range_y=[0,500000]),
        
    }
    
    animation = animations[selection]
    
    animation.update_layout(
        width=1500,  # Ορισμός του πλάτους του γραφήματος
        height=500,  # Ορισμός του ύψους του γραφήματος
        # Ορισμός των Play και Pause buttons
        updatemenus=[
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 1000}, "fromcurrent": True}]
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}]
                    }
                ] 
            }
        ]
    )
    
    return animation

def anime_visuals(request):
    
    # Φόρτωση του template 'smartcity/anime_visuals.html' με παράμετρο την 'dash_app'
    return render(request, 'smartcity/anime_visuals.html', {'dash_app': app})