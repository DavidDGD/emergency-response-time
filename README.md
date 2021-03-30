![Dashboard](https://user-images.githubusercontent.com/51342082/113048770-303e0600-91a3-11eb-9324-4b74935b2c0d.png)

# Dashboard
<table>
<tr>
<td>
  A Dashboard using Quandl API to display history of stock growth in a given period of time. It helps predict the growth of stocks from the  charts of stock performace in any period of time. It helps to judge stocks, with the principle of momentum investing, which returns 1% per month on average.
</td>
</tr>
</table>


## Web Application
The web application can be found on:  https://dsp-response-time-dashboard.herokuapp.com/ (currently not live)

### The Project Aims:
- determine to what extent properties can be prioritized for fire inspection on the basis of the intervention time
- intervention time is defined as the time between the ignition of a fire and the start of fire suppression, modelled as the aggregate of several components
- each property is assigned to the fire station of their respective fire station district
- a street network specialized for fire trucks on OpenStreetMap (OSM) is used
- other used datasources are: i.a. Register for Topography, the KMNI API, the TomTom API
- using OSMnx and NetworkX for the street network and the intervention time
- properties with critical intervention times are marked red on the map in the dashboard
