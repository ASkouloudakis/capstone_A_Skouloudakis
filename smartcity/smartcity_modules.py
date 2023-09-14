import pandas as pd
import geopandas as gpd
import numpy as np
import folium
import pyproj
import os
import plotly.express as px
import json
from folium.plugins import MarkerCluster
from folium.plugins import StripePattern
import ast
from shapely.geometry import Point
from shapely import wkt
from shapely.ops import transform
from shapely.wkt import loads

# ----------------------------------------------------- Get Datasets -----------------------------------------------------
def get_polygons():
    # Συνδυάζει τον κατάλογο του τρέχοντος σεναρίου με το όνομα αρχείου 'gebieden-wijken.csv' για να δημιουργήσει 
    # μια πλήρη διαδρομή προς αυτό το αρχείο, από οπουδήποτε στο σύστημα αρχείων
    file_path = os.path.join(os.path.dirname(__file__), 'datasets/gebieden-wijken.csv')

    # Μετατροπή του αρχείου CSV σε ένα pandas DataFrame με το όνομα 'polygons'.
    polygons = pd.read_csv(file_path)
    return polygons

def get_roads(file_name):
    
    file_path = os.path.join(os.path.dirname(__file__), 'datasets/'+ file_name)

    # Μετατροπή του αρχείου CSV σε ένα pandas DataFrame με το όνομα 'road_edges'.
    road_edges = pd.read_csv(file_path)
    
    return road_edges

def get_horeca_data(file_name):
    
    file_path = os.path.join(os.path.dirname(__file__), 'datasets/'+ file_name)

    # Μετατροπή του αρχείου CSV σε ένα pandas DataFrame με το όνομα 'horeca_position'.
    horeca_position = pd.read_csv(file_path)
    
    return horeca_position

def get_areas_crowd_sens():
    
    file_path = os.path.join(os.path.dirname(__file__), 'datasets/areas_crowd_sens_df.csv')

    # Μετατροπή του αρχείου CSV σε ένα pandas DataFrame με το όνομα 'areas_crowd_sens'.
    areas_crowd_sens = pd.read_csv(file_path)

    return areas_crowd_sens

def get_areas_polygons_of_amsterdam():

    file_path = os.path.join(os.path.dirname(__file__), 'datasets/areas_polygons_of_amsterdam.csv')

    # Μετατροπή του αρχείου CSV σε ένα pandas DataFrame με το όνομα 'areas_polygons_of_amsterdam'.
    areas_polygons_of_amsterdam = pd.read_csv(file_path)

    return areas_polygons_of_amsterdam

def read_csv_file():
    
    # Ορισμός των τύπων των στηλών του dataframe
    dtypes = {
        'Sensor': str,
        'Periode': str,
        'Naamlocatie': str,
        'Datumuur': str,
        'Aantalpassanten': int,
        'Gebied': str,
        'Geometrie': str,
        'Year':int,
        'Month':int,
        'Date':int,
        'Hour':int
    }

    # Μετατροπή του αρχείου CSV σε ένα pandas DataFrame με το όνομα 'areas_polygons_of_amsterdam'.
    df = pd.read_csv('smartcity/datasets/dataset.csv', dtype=dtypes)
    
    # Μετονομασία των στηλών του dataframe df
    df.columns=['id','Sensor', 'Period', 'LocationName', 'DateHour', 'Passers', 'Area', 'Geometry', 'Year', 'Month', 'Date','Hour']
    return df

# ----------------------------------------------------- Create Displays -----------------------------------------------------
def display_table():

    # Διαβάζεται το csv αρχείο dataset και αποδίδεται στο dataframe df.
    df = read_csv_file()

    # Φιλτράρισμα του df για όλες της τιμές της στήλης 'Period' όταν είναι ίση με 'uur'.
    df = df[df['Period'] == 'uur']

    # Δημιουργία λίστών με μοναδικές τιμές για τις στήλες sensors, location_names και areas.
    sensors = df['Sensor'].unique().tolist()
    location_names = df['LocationName'].unique().tolist()
    areas = df['Area'].unique().tolist()
    
    # Επιστροφή του φιλτραρισμένου df και των λιστών sensors, location_names και areas.
    return df, sensors, location_names, areas

