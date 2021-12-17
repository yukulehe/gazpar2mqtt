# gazpar2mqtt
Python script to fetch GRDF's website data and publish data to a mqtt broker

![Gazpar logo](https://s2.qwant.com/thumbr/474x266/d/6/5f73ca2a6a6ad456cee493bb73bc9bf24662ded76a98c4eb0a117e16d666d2/th.jpg?u=https%3A%2F%2Ftse2.explicit.bing.net%2Fth%3Fid%3DOIP.Y_lVygaMR2JQYgTvLVvc5wHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)

![MQTT logo](https://s2.qwant.com/thumbr/474x266/e/b/0bb1caaf35b0ed78b567ce4ba21cffd3d22f8bc4a7c82a3ba331cc0dd88a23/th.jpg?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.eK8FAO1DnuuVt6wYA1WOmAHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)

# Externals/Thanks
The project has been inspired by job done by [empierre](https://github.com/empierre/domoticz_gaspar) on project domoticz_gazpar and [beufanet](https://github.com/beufanet/gazpar) on project gazinflux availables on Github. I modified a bit the code to work and fit my needs.
Thanks to [echauvet](https://github.com/echauvet) for his big contribution on GRDF API and the calculation of new sensors.

# Informations

Important :
- The tool is still under development, various functions may disappear or be modified.
- GRDF website has a new design since 23/11/2021. We have redesign the app. A lot of work remains. All previous functionalities could not be performed.


## Changelogs :

- v0.6.x :
  - Implementation of a sqlite database
  - Addition of converter factor from Grdf
  - Calculation of aggregated consumptions  for calendar periods (year, month, week and day) and rolling periods (1 year, 1 month, 1 week)
  - Exponential wait between retries when the application failed to connect to GRDF website
- v0.5.x :
  - Hard redesign of the application after new GRDF website released on 23/11/2021 . Thanks to **echauvet** for his contribution.
  - Published values are now PCE dependent
  - Add last index
  - Home assistant : Add entity last index which can be integrated in Hass Energy panel
  - Rework of python code
  - Add Debug mode in environment variable
  - Add connexion retries to GRDF when it failed
- v0.4.x : 
  - Home assistant mqtt discovery available
  - Home assistant add-on available : https://github.com/alexbelgium/hassio-addons/tree/master/gazpar2mqtt (special thx to [alexbelgium](https://github.com/alexbelgium))
  - Enable Docker build for arm/v7 architecture
  - Enable MQTT SSL connexion
  - Grdf's thresholds (seuil) and previous year consumption
- v0.3.x :
  - First reliable release


## Roadmap :

- Retrieve threesolds
- Home assistant custom entity card

# Requirements

## Python3 and libs

**python3** with its dependencies:

``` 
pip3 install -r app/requirement.txt
``` 

## GRDF Gazpar API

Verify you have gazpar data available on [GRDF Portal](https://monespace.grdf.fr/monespace/connexion)
Remember, kWh provided is conversion factor dependant. Please verify it's coherent with your provider bills.


## MQTT broker

A MQTT broker is required. Please check its configuration (hostname, port, remote access allowed, username & password if needed).


## Parameters

Currently, parameters can be provided by command's arguments or by the OS's environment variables.

Mandatory :

| Variable | Description |
| --- | --- |
| **GRDF_USERNAME** | Your GRDF login (ex : myemail@email.com) |
| **GRDF_PASSWORD** | Your GRDF password |
| **MQTT_HOST** | Hostname or ip adress of the MQTT broker |

Optional :

| Variable | Description | Default value |
| --- | --- | --- |
| **SCHEDULE_TIME** | Time for refreshing data everyday | None (format : 14:30) |
| **MQTT_PORT** | Port of the MQTT broker | 1883 |
| **MQTT_TOPIC** | Topic used as prefix | gazpar |
| **MQTT_CLIENTID** | Client id to be used for connexion to the MQTT broker | gazou |
| **MQTT_USERNAME** | Username to be used for connexion to the MQTT brokerr |  |
| **MQTT_PASSWORD** | Password to be used for connexion to the MQTT broker |  |
| **MQTT_QOS** | QOS for message publishing (0, 1 or 2) | 1 |
| **MQTT_RETAIN** | Retain flag| False |
| **MQTT_SSL** | Enable MQTT SSL connexion | False |
| **STANDALONE_MODE** | Enable standalone publication mode | True |
| **HASS_DISCOVERY** | Enable Home assistant dicovery mode | False |
| **HASS_PREFIX** | Home assistant topic prefix | homeassistant |
| **HASS_DEVICE_NAME** | Home assistant device name | gazpar |
| **DB_INIT** | Force reinitialization of the database | False |
| **DEBUG** | Enable debug mode| False |


# Usage

## Running script

Run it manually :

``` 
python3 app/gazpar2mqtt.py
``` 

Run it manually with a selection of arguments overwritting parameters :

``` 
python3 app/gazpar2mqtt.py --grdf_username=myemail@email.com --grdf_password=mypassword --mqtt_host=myhost --mqtt_clientId=gazou --mqtt_retain=True
``` 

Schedule it manually :

``` 
python3 app/gazpar2mqtt.py --schedule 10:30
``` 

Full list of arguments  :

``` 
python3 app/gazpar2mqtt.py --help
``` 



## Docker

![docker_logo](https://s1.qwant.com/thumbr/0x0/2/d/05170a4d28c2e2d0c394367d6db2e6f73292e9fbc305c087b51ee8b689e257/120px-Docker_(container_engine)_logo.png?u=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2Farchive%2F7%2F79%2F20140516082115!Docker_(container_engine)_logo.png%2F120px-Docker_(container_engine)_logo.png&q=0&b=1&p=0&a=0)

Have a look the [docker repository](https://hub.docker.com/r/yukulehe/gazpar2mqtt) 

Example of docker run command with environment variables :

``` 
docker run --name app/gazpar2mqtt -e GRDF_USERNAME=gazou@email.com -e GRDF_PASSWORD=password -e MQTT_HOST=192.168.1.99 -e MQTT_PORT=1883 -e MQTT_CLIENTID=gazou -e MQTT_QOS=1 -e MQTT_TOPIC=gazpar -e MQTT_RETAIN=False --tty yukulehe/gazpar2mqtt:latest
```


## Standalone mode

Default mode, gazpar2mqtt is autonomous and is not dependent of any third-party tool.
You can replace the default topic prefix *gazpar* (see mqtt broker requirements chapter)

### Measures :

Last measures :

| Topic | Description |
| --- | --- |
| gazpar/PCE/index | Gas index in m3 of the last measure |
| gazpar/PCE/date | Date of the last measure |
| gazpar/PCE/energy | Gas consumption in kWh of the last measure |
| gazpar/PCE/gas | Gas consumption in m3 of the last measure  |
| gazpar/PCE/conversion_factor | Conversion factor in kWh/m3 of the last measure  |

Calculated calendar measures :

| Topic | Description |
| --- | --- |
| gazpar/PCE/histo/current_year_gas | Gas consumption in m3 of current year |
| gazpar/PCE/histo/previous_year_gas | Gas consumption in m3 of previous year |
| gazpar/PCE/histo/current_month_gas | Gas consumption in m3 of current month |
| gazpar/PCE/histo/previous_month_gas | Gas consumption in m3 of previous month |
| gazpar/PCE/histo/current_month_previous_year_gas | Gas consumption in m3 of current month, 1 year ago |
| gazpar/PCE/histo/current_week_gas | Gas consumption in m3 of current week |
| gazpar/PCE/histo/previous_week_gas | Gas consumption in m3 of previous week |
| gazpar/PCE/histo/current_week_previous_year | Gas consumption in m3 of current week, 1 year ago |
| gazpar/PCE/histo/day-1_gas | Gas consumption in m3, 1 day ago |
| gazpar/PCE/histo/day-2_gas | Gas consumption in m3, 2 day ago |
| gazpar/PCE/histo/day-3_gas | Gas consumption in m3, 3 day ago |
| gazpar/PCE/histo/day-4_gas | Gas consumption in m3, 4 day ago |
| gazpar/PCE/histo/day-5_gas | Gas consumption in m3, 5 day ago |
| gazpar/PCE/histo/day-6_gas | Gas consumption in m3, 6 day ago |
| gazpar/PCE/histo/day-7_gas | Gas consumption in m3, 7 day ago |

Calculated rolling measures :

| Topic | Description |
| --- | --- |
| gazpar/PCE/histo/rolling_year_gas | Gas consumption in m3 for 1 rolling year |
| gazpar/PCE/histo/rolling_year_last_year_gas | Gas consumption in m3 for 1 rolling year, 1 year ago |
| gazpar/PCE/histo/rolling_month_gas | Gas consumption in m3 for 1 rolling month |
| gazpar/PCE/histo/rolling_month_last_month_gas | Gas consumption in m3 for 1 rolling month, 1 month ago |
| gazpar/PCE/histo/rolling_month_last_year_gas | Gas consumption in m3 for 1 rolling month, 1 year ago |
| gazpar/PCE/histo/rolling_month_last_2_year_gas | Gas consumption in m3 for 1 rolling month, 2 years ago |
| gazpar/PCE/histo/rolling_week_gas | Gas consumption in m3 for 1 rolling week |
| gazpar/PCE/histo/rolling_week_last_week_gas | Gas consumption in m3 for 1 rolling week, 1 week ago |
| gazpar/PCE/histo/rolling_week_last_year_gas | Gas consumption in m3 for 1 rolling week, 1 year ago |
| gazpar/PCE/histo/rolling_week_last_2_year_gas | Gas consumption in m3 for 1 rolling week, 2 years ago |



### Status :

| Topic | Description |
| --- | --- |
| gazpar/PCE/status/date | Last execution date time of gazpar2mqtt |
| gazpar/PCE/status/value | Last execution status of  gazpar2mqtt (ON or OFF) |


## Home Assistant discovery mode

![HA_logo](https://user-images.githubusercontent.com/31646663/141127001-6f868a1a-1820-45bc-9f3b-c3ee2a4d2d06.png)

Gazpar2mqtt provides Home Assistant compatible Mqtt devices. The discovery function enable to use MQTT devices with a minimal configuration effort.
Have a look to [Home Assistant Mqtt discovery documentation](https://www.home-assistant.io/docs/mqtt/discovery/).

### Device :
| Device name | Device ID | Model | Manufacturer |
| --- | --- | --- | --- |
| gazpar | gazpar_PCE | PCE | GRDF |

Note : you can replace the default device name *gazpar* by editing the related parameter.

### List of entities :

Last measure entities :

| Entity name | Component | Device class | Description |
| --- | --- | --- | --- |
| gazpar_PCE_index | Sensor | Gas | Gas index in m3 of the last measure |
| gazpar_PCE_gas | Sensor | Gas | Gas consumption in m3 of the last measure |
| gazpar_PCE_energy | Sensor | Energy | Gas consumption in kWh of the last measure |
| gazpar_PCE_consumption_date | Sensor | Date | Date of the last measure |
| gazpar_PCE_connectivity | Binary sensor | Connectivity | Binary sensor which indicates if the last gazpar statement succeeded (ON) or failed (OFF) |


Calendar measure entities :

| Entity name | Component | Device class | Description |
| --- | --- | --- | --- |
| gazpar_PCE_current_year_gas | Sensor | Gas | Gas consumption in m3 of current year |
| gazpar_PCE_previous_year_gas | Sensor | Gas | Gas consumption in m3 of previous year |
| gazpar_PCE_previous_2_year_gas | Sensor | Gas | Gas consumption in m3 of previous 2 years |
| gazpar_PCE_current_month_gas | Sensor | Gas | Gas consumption in m3 of current month |
| gazpar_PCE_previous_month_gas | Sensor | Gas | Gas consumption in m3 of previous month |
| gazpar_PCE_current_month_last_year_gas | Sensor | Gas | Gas consumption in m3 of current month, 1 year ago |
| gazpar_PCE_current_week_gas | Sensor | Gas | Gas consumption in m3 of current week |
| gazpar_PCE_previous_week_gas | Sensor | Gas | Gas consumption in m3 of current week |
| gazpar_PCE_current_week_last_year_gas | Sensor | Gas | Gas consumption in m3 of current week, 1 year ago |
| gazpar_PCE_current_day_1_gas | Sensor | Gas | Gas consumption in m3 of day -1 |
| gazpar_PCE_current_day_2_gas | Sensor | Gas | Gas consumption in m3 of day -2 |
| gazpar_PCE_current_day_3_gas | Sensor | Gas | Gas consumption in m3 of day -3 |
| gazpar_PCE_current_day_4_gas | Sensor | Gas | Gas consumption in m3 of day -4 |
| gazpar_PCE_current_day_5_gas | Sensor | Gas | Gas consumption in m3 of day -5 |
| gazpar_PCE_current_day_6_gas | Sensor | Gas | Gas consumption in m3 of day -6 |
| gazpar_PCE_current_day_7_gas | Sensor | Gas | Gas consumption in m3 of day -7 |


Rolling measure entities :

| Entity name | Component | Device class | Description |
| --- | --- | --- | --- |
| gazpar_PCE_rolling_year_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling year |
| gazpar_PCE_rolling_year_last_year_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling year, 1 year ago |
| gazpar_PCE_rolling_rolling_month_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling month |
| gazpar_PCE_rolling_month_last_month_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling month, 1 month ago |
| gazpar_PCE_rolling_month_last_year_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling month, 1 year ago |
| gazpar_PCE_rolling_month_last_2_year_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling month, 2 years ago |
| gazpar_PCE_rolling_rolling_week_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling week |
| gazpar_PCE_rolling_week_last_week_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling week, 1 week ago |
| gazpar_PCE_rolling_week_last_year_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling week, 1 year ago |
| gazpar_PCE_rolling_week_last_2_year_gas | Sensor | Gas | Gas consumption in m3 for 1 rolling week, 2 years ago |



### Add-on
For Hass.io users, gazpar2mqtt is also available as an add-on provided by [alexbelgium](https://github.com/alexbelgium) (thanks you to him). Please visit the dedicated [repository](https://github.com/alexbelgium/hassio-addons/tree/master/gazpar2mqtt).
