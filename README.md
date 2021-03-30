![Dashboard](https://user-images.githubusercontent.com/51342082/113048770-303e0600-91a3-11eb-9324-4b74935b2c0d.png)

# Dashboard
<table>
<tr>
<td>
  A web application using property data to calculate the time fire emergency services need before the suppression of a fire can start. The calculated 'Intervention 
  Times' are visualized in a dashboard, which in turn can be used for prioritizing fire safety inspections in the municipality of Amsterdam.
</td>
</tr>
</table>


## Web Application
The web application can be found on:  https://dsp-response-time-dashboard.herokuapp.com/ (currently offline)

### The Project Aims:
- determine to what extent properties can be prioritized for fire inspection on the basis of the intervention time
- intervention time is defined as the time between the ignition of a fire and the start of fire suppression, modelled as the aggregate of several components
- each property is assigned to the fire station of their respective fire station district
- a street network specialized for fire trucks on OpenStreetMap (OSM) is used
- other used datasources are: i.a. Register for Topography, the KMNI API, the TomTom API
- using OSMnx and NetworkX for the street network and the intervention time
- properties with critical intervention times are marked red on the map in the dashboard