def filter_dataframe(df, area, location_name, sensor):
    filtered_df = df
    if area != 'all':
        filtered_df = df[df['Area'] == area]
    if location_name != 'all':
        filtered_df = df[df['LocationName'] == location_name]
    if sensor != 'all':
        filtered_df = df[df['Sensor'] == sensor]
    
    print(f"{sensor} {location_name} {area}")

    return filtered_df

def chart_bar_pivot(df): #  

    ################## Δημιουργία Pivot dataframe για το το ChartBar ##################
    # Επιλογή στηλών από το dataframe που εισάγεται ως όρισμα και δημιουργία του dataframe 'chart_ar_year_pass'.  
    chart_ar_year_pass = df[['DateHour', 'Passers', 'Area']].copy()

    # Αντικατάσταση των τιμών της στήλης 'DateHour' με το έτος της εκάστοτε ημερομηνίας.
    chart_ar_year_pass['DateHour'] = pd.to_datetime(chart_ar_year_pass['DateHour']).dt.year

    # Groups chart_ar_year_pass data by 'Area' and 'DateHour', υπολογισμόςη μερήσιου μέσου όρου ανά έτος 
    # σε κάθε περιοχή και δημιουργία του dataframe grouped.
    grouped = chart_ar_year_pass.groupby(['Area', 'DateHour'], as_index=False).mean()

    # Δημιουργία Pivot table με ευρετήριο τη στήλη 'Area'
    pivot = grouped.pivot(index='Area', columns='DateHour', values='Passers')

    # Επαναφορά του ευρετηρίου και μετατροπή του ευρετηρίου 'Area' σε στήλη
    pivot.reset_index(inplace=True)

    # Συμπλήρωση των τιμών που λείπουν με 0
    pivot.fillna(0, inplace=True)

    # Μετατροπή των τιμών της στήλης 'Passers' σε ακεραίους
    pivot[pivot.columns[1:]] = pivot.iloc[:, 1:].astype(int)

    #################### End of create the dataframe Pivot ####################

    # Create datasets for chartBar
    dataset_graph_json = []

    # Επιλογή των χρωμάτων για τις μπάρες του γραφήματος 
    rgb = ['63, 57, 247', '247, 57, 57', '255, 99, 132', '255, 159, 64',  '255, 205, 86', '75, 192, 192', '54, 162, 235', '153, 102, 255',  '201, 203, 207', '101, 247, 57']
    
    index = 0
    for i, row in pivot.iterrows():
        # Δημιουργία χρώματος φόντου σε μορφή RGBA χρησιμοποιώντας την τιμή RGB από τη λίστα 'rgb' με αδιαφάνεια 0,2.
        rgba_bgc = 'rgba('+ rgb[index] + ', 0.2)'

        # Δημιουργία χρώματος περιγράμματος σε μορφή RGBA χρησιμοποιώντας την τιμή RGB από τη λίστα 'rgb' με πλήρη αδιαφάνεια.
        rgba_border = 'rgba('+ rgb[index] + ', 1)'

        # Ανάκτηση της περιοχής της τρέχουσας σειράς. 
        area = row['Area']

        # Ανάκτηση των τιμών δεδομένων από τη δεύτερη στήλη και μετά, για τη τρέχουσα σειρά.
        data = list(row.iloc[1:])

        # Ορισμός backgroundColor borderColor και borderWidth των στοιχείων του γραφήματος για τη τρέχουσα σειρά.
        backgroundColor = rgba_bgc
        borderColor = rgba_border
        borderWidth = 1
        dataset_graph_json.append({'label': area, 'data': data, 'backgroundColor': backgroundColor, 'borderColor': borderColor, 'borderWidth': borderWidth})

        index += 1
    return dataset_graph_json, chart_ar_year_pass # Επιστροφή του γραφήματος και του dataframe 'chart_ar_year_pass'

