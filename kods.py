import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By

def kordinatas(address, city, api_key):#funkcija lai atrastu visu vietu kordinātas
    url = f"https://api.tomtom.com/search/2/geocode/{address},{city}.json?key={api_key}"
    response = requests.get(url)
    data = response.json()
   
    return (data["results"][0]["position"]["lat"], data["results"][0]["position"]["lon"])


def DUS_tuvuma(latitude, longitude, radiuss, api_key):#pēc ievadītās adreses kordinātām tiek atrastas tuvejas DUS
    url = f"https://api.tomtom.com/search/2/categorySearch/petrol station.json?key={api_key}&lat={latitude}&lon={longitude}&radius={radiuss*1000}"
    response = requests.get(url)
    data = response.json()

    return data["results"]


def attalums(start_lat, start_lon, end_lat, end_lon, api_key):#pēc kordinātām atrod attālumu starp A un B punktiem
    url = f'https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json?key={api_key}&traffic=true'
    response = requests.get(url)
    data = response.json()

    return data["routes"][0]["summary"]["lengthInMeters"] / 1000


def majaslapa(city):# noskraipo datus no mājas lapas
    driver = webdriver.Chrome()
    driver.get(f"https://gasprices.dna.lv/lv/?city={city}")

    return driver.find_elements(By.CLASS_NAME,('dusitem'))


def degvielas_cena(gas_station, fuel_type):
    prices = gas_station.text.replace('\n','EUR',2)# parveido pirmos divus uz EUR
    prices = prices.split('EUR')# sadala pa EUR
    spec = '\n'+fuel_type

    for i in range (1, len(prices)): # pārbauda DD, jo viņš vienigais ir bez \n
        if fuel_type =='DD':
            if fuel_type in prices[i]:
                return float(prices[i].replace(fuel_type + '\n',''))#noņem nost 
        elif spec in prices[i]:
            return float(prices[i].replace(fuel_type + '\n',''))      
        
    return None
         
def izmaksas(distance, fuel_consumption, fuel_price, fuel_amount):

    return (fuel_price*fuel_consumption*distance)/100+(fuel_price*fuel_amount)

def letaka_DUS(address, city, fuel_type, fuel_consumption, fuel_amount, radiuss, api_key):
    gas_price_data = majaslapa(city)
    coordinates = kordinatas(address,city, api_key)
    gas_stations = DUS_tuvuma(*coordinates, radiuss, api_key)
    printed_addresses = [] # new list to store printed addresses

    for gas_station in gas_stations:
        if gas_station['poi']['name'] not in ['Lukoil', 'Trest']:
            gas_station_address = gas_station['address']['freeformAddress']
            k = gas_station_address.find(",")
            gas_station_address = gas_station_address[:k]

            if gas_station_address not in printed_addresses: # check if address has already been printed
                printed_addresses.append(gas_station_address)
                gas_price = None
                for gas_price_element in gas_price_data:
                    if gas_station_address in gas_price_element.text:
                        gas_price = degvielas_cena(gas_price_element, fuel_type)
                        break

                if gas_price is not None:
                    distance = attalums(*coordinates, *kordinatas(gas_station_address,city,api_key), api_key)
                    fuel_cost = izmaksas(distance, fuel_consumption, gas_price, fuel_amount)
                    fuel_cost = round(fuel_cost,2) #izmaksas noapaļo lidz 2 cipariem aiz komata
                    atbilde = (str(gas_station_address)+' attālums līdz DUS '+str(distance)+' km un kopējās izmaksas būs '+str(fuel_cost)+' eiro ').encode()
                    atb = atbilde.decode()
                    print(atb)

api_key = 'jūsu api key'
city = input('Ievadi pilsētu: ')
address = input('Ievadi adresi: ')
fuel_consumption = float(input('ievadi mašīnas patēriņu (l/100km): '))
fuel_amount = float(input('ievadi uzpildes daudzumu (l): '))
fuel_type = input('ievadi degvielas veidu (DD/95/98/LPG): ')
radiuss = float(input('ievadi radiusu'))

letaka_DUS(address, city, fuel_type, fuel_consumption, fuel_amount,radiuss,api_key)
