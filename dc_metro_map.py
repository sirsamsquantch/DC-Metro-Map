from google.transit import gtfs_realtime_pb2
import folium
from folium.plugins import MarkerCluster
import requests
import math
import time

key = [API Key]
baseURL = "https://api.wmata.com"
trainPosURL = "/gtfs/rail-gtfsrt-vehiclepositions.pb"
busPosURL = "/gtfs/bus-gtfsrt-vehiclepositions.pb"
stationListURL = "/Rail.svc/json/jStations"

m = folium.Map(zoom_start=11, location=[38.89636148264804, -77.03569725275094])

def plotVehicles(vehicleType, apiEndpoint, key, baseUrl):
  vehicles = {}
  marker_cluster = MarkerCluster().add_to(m)

  feed = gtfs_realtime_pb2.FeedMessage()
  response = requests.get(f"{baseURL}{apiEndpoint}?api_key={key}")
  feed.ParseFromString(response.content)

  for entity in feed.entity:
    # print(entity)
    vehicleID=entity.id
    position = {}
    position['lat'] = entity.vehicle.position.latitude
    position['long'] = entity.vehicle.position.longitude

    if vehicleType == 'train':      
      if entity.vehicle.current_status == 2:
        current_status = "in transit to"
      elif entity.vehicle.current_status == 1:
        current_status = "stopped"

      vehicles[vehicleID] = {
        'vehicleID':entity.id,
        'route_id':entity.vehicle.trip.route_id,
        'position':position,
        'current_status':current_status
      }
    elif vehicleType == 'bus':
      vehicles[vehicleID] = {
      'vehicleID':entity.id,
      'speed':str(int(entity.vehicle.position.speed * 2.23694))+' mph',
      'route_id':entity.vehicle.trip.route_id,
      'position':position
    }

  for vehicle in vehicles:
    if vehicleType == 'train':
      popup = f"Train {vehicles[vehicle]['vehicleID']} on {vehicles[vehicle]['route_id']} is {vehicles[vehicle]['current_status']}"

      colors = {
        'GREEN':'darkgreen',
        'BLUE':'blue',
        'ORANGE':'orange',
        'SILVER':'lightgray',
        'RED':'red',
        'YELLOW':'lightgreen',
        'NR':'black'
      }

      color = colors[vehicles[vehicle]['route_id']]

      folium.Marker(
        location = [vehicles[vehicle]['position']['lat'],vehicles[vehicle]['position']['long']],
        popup = popup,
        icon = folium.Icon(icon="train",color=color)
      ).add_to(marker_cluster)    
    
    elif vehicleType == 'bus':
      # print(vehicles[vehicle])
      icon_image = ("bus.png")
      popup = f"Bus {vehicles[vehicle]['vehicleID']} is traveling {vehicles[vehicle]['speed']}"
      folium.Marker(
          location = [vehicles[vehicle]['position']['lat'],vehicles[vehicle]['position']['long']],
          icon = folium.CustomIcon(icon_image, icon_size=(50, 50)),
          popup = popup    
        ).add_to(marker_cluster)  

def plotStations(apiEndpoint, key, baseUrl):
  
  marker_cluster = MarkerCluster().add_to(m)

  response = requests.get(f"{baseURL}{apiEndpoint}?api_key={key}")
  stations = response.json()['Stations']

  icon_image = ("train-station.png")

  for station in stations:
    popup = f"{station['Name']} station. Code: {station['Code']}"
    # print(station)
    folium.Marker(
        location = [station['Lat'],station['Lon']],
        icon = folium.CustomIcon(icon_image, icon_size=(50, 50)),
        popup = popup    
      ).add_to(marker_cluster)

plotStations(stationListURL, key, baseURL)

plotVehicles('train', trainPosURL, key, baseURL)
plotVehicles('bus', busPosURL, key, baseURL)
m.save('dc_metro.html')
# print('map updated')