def point_to_lonlat(point):
    # Εξαγωγή των συντεταγμένων από τη συμβολοσειρά 'point'
    x, y = point.split("POINT (")[1].split(")")[0].split()
    x = float(x)
    y = float(y)

    # Ορισμός συστημάτων αναφοράς συντεταγμένων
    # Σύστημα αναφοράς συντεταγμένων - Πηγή 
    source = pyproj.CRS.from_string("+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725 +units=m +no_defs")
    # Σύστημα αναφοράς συντεταγμένων - Στόχος
    target = pyproj.CRS.from_string("EPSG:4326")

    # Δημιουργία μετατροπέα χρησιμοποιώντας το καθορισμένο CRS
    transformer = pyproj.Transformer.from_crs(source, target, always_xy=True)

    # Μετατροπή των συντεταγμένων
    lon, lat = transformer.transform(x, y)

    # Επιστροφή γεωγραφικού μήκους and γεωγραφικού πλάτους
    return lon, lat

# **************************************************************************88

def create_interactive_mobility_map(data):
    # Δημιουργία χάρτη
    amsterdam_map = folium.Map(location=[52.379189, 4.899431], zoom_start=12, width='96%', height=550)

    # Διατρέχεται το Datafrane που έχει εισαχθεί ως όρισμα
    for _, row in data.iterrows():

        # Ανάκτηση των συντεταγμένων της στήλης 'geometrie_epsg_4326', στην τρέχουσα γραμμή 
        lat_lng_coords_str = row['geometrie_epsg_4326']

        # Μετατροπή των συντεταγμένων της στήλης 'lat_lng_coords_str' σε μια λίστα, στην τρέχουσα γραμμή.
        lat_lng_coords = ast.literal_eval(lat_lng_coords_str)

        # Δημιουργείται ένα αντικείμενο PolyLine και προστίθεται στο χάρτη
        folium.PolyLine(locations=lat_lng_coords, color='blue').add_to(amsterdam_map)

    # Επιστρέφεται ο χάρτης
    return amsterdam_map 

def create_sensors_map(data): # Δημιουργία χάρτη αισθητήρων

    coord = []
    coord_WGS_84 = []

    data['Sensor_Geometry'] = data['Sensor'] + ";" + data['LocationName'] + ";" + data['Geometry']

    Sensor_Geometry = data['Sensor_Geometry'].drop_duplicates()

    for row in Sensor_Geometry:
        # Split rows
        result = row.split("POINT")
        sensor = result[0].split(";")[0]
        locationName = result[0].split(";")[1]

        result = result[1][2:-1]

        result = result.split(" ")
        # Temporary tuple is created with system coordinates SRID=28992
        coord.append((sensor, locationName, result[0], result[1]))

    for coordinates in coord:
        x3 = float(coordinates[2])
        x4 = float(coordinates[3])

        point = Point(x3, x4)
        point_gpd = gpd.GeoSeries([point], crs='epsg:28992')

        # Reproject the point to WGS 84
        point_gpd = point_gpd.to_crs(epsg=4326)

        coord_WGS_84.append((coordinates[0], coordinates[1], point_gpd.y[0], point_gpd.x[0]))

    data = pd.DataFrame(coord_WGS_84)
    data.columns = ['Sensor', 'LocationName', 'Latitude', 'Longitude']

    lat = data['Latitude']
    lon = data['Longitude']
    sensor = data['Sensor']
    locationName = data['LocationName']

    sensors_map = folium.Map(location=[lat.mean(), lon.mean()], zoom_start=12)

    # Define a list of colors for markers
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'pink', 'gray', 'yellow', 'black', 'brown']
 
    for _, row in data.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        sensor = row['Sensor']
        locationName = row['LocationName']
        
        # Get the color for the marker based on its index
        color = colors[_ % len(colors)]
        
        # Create the marker with the specified color
        marker = folium.Marker(location=[lat, lon], popup=f"<b>{locationName}</b> - sensor: {sensor}", icon=folium.Icon(color=color))
        
        # Add the marker to the map
        marker.add_to(sensors_map)

    return sensors_map

