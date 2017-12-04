import datetime
import json
from urllib.request import Request, urlopen
from urllib import error
import os
from SystemOwner import PredictionTools as pt


def get_predicted_values(location):
    predicted_values = pt.fetch_predicted_values(str(location))
    return predicted_values


def fetchDataNOAA(location):
    """
    Download the data from NREL based on the input city. Google API is used to get the latitude and longitude of the
    location. NREL API is used to download GHI, Wind Speed and Temperature data.
    :param zipcode:
    """

    def get_csv_by_year(startyear, endyear, url_base, location):
        if os.path.isdir(location+'/Datasets') is False:
            os.makedirs(location+'/Datasets')
        for year in range(startyear, endyear):
            url = url_base + '&names=' + str(year)
            print(url)
            try:
                page = urlopen(url)
            except error:
                print("Exception occured ! Starting now from " + str(year))
                get_csv_by_year(year, endyear, url_base)
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            content = page.read().decode()
            weatherCSV = open(location+'/Datasets/' + str(year) + ".csv", "w")
            weatherCSV.write(content)

    address = pt.get_city_and_state(location)
    lat_long_api = "https://maps.googleapis.com/maps/api/geocode/json?address=" + address[0] + ',' + address[1]
    # lat_long_api = "http://maps.googleapis.com/maps/api/geocode/json?address="+str(zipcode)
    page = urlopen(lat_long_api)
    req = Request(lat_long_api, headers={'User-Agent': 'Mozilla/5.0'})
    content = json.loads(page.read().decode())
    # pdb.set_trace()
    lat_long = content["results"][0]["geometry"]["location"]
    lat = lat_long["lat"]
    lon = lat_long["lng"]

    # Download the data and save it in files
    api_key = '3KEle87nPOrTBNXBVWeXqChGztQm0pvTLbepwVwW'

    attributes = 'ghi,wind_speed_10m_nwp,surface_air_temperature_nwp'
    leap_year = 'false'
    # Set time interval in minutes to '30'.
    interval = '30'
    # Specify Coordinated Universal Time (UTC), 'true' will use UTC, 'false' will use the local time zone of the data.
    utc = 'false'
    your_name = 'Nischal+Kumar'
    # Your reason for using the NSRDB.
    reason_for_use = 'beta+testing'
    # Your affiliation
    your_affiliation = 'Arizona+State+University'
    # Your email address
    your_email = 'nischal.kumar@.com'
    # Please join our mailing list so we can keep you up-to-date on new developments.
    mailing_list = 'true'
    year = datetime.date.today().year - 1

    
    url = 'http://developer.nrel.gov/api/solar/nsrdb_0512_download.csv?wkt=POINT({lon}%20{lat})&leap_day={leap}&interval={interval}&utc={utc}&full_name={name}&email={email}&affiliation={affiliation}&mailing_list={mailing_list}&reason={reason}&api_key={api}&attributes={attr}'\
          .format(
          lat=lat,
          lon=lon,
          leap=leap_year,
          interval=interval,
          utc=utc, name=your_name,
          email=your_email,
          mailing_list=mailing_list,
          affiliation=your_affiliation,
          reason=reason_for_use,
          api=api_key,
          attr=attributes)
    get_csv_by_year(year-15, year, url, str(location))
    pt.build_model(str(location))

