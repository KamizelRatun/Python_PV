import requests
import json


def pvapiansparser(inputstring):
    inputstring=inputstring.split("WS10m,Int",2)
    inputstring=inputstring[1]
    inputstring=inputstring.split("G(i):",2)
    inputstring=inputstring[0]
    lines= inputstring.splitlines()
    del inputstring
    json_data = []
    i=0
    for line in lines:
        parts = line.split(',')
        if line:
            timearray=parts[0].split(":")
            date=timearray[0]
            yr=int(date[0:4])
            mnth=int(date[4:6])
            da=int(date[6:8])
            hour=int(timearray[1][0:2])
            json_data.append({
            #'no': i,
            'timestamp': parts[0],
            'irradiance': parts[1],
            'temperature': parts[3],
            'year': yr,
            'month': mnth,
            'day':da,
            'hour':hour


            })
            i=i+1
    del lines
    return json_data


def sarah2(startyear,endyear,panel_slope,latitude,longitude,panel_azimuth,name):
    # URL API
    url = "https://re.jrc.ec.europa.eu/api/seriescalc"

    #Validation check of input arguments
    errorFlag = False
    if startyear > 2023 or startyear < 2005:
        print("Błąd zapytania SARAH2: Nieprawidłowy rok.")
        errorFlag = True
    if startyear > endyear:
        print("Błąd zapytania SARAH2: Rok początkowy musi być młodszy niż końcowy.")
        errorFlag = True
    if panel_slope < 0 or panel_slope >90:
        print("Błąd zapytania SARAH2: Kąt nachylenia panelu musi się znajdować w zakresie od 0 do 90 stopni.")
        errorFlag = True
    if panel_azimuth < -180 or panel_azimuth >180:
        print("Błąd zapytania SARAH2: Azymut panelu musi się znajdować w zakresie od -180 do 180 stopni.")
        errorFlag = True
    if latitude < -90 or latitude > 90:
        print("Błąd zapytania SARAH2: Nieprawidłowa szerokość geograficzna.")
        errorFlag = True
    if longitude < -90 or longitude > 90:
        print("Błąd zapytania SARAH2: Nieprawidłowa długość geograficzna.")
        errorFlag = True
    if errorFlag:
        return 0

    #Adding input parameters to request dictionary "params"
    params = {"usehorizon": 1}
    params["lat"] = latitude
    params["lon"] = longitude
    params["startyear"] = startyear
    params["endyear"] = endyear
    params["aspect"] = panel_azimuth
    params["angle"] = panel_slope

    # sending the request
    response = requests.get(url, params=params)

    #Checking the validity of the answer
    if "time,G(i),H_sun,T2m,WS10m,Int" in response.text:
        "SARAH2: zapytanie poprawne, odpowiedź otrzymana"
    else:
        print("Błąd zapytania SARAH2: nieprawidłowa odpowiedź")
        print(response.text)
        return 0
    #print(pvapiansparser(response.text))

   # file_path = name+"_"+str(startyear)+"_"+str(endyear)+"_ps_"+str(panel_slope)+"_panelaz_"+str(panel_azimuth)+".json"
    file_path = name +".json"

    # Zapisanie danych do pliku JSON
    with open(file_path, 'w') as json_file:
        json.dump(pvapiansparser(response.text), json_file, indent=4)