def create_horeca_map(data): # Δημιουργία χάρτη HORECA  

    # data = data[data['Zaakcategorie']=='Restaurant']
    categories = data['Zaakcategorie'].unique()

    # Centered the map
    map = folium.Map(location=[52.373338, 4.891206], zoom_start=12, width='97%', height=550)

    # Creating an instance of MarkerCluster() and adding to map  
    # marker_cluster = MarkerCluster().add_to(map)

    # colors = ['blue']
 
    for category in categories:
    
        if category == "Café":
            show=True
        else:
            show=False
        # Create a feature group for the current category
        feature_group = folium.FeatureGroup(name=category, show=show)

        # Create marker cluster and add it to the feature group
        marker_cluster = MarkerCluster().add_to(feature_group)

        # Filter the data for the current category
        filtered_data = data[data['Zaakcategorie'] == category]

        for _, row in filtered_data.iterrows():
            if row['Lat'] and row['Lon']:
                lat = row['Lat']
                lon = row['Lon']
                categorie = row['Zaakcategorie']
                brand_name = row['Zaaknaam']
                adress = row['Adres']

                # Create the marker with the specified color
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=f"<div style='width: 200px;'> <b> Categorie:</b> {categorie}</br> <b>Brand:</b> {brand_name}</br> <b>Adress:</b> {adress}<b></br> Lat:</b> {lat} <b></br> Lon:</b> {lon} </div>",
                    icon=folium.Icon(color='blue'),
                ).add_to(marker_cluster)

        # Add the feature group to the map
        feature_group.add_to(map)

    folium.LayerControl(collapsed=False).add_to(map)
    
    return map

def bubble_plot(df, year, x, y, size, color, hover_name, default_option):
    
    fig = px.scatter(df.query(year), x=x, y=y,
	         size=size, color=color,
                 hover_name=hover_name, log_x=True, size_max=50, facet_col="Year")

    for trace in fig.data:
        if default_option not in trace.name:
            trace.visible = 'legendonly'
    
    return fig

