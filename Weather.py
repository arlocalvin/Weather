import json
import smtplib
import pandas as pd
import time as tm
import requests



char_to_replace = {"'": "",
                   "[": "",
                   "]": ""}

def gmail_conn(email, password):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(email, password)

    return server



def txt(server, email, nmbr, msg):
    server.sendmail(email, nmbr, str(msg).translate(str.maketrans(char_to_replace)))



#Loop through all 7 days (14 entries, one for each day & night)
def weather(nmbr):
    a = []

    msg = ['Min Snow', 'Max Snow', 'Day', 'Temp']
    txt(server, email,nmbr,msg)
    tm.sleep(5)
    for i in range(14):
        q = "\""
        d = "f"
        tm.sleep(5)
        #Access contextual data
        day = brighton['properties']['periods'][i]['name']
        temp = brighton['properties']['periods'][i]['temperature']
        #Access the entire forecast to harvest snow data
        forecast = brighton['properties']['periods'][i]['detailedForecast']
        #Append if temp is over 32
        if temp > 32 and "New snow accumulation" not in forecast:
            #a.append([0.00,0.00,day,temp,short])
            msg = [0.00,0.00,day,temp]
            a.append(msg)
            txt(server, email, nmbr, msg)
        #Narrow down detailed forecast to relevant snow data
        if "New snow accumulation" in forecast:
            snow_data = "New snow accumulation of "
            #Snow data location in detailed forecast & raw snow accumulation extract
            snow_data_location = forecast[forecast.find(snow_data) + len(snow_data):]
            raw_snow_data = [int(i) for i in snow_data_location.split() if i.isdigit()]+[day]+[temp]
            #Harvest raw snowpredictions, only provide data with low & high predictions
            if len(raw_snow_data) == 4:
                msg = raw_snow_data
            #Turn words into numbers
            if "New snow accumulation of less than half an inch possible." in forecast:
                msg = [0.00,0.25,day,temp]
            if "New snow accumulation of less than one inch possible." in forecast:
                msg = [0.00,0.50,day,temp]
            if "New snow accumulation of around one inch possible." in forecast:
                msg = [0.00,1.00,day,temp]
            a.append(msg)
            txt(server, email, nmbr, msg)
    tm.sleep(5)
    #Place list into a dataframe and send total
    df = pd.DataFrame(columns=['min snow', 'max snow', 'day', 'temp'], data=a)
    mn = df['min snow'].sum()
    mx = df['max snow'].sum()
    tp = round(df['temp'].mean(),2)
    msg = [mn, mx, 'All Week', tp]
    txt(server, email, nmbr, msg)
    print(df)




nmbrs = ['5555555555@vtext.com']
own_nmbr = '5555555555@vtext.com'


#Brighton
#Latitude: 40.60384
#Longitude: -111.5821429
#Forecast APIs
#https://api.weather.gov/points/40.6038,-111.5821

#State wide alerts
#https://api.weather.gov/alerts/active?area=UT

#Forecast API request
b_json = requests.get('https://api.weather.gov/gridpoints/SLC/109,166/forecast')
brighton = b_json.json()
print(brighton)

email = '<email>'
password = '<password>'

server = gmail_conn(email, password)


if str(b_json) == '<Response [200]>':
    for i in range(len(nmbrs)):
        weather(nmbrs[i])
else:
    msg = b_json
    txt(server, email, own_nmbr, msg)
    tm.sleep(60)
    b_json = requests.get('https://api.weather.gov/gridpoints/SLC/109,166/forecast')
    brighton = b_json.json()
    if str(b_json) == '<Response [200]>':
        for i in range(len(nmbrs)):
            weather(nmbrs[i])
    else:
        msg = 'Second' + str(b_json)
        txt(own_nmbr, msg)