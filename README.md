# gazpar2mqtt
Python script to fetch GRDF data and publish data to a mqtt broker

![Gazpar logo](https://s2.qwant.com/thumbr/474x266/d/6/5f73ca2a6a6ad456cee493bb73bc9bf24662ded76a98c4eb0a117e16d666d2/th.jpg?u=https%3A%2F%2Ftse2.explicit.bing.net%2Fth%3Fid%3DOIP.Y_lVygaMR2JQYgTvLVvc5wHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)
![MQTT logo](https://s2.qwant.com/thumbr/474x266/e/b/0bb1caaf35b0ed78b567ce4ba21cffd3d22f8bc4a7c82a3ba331cc0dd88a23/th.jpg?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.eK8FAO1DnuuVt6wYA1WOmAHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)

# Externals/Thanks
The project has been inspired by job done by [empierre](https://github.com/empierre/domoticz_gaspar) on project domoticz_gazpar and [beufanet](https://github.com/beufanet/gazpar) on project gazinflux availables on Github. I modified a bit the code to work and fit my needs.

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
| --- | --- | --- |
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

[Docker repository](https://hub.docker.com/repository/docker/yukulehe/gazpar2mqtt) 

Example of docker run command with environment variables :

``` 
docker run --name app/gazpar2mqtt -e GRDF_USERNAME=gazou@email.com -e GRDF_PASSWORD=password -e MQTT_HOST=192.168.1.99 -e MQTT_PORT=1883 -e MQTT_CLIENTID=gazou -e MQTT_QOS=1 -e MQTT_TOPIC=gazpar -e MQTT_RETAIN=False --tty yukulehe/gazpar2mqtt:latest
```


## MQTT publication topics

Please note that only GRDF's **last values** are published in the MQTT broker in the topics bellow.

Note : you can replace the default topic prefix *gazpar* (see mqtt broker requirements chapter)

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