def areas_passers_map (df, df1):
    # Η συνάρτηση δέχεται ως όρισματα δύο DataFrames
    # Αντιγράφονται γεωμετρίες του Dataframe df1 στο df
    df['Geometrie'] = df1['Geometrie'].values

    # Αντικαθιστούμε τις περιοχές με πλήθος = 0 με NaN
    df['Aantalpassanten'] = df['Aantalpassanten'].replace(0, np.nan)

    # Υλοποιείται συνάρτηση η οποία εξάγει τις WKT συντεταγμένες και τις μετατρέπουμε σε γεωμετρία Shapely
    def convert_geometry(value):
        wkt_str = value.split(";")[1]
        geometry = loads(wkt_str)
        return geometry

    #  Εφαρμόζουμε τη συνάρτηση convert_geometry() στη στήλη 'Geometrie'
    df['Geometrie'] = df['Geometrie'].apply(convert_geometry)

    # Μετατρέπουμε το DataFrame σε ένα GeoDataFrame
    geoJSON_df1 = gpd.GeoDataFrame(df, geometry='Geometrie')

    # Ορίζουμε το παρόν σύστημα συντεταγμένων και το προβάλουμε στο EPSG:4326
    geoJSON_df1.crs = "EPSG:28992"
    geoJSON_df1 = geoJSON_df1.to_crs("EPSG:4326")

    # Ορίζουμε νέο χάρτη 
    map = folium.Map(location=[52.370017472433854, 4.8925988104555245], zoom_start=11, width='96%', height=550)

    # Ορίζουμε τίτλο για το χάρτη
    title_html = '''
             <h3 align="center" style="font-size:20px"><b>Μέτρηση Πλήθους ανά Περιοχή</b></h3>
             '''
    # Προσθέτουμε το τίτλο στο χάρτη
    map.get_root().html.add_child(folium.Element(title_html))

    # Ορίζουμε ένα χάρτη Choropleth
    choropleth = folium.Choropleth(
        geo_data=geoJSON_df1, # Ορίζουμε την πηγή των δεδομένων μορφής GeoJSON για το χάρτη choropleth.
        data=geoJSON_df1, # Ταιριάζουμε τα δεδομένα με geoDataFrame
        # Ορίζουμε ποιες στήλες θα χρησιμοποιηθούν: 'Identificatie' ως αναγνωριστικό για κάθε περιοχή 
        # και 'Aantalpassanten' για την τιμή δεδομένων που θα απεικονιστεί.
        columns=['Identificatie', "Aantalpassanten"], 
        key_on="feature.properties.Identificatie", # Ορισμός Κλειδιού για την αντιστοίχιση με το 'Identificatie' στα δεδομένα για σύνδεση του GeoJSON με τιμές δεδομένων.
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Μέτρηση Πλήθους",
        smooth_factor=0, # Μειώνεται ο αριθμός των μικρών ατελειών στα περιγράμματα, το 0 σημαίνει χωρίς εξομάλυνση.
        Highlight=True, # # Επισημάινονται οι περιοχές όταν τοποθετούνται το δείκτη του ποντικιού πάνω τους.
        line_color="#0000",
        name="Aantalpassanten",
        show=False, # Ορίζεται ότι το layer δεν πρέπει να είναι ορατό κατά τη φόρτωση του χάρτη.
        overlay=True, # Ορίζεται ότι το layer επικαλύπτει την βάση του χάρτη
        nan_fill_color="lightgrey"
    ).add_to(map)

    # Προσθέτουμε στο χάρτη λειτουργία hover.
    style_function = lambda x: {'fillColor': '#ffffff', 
                                'color':'#000000', 
                                'fillOpacity': 0.1, 
                                'weight': 0.1}
    highlight_function = lambda x: {'fillColor': '#000000', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.50, 
                                    'weight': 0.1}
    NIL = folium.features.GeoJson(
        data = geoJSON_df1,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Name', 'Aantalpassanten'],
            aliases=['Area', 'Passers'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    )
    map.add_child(NIL)
    map.keep_in_front(NIL)

    # Προστίθεται cross-hatching (διασταύρωση γραμμών) για να εμφανίστούν οι τιμές NaN.
    nans = geoJSON_df1[geoJSON_df1["Aantalpassanten"].isnull()]['Identificatie'].values
    gdf_nans = geoJSON_df1[geoJSON_df1['Identificatie'].isin(nans)]
    sp = StripePattern(angle=45, color='grey', space_color='white')
    sp.add_to(map)

    folium.features.GeoJson(name="Click για Περιοχές χωρίς Πλήθος",data=gdf_nans, style_function=lambda x :{'fillPattern': sp}, show=False).add_to(map)

    # Προσθέτουμε dark και light mode. 
    folium.TileLayer('cartodbdark_matter',name="dark mode",control=True, show=True).add_to(map)
    folium.TileLayer('cartodbpositron',name="light mode",control=True).add_to(map)

    # Προσθέτουμε ένα layer controller. 
    folium.LayerControl(collapsed=False).add_to(map)

    return map

def create_areas_pass_per_week(data):
    
    # Φιλτραρισμα του Dataframe στη βάση του data['Period']=='week'.
    df=data[data['Period']=='week']

    # Ορίζεται η στήλη 'DateHour' σε τύπι datetime
    df['DateHour'] = pd.to_datetime(df['DateHour'])

    # Δημιουργείται στήλη με το όνομα 'Week_Number' στην οποία θα περιλαμβάνονται οι αριθμοί
    # των εβδομάδων με βάση την ημερομηνίας στη στήλη DateHour του DataFrame
    df['Week_Number'] = df['DateHour'].dt.isocalendar().week

    # Δημιουργείται το DataFrame 'sensor_df dataframe' με συγκεκριμένες στήλες
    sensor_df = df[['Area', 'Passers', 'Week_Number', 'Year']].copy()
    
    # Μετατροπή του DataFrame σε μορφότυπο JSON
    json_data = sensor_df.to_json(orient='records')

    # Δημιουργείται διαδραστικό γράφημα χρησιμοποιώντας τη βιβλιοθήκη Vega-Lite για τη μέτρηση του πλήθους ανά περιοχή και εβδομάδα
    vega_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "width": 900.0, "height": 400,
        "data": {
            "values": json.loads(json_data)  # Φορτώνεται τ σύνολο δεδομένων
        },
        "mark": "bar", # Ορίζεται ο τύπος του γραφήματος από μία σειρά γραφημάτων π.χ. area, bar, line, circle κλπ
        "params": [{
            "name": "industry", 
            "select": {"type": "point", "fields": ["Area"]},
            "bind": "legend"
        }],
        "encoding": {
            "x": {
                "field": "Week_Number",  # Ορίζεται η στήλη του DataFrame στον άξονα x
                "type": "ordinal",  # Ορίζεται ο τύπος για διακριτές τιμές
                "axis": {
                    "title": "Εβδομάδα",  # Ορίζεται ο τίτλος
                    "labelAngle": 0, #  Περιστρέφονται οι ετικέτες του άξονα σε -45 μοίρες
                    "labelSeparation": 20,  # Ορίζεται ο διαχωρισμός μεταξύ των τιμών του άξονα x
                    "values": list(range(1, 53, 5))  # Εμφανίζεται ο αριθμός για κάθε 5η εβδομάδα
            }
            },
            "y": {
                "aggregate": "sum", "field": "Passers",  #Ορίζεται η στήλη του DataFrame στον άξονα y και ο τρόπος διαχείρισης σε 'sum'
                "axis": {
                    "title": "Άθροισμα Πλήθους"  # Ορίζεται ο τίτλος
            }
            },
            "color": {
                "field": "Area", # Ορίζεται το πεδίο βάσης για τον προσδιορισμό του χρώματος των σημείων δεδομένων.
                "scale": {"scheme": "goldred"} # Εφαρμόζεται ο συνδυασμός χρωμάτων "category20b"
            },
            "opacity": {
                "condition": {"param": "industry", "value": 1}, # Για τις επιλεγμένες περιοχές η αδιαφάνεια είναι 1 
                "value": 0.2 # Για τις μη επιλεγμένες περιοχές η αδιαφάνεια είναι 0.2 
            }
        }
    }

    # Convert the Vega-Lite specification to a JSON string and return it
    return json.dumps(vega_spec)

