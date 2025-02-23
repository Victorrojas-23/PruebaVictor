# Victor Rojas
#script realizado en python
#prueba tecnica KEA
from faker import Faker
import json
import math
from geopy.distance import geodesic

fake = Faker()
Faker.seed(0)


taxpayers = []

for _ in range(1000):
    geolocation = fake.local_latlng(country_code="MX")
    taxpayer = {
        "id": fake.uuid4(),
        "name": fake.name(),
        "location": {
          "latitude":float(geolocation[0]),
          "longitude":float(geolocation[1])
        },
        "age" : fake.random_int(18, 90),
        "accepted_offers" : fake.random_int(0, 100),
        "canceled_offers" : fake.random_int(0, 100),
        "average_reply_time" : fake.random_int(1, 3600),
    }
    taxpayers.append(taxpayer)

# Writing to taxpayers.json
with open("taxpayers.json", "w") as outfile:
    outfile.write(json.dumps(taxpayers))
       

    
#funcion para calcular la distancia importanto geodesic
def calcularDistancia(latitud1, longitud1,latitud2, longitud2):
    punto1 = (latitud1, longitud1)
    punto2 = (latitud2, longitud2)
    return geodesic (punto1,punto2).km

#le damos un puntaje del 10% a todos los clientes que esten en el rango de 18 a 90 años
def puntajeE (cliente):
     if 18 <= cliente['age'] <=  90:
        puntajeEdad = 1
    
     else:
        puntajeEdad = 0

     return puntajeEdad

 #  se calcula la distancia con ayuda de la funcion calcularDistancia para darle un puntaje mayor a los clientes que se encuentren mas cerca

def demografico(cliente, oficinaLatitud, oficinaLongitud):
    distancia =  max(0, 1 / calcularDistancia(cliente['location']['latitude'], cliente['location']['longitude'], oficinaLatitud, oficinaLongitud)) * 10 * 0.1
    return round(distancia)

#aqui damos mas puntos de ponderacion a los clientes con mas ofertas aceptadas que canceladas
def ofertasAceptadas(cliente):
    
    if cliente['accepted_offers'] >= cliente['canceled_offers'] or cliente['canceled_offers'] == 0 or cliente['accepted_offers'] == 0:
        puntosAceptados = 3

    else:
        puntosAceptados = 1  
    return puntosAceptados 
#aqui damos puntos de ponderacion a los que tienen menos canceladas tomado como referencia el total de las ofertas 
def ofertasCanceladas(cliente):
    totalOfertas = cliente['accepted_offers'] + cliente['canceled_offers']
    if totalOfertas > 0:
        canceladas = cliente['canceled_offers'] /  totalOfertas
        if 0 <= canceladas <= 0.2:
            puntos = 3
        elif 0.3 <= canceladas <= 0.5 :
            puntos = 2 
        else:  
            puntos = 1

    else:
        puntos = 0   
    return puntos

# los clientes con el menor tiempo de respuesta se le brinda 20% de ponderacion y a los que tardan mas solo el 10%

def tiempoRespuesta(cliente):
    if 1 <= cliente['average_reply_time'] <= 1800:
        puntosT = 2
    else:
        puntosT = 1
    return puntosT

# en la siguiente funcion se suman todos los puntos obtenidos

def calculandoPuntos(cliente, oficinaLatitud, oficinaLongitud):
    puntosPorEdad= puntajeE (cliente)
    puntosPorDistancia = demografico(cliente, oficinaLatitud, oficinaLongitud)
    puntosOfertaAC =ofertasAceptadas(cliente)
    puntosOfertaCA = ofertasCanceladas(cliente)
    puntosPorTiempo =tiempoRespuesta(cliente)

    totalScore = puntosPorEdad + puntosPorDistancia + puntosOfertaAC + puntosOfertaCA + puntosPorTiempo
    return totalScore

#el puntaje obtenido es ingresado a un for para que nos brinde su score y sea ordenado en el lugar donde sea mas probale que acepte una oferta 

def probables(oficinaLatitud, oficinaLongitud,clientesData):

    for cliente in clientesData:
        cliente['score'] = calculandoPuntos(cliente, oficinaLatitud, oficinaLongitud)
    
    ordenDeClientes = sorted(clientesData,key=lambda x: x['score'], reverse = True)

    return ordenDeClientes[:10]

oficinaLatitud = 19.3797208
oficinaLongitud = -99.1940332

#lee los datos de taxpayers.json

with open("taxpayers.json", "r") as f:
    clientesData = json.load(f)

#llamamos a los clientes mas probables para que el siguiente for nos muestre el resultado donde recorre la lista de clientes

primerosClientes = probables(oficinaLatitud, oficinaLongitud,clientesData)

for cliente in primerosClientes :
    print(json.dumps(cliente, indent=4))