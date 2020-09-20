import os.path, configparser, requests, json, datetime as dt, dateutil.parser as parser, dateutil.tz as tz


def readconfig():

    print("Reading configuration file to determine if values exist.")
    config = configparser.ConfigParser()
    config.read('appconfig.ini')
    print(config.sections())
    return config


def get_from_config(section, property_key):
    return configurer.get(section, property_key)


def get_ip_address_from_rest_call():
    response = requests.get(configurer.get('IP Address', 'ip_address_rest_url'))
    print('ip address from rest call: ' + response.text)
    return response.text


def get_lat_long_from_rest_call():
    lat_url = configurer.get('Lat And Long', 'lat_and_long_rest_url')
    print('Getting latitude and longitude from: ' + lat_url)
    response = requests.get(lat_url)
    lat = response.json()['lat']
    lon = response.json()['lon']
    print('fetched from URL --> lat: ' + lat + ', lon: ' + lon)
    return lat, lon


def get_sunrise_sunset_from_rest_call(lat, lon):
    sunrise_url = get_from_config('Dusk Till Dawn', 'sunrise_sunset_rest_url')
    url_params = {
        "lat": lat,
        "lng": lon,
        "date": "2020-09-19",
        "formatted": 0
    }
    print('url: ' + sunrise_url)
    for i in url_params:
        print(i, url_params[i])

    response = requests.get(sunrise_url, params=url_params)
    print(response.text)
    sunrise_time = response.json()['results']['sunrise']
    sundown_time = response.json()['results']['sunset']
    return sunrise_time, sundown_time


def update_config(section, key, value):
    configurer[section][key] = value
    with open('appconfig.ini', 'w') as configfile:    # save
        configurer.write(configfile)


def convert_date_from_utc(date_string):
    date_dt = parser.parse(date_string)
    local_tz = tz.tzlocal()
    local_dt = date_dt.replace(tzinfo=tz.gettz('UTC'))
    local_dt = local_dt.astimezone(local_tz)
    return local_dt.strftime("%H:%M:%S")


configurer = readconfig()
ip_address = get_from_config('IP Address', 'ip_address')
print("ip address from config file: " + ip_address)

if ip_address == '':
    print('ip address not set. Will retrieve and store')
    ip_address = get_ip_address_from_rest_call()
    update_config('IP Address', 'ip_address', ip_address)

latitude = get_from_config('Lat And Long', 'latitude')
longitude = get_from_config('Lat And Long', 'longitude')
print ('lat and long from config file: ' + latitude + ', ' + longitude)
if latitude == '' or longitude == '':
    print('hitting rest endpoint for latitude and longitude')
    latitude, longitude = get_lat_long_from_rest_call()
    update_config('Lat And Long', 'latitude', latitude)
    update_config('Lat And Long', 'longitude', longitude)

curr_date_str = get_from_config('Dusk Till Dawn', 'current_date')
curr_date_obj = dt.date.today()
is_date_blank = False
if curr_date_str == '':
    is_date_blank  = True
    curr_date_str = curr_date_obj.strftime("%Y-%m-%d")
    print('current date is not set. Updating config file with value: ' + curr_date_str)
    update_config('Dusk Till Dawn', 'current_date', curr_date_str)


config_date = parser.parse(curr_date_str).date()
is_date_correct = True
if is_date_blank is False and config_date < curr_date_obj:
    is_date_correct = False
    print('date in config file is not current. Updating config file to: ' + curr_date_obj.strftime("%Y-%m-%d"))
    update_config('Dusk Till Dawn', 'current_date', curr_date_obj.strftime("%Y-%m-%d"))

dawn_time = get_from_config('Dusk Till Dawn', 'dawn_time')
dusk_time = get_from_config('Dusk Till Dawn', 'dusk_time')

if is_date_correct is False or (dawn_time == '' or dusk_time == ''):
    print('Either we do not have the correct date or the dawn/dusk times are not set. Fetching from rest endpoint')
    dawn_time, dusk_time = get_sunrise_sunset_from_rest_call(latitude, longitude)
    update_config('Dusk Till Dawn', 'dawn_time', convert_date_from_utc(dawn_time))
    update_config('Dusk Till Dawn', 'dusk_time', convert_date_from_utc(dusk_time))


