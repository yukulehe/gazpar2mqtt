# gazpar2mqtt
Python script to fetch GRDF data and publish data to a mqtt broker

![Gazpar logo](https://s2.qwant.com/thumbr/474x266/d/6/5f73ca2a6a6ad456cee493bb73bc9bf24662ded76a98c4eb0a117e16d666d2/th.jpg?u=https%3A%2F%2Ftse2.explicit.bing.net%2Fth%3Fid%3DOIP.Y_lVygaMR2JQYgTvLVvc5wHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)
![MQTT logo](https://s2.qwant.com/thumbr/474x266/e/b/0bb1caaf35b0ed78b567ce4ba21cffd3d22f8bc4a7c82a3ba331cc0dd88a23/th.jpg?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.eK8FAO1DnuuVt6wYA1WOmAHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)

# Externals/Thanks
The project has been inspired by job done by [empierre](https://github.com/empierre/domoticz_gaspar) on project domoticz_gazpar and [beufanet](https://github.com/beufanet/gazpar) on project gazinflux availables on Github. I modified a bit the code to work and fit my needs.

# Informations

Important : the tool is still under development, various functions may disappear or be modified.

## Changelogs :

- v0.4 : Home assistant mqtt discovery
- v0.3 : First reliable release

## Roadmap :

- Home assistant add-on

# Requirements

## Python3 and libs

**python3** with its dependencies:

``` 
pip3 install -r app/requirements.txt
``` 

## GRDF Gazpar API

Verify you have gazpar data available on [GRDF Portal](https://monespace.grdf.fr/monespace/connexion)

Data provided is the last day and last month consumptions.

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

Optionnal :

| Variable | Description | Default value |
| --- | --- | --- |
| **SCHEDULE_TIME** | Time for refreshing data everyday | 04:00 |
| **MQTT_PORT** | Port of the MQTT broker | 1883 |
| **MQTT_TOPIC** | Topic used as prefix | gazpar |
| **MQTT_CLIENTID** | Client id to be used for connexion to the MQTT broker | gazou |
| **MQTT_USERNAME** | Username to be used for connexion to the MQTT brokerr |  |
| **MQTT_PASSWORD** | Password to be used for connexion to the MQTT brokerr |  |
| **MQTT_QOS** | QOS for message publishing (0, 1 or 2) | 1 |
| **MQTT_RETAIN** | Retain flag, default False | False |
| **STANDALONE_MODE** | Enable standalone publication mode | True |
| **HASS_DISCOVERY** | Enable Home assistant dicovery mode | False |
| **HASS_PREFIX** | Home assistant topic prefix | homeassistant |


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
python3 app/gazpar2mqtt.py --schedule 04:00
``` 

Full list of arguments  :

``` 
python3 app/gazpar2mqtt.py --help
``` 



## Docker

![docker_logo](https://s1.qwant.com/thumbr/0x0/2/d/05170a4d28c2e2d0c394367d6db2e6f73292e9fbc305c087b51ee8b689e257/120px-Docker_(container_engine)_logo.png?u=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fcommons%2Fthumb%2Farchive%2F7%2F79%2F20140516082115!Docker_(container_engine)_logo.png%2F120px-Docker_(container_engine)_logo.png&q=0&b=1&p=0&a=0)

Have a look the [docker repository](https://hub.docker.com/repository/docker/yukulehe/gazpar2mqtt) 

Example of docker run command with environment variables :

``` 
docker run --name app/gazpar2mqtt -e GRDF_USERNAME=gazou@email.com -e GRDF_PASSWORD=password -e MQTT_HOST=192.168.1.99 -e MQTT_PORT=1883 -e MQTT_CLIENTID=gazou -e MQTT_QOS=1 -e MQTT_TOPIC=gazpar -e MQTT_RETAIN=False --tty yukulehe/gazpar2mqtt:latest
```


## Standalone mode

Default mode, gazpar2mqtt is autonomous and is not dependent of any third-party tool.
Please note that only GRDF's **last values** are published in the MQTT broker in the topics bellow.
You can replace the default topic prefix *gazpar* (see mqtt broker requirements chapter)

### Daily values :

| Topic | Description |
| --- | --- |
| gazpar/daily/date | Date of the last daily statement |
| gazpar/daily/kwh | Consumption in kwh of the last daily statement |
| gazpar/daily/mcube | Consumption in cube meter of the last daily statement  |
| gazpar/daily/delta | Variation in percentage between the last and the previous daily statement  |

### Monthly values :

| Topic | Description |
| --- | --- |
| gazpar/monthly/date | Month of the last monthly statement |
| gazpar/monthly/kwh | Consumption in kwh of the last monthly statement |
| gazpar/monthly/mcube | Consumption in cube meter of the last monthly statement  |
| gazpar/monthly/delta | Variation in percentage between the last and the previous monthly statement  |

### Status values :


| Topic | Description |
| --- | --- |
| gazpar/status/date | Last execution date time of gazpar2mqtt |
| gazpar/status/value | Last execution status of  gazpar2mqtt |


## Home Assistant discovery mode

![HA_logo](https://user-images.githubusercontent.com/31646663/141127001-6f868a1a-1820-45bc-9f3b-c3ee2a4d2d06.png)

Gazpar2mqtt provides Home Assistant compatible Mqtt devices. The discovery function enable to use MQTT devices with a minimal configuration effort.
Have a look to [Home Assistant Mqtt discovery documentation](https://www.home-assistant.io/docs/mqtt/discovery/).

### List of available sensors :

| Sensor name | Component | Device class | Description |
| --- | --- | --- | --- |
| gazpar_daily_gas | Sensor | Gas | Gas consumption in m3 of the last daily statement |
| gazpar_daily_energy | Sensor | Energy | Gas consumption in kWh of the last daily statement |
| gazpar_monthly_gas | Sensor | Gas | Gas consumption in m3 of the last monthly statement |
| gazpar_monthly_energy | Sensor | Energy | Gas consumption in kWh of the last monthly statement |
| gazpar_consumption_date | Sensor | Date | Date of the last daily statement |
| gazpar_consumption_month | Sensor | Text | Month of the last monthly statement |
| gazpar_connectivity | Binary sensor | Connectivity | Binary sensor which indicates if the last gazpar statement succeeded (ON) or failed (OFF) |

### List of topics :
| Topic | Description
| --- | --- 
| home_assistant/sensor/gazpar/config | Sensor's configuration topic |
| home_assistant/sensor/gazpar/state | Sensor's state topic |
| home_assistant/binary_sensor/gazpar/config | Binary sensor's configuration topic |
| home_assistant/binary_sensor/gazpar/state | Binary sensor's state topic |

Note : you can replace the default topic prefix *home_asssistant*
