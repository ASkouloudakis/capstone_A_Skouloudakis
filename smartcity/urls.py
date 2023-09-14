from django.urls import path
from . import views

# For each URL, add to the urlpatterns list the path function with two or three arguments: 
# A string with the URL path, a function from views.py that we wish to call when that URL is visited, 
# and (optionally) a name for that path, in the format name="something". 
app_name = 'smartcity'  # Define the app namespace

urlpatterns = [
    path("", views.index, name="index"),
    path('overview/', views.overview, name='overview'),
    path('plot2/', views.plot2, name='plot2'),
    path('passengers_tbl/', views.passengers_tbl, name='passengers_tbl'),
    path('passengers_tbl/<int:page>/', views.passengers_tbl, name='passengers_tbl'),
    path('maps/', views.maps, name='maps'),
    path('maps1/', views.maps1, name='maps1'),
    path('plot1/', views.plot1, name='plot1'),
    path('map_areas_passers/', views.map_areas_passers, name='map_areas_passers'),
    path('anime_visuals/', views.anime_visuals, name='anime_visuals'),
    # path('smartcity/dash_anime_visuals/', views.anime_visuals, name='dash_anime_visuals'),
    
]
