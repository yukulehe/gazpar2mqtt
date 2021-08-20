# gazpar2mqtt
Python script to fetch GRDF data and publish data to a mqtt broker

![Gazpar logo](https://s2.qwant.com/thumbr/474x266/d/6/5f73ca2a6a6ad456cee493bb73bc9bf24662ded76a98c4eb0a117e16d666d2/th.jpg?u=https%3A%2F%2Ftse2.explicit.bing.net%2Fth%3Fid%3DOIP.Y_lVygaMR2JQYgTvLVvc5wHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)
![MQTT logo](https://s2.qwant.com/thumbr/474x266/e/b/0bb1caaf35b0ed78b567ce4ba21cffd3d22f8bc4a7c82a3ba331cc0dd88a23/th.jpg?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.eK8FAO1DnuuVt6wYA1WOmAHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)

# Externals/Thanks
The project has been inspired by job done by [empierre](https://github.com/empierre/domoticz_gaspar) on project domoticz_gazpar and [beufanet](https://github.com/beufanet/gazpar) on project gazinflux availables on Github. I modified a bit the code to work and fit my needs.

# Requirements

## Python3 and libs

**python3** with its dependencies:

` pip install -r requirements.txt `


## GRDF Gazpar API

Verify you have gazpar data available on [GRDF Portal](https://monespace.grdf.fr/monespace/connexion)

Data provided is per day and per month.

Remember, kWh provided is conversion factor dependant. Please verify it's coherent with your provider bills.

## MQTT broker

A MQTT broker is required. Please check its configuration (hostname, port, remote access allowed if needed).

Fill the mandatory environment **MQTT_HOST** to indicates the MQTT broker hostname or IP adress.

By default, port is set to 1883, prefix topic is *gazpar*, retain flag is set to false, QOS is set to 1. You can modify those values by updating environment variables (**MQTT_PORT**, **MQTT_TOPIC**, **MQTT_RETAIN** and **MQTT_QOS**).

# Usage

## Running script

Test it manually :

` python3 gazpar2mqtt.py `

Schedule it manually :

` python3 gazpar2mqtt.py --schedule 04:00 `

## Docker

Example of docker run command with environment variables :

``` 
docker run -e GRDF_USERNAME=gazou@email.com -e GRDF_PASSWORD=password -e MQTT_HOST=192.168.1.99 e MQTT_PORT=1883 -e MQTT_CLIENTID=gazou -e MQTT_QOS=1 -e MQTT_TOPIC=gazpar -e MQTT_RETAIN=False --tty yukulehe/gazpar2mqtt:0.1 
```


## MQTT publication topics

Please note that only GRDF's **last values** are published in the MQTT broker in the topics bellow.

Note : you can replace the default topic prefix *gazpar* (see mqtt broker requirements chapter)

### Daily values :
> gazpar/daily/date

> gazpar/daily/kwh

> gazpar/daily/mcube

### Monthly values :
> gazpar/monthly/date

> gazpar/monthly/kwh

> gazpar/monthly/mcube

### Status values :
> gazpar/status/date

> gazpar/status/value