def passers_on_today_year(df):
    # Ανακτάται το τρέχον έτος
    year = df['Year'].max()

    # Φιλτράρεται το Dataframe στις γραμμές του τρέχοντος έτους. 
    data2023 = df[df['Year']==year]

    # Δημιουργείται Dataframe στις γραμμές που ισχύει data2023['Period']=='uur'
    dt = data2023[data2023['Period']=='uur']
    
    # Δημιουργείται Dataframe με τα σύνολα της μέτρησης πλήθους για κάθε περιοχή
    grouped_df = dt.groupby(['Area'])['Passers'].sum().reset_index()

    # Δημιουργείται Dataframe στις γραμμές που ισχύει data2023['Period']=='dag'
    passers_per_day = data2023[data2023['Period']=='dag']
    
    # Υπολογίζονται τα Q1 και Q3 για κάθε Περιοχή (Area)
    Q1 = passers_per_day.groupby('Area')['Passers'].transform(lambda x: x.quantile(0.25))
    Q3 = passers_per_day.groupby('Area')['Passers'].transform(lambda x: x.quantile(0.75))
    IQR = Q3 - Q1

    # Ορίζονται τα όρια
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Φιλτράρονται οι τιμές πέραν των ακραίων
    filtered_df = passers_per_day[(passers_per_day['Passers'] >= lower_bound) & (passers_per_day['Passers'] <= upper_bound)]

    # Επιστρέφεται το τρέχον έτος, το DataFrame των συνόλων και το DataFrame των ημερήσιων μετρήσεων.
    return year, grouped_df.to_json(orient="records"), filtered_df.to_json(orient="records")

