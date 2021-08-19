# gazpar2mqtt
Python script to fetch GRDF data and publish data to a mqtt broker

![Gazpar logo](https://s2.qwant.com/thumbr/474x266/d/6/5f73ca2a6a6ad456cee493bb73bc9bf24662ded76a98c4eb0a117e16d666d2/th.jpg?u=https%3A%2F%2Ftse2.explicit.bing.net%2Fth%3Fid%3DOIP.Y_lVygaMR2JQYgTvLVvc5wHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)
![MQTT logo](https://s2.qwant.com/thumbr/474x266/e/b/0bb1caaf35b0ed78b567ce4ba21cffd3d22f8bc4a7c82a3ba331cc0dd88a23/th.jpg?u=https%3A%2F%2Ftse3.mm.bing.net%2Fth%3Fid%3DOIP.eK8FAO1DnuuVt6wYA1WOmAHaEK%26pid%3DApi&q=0&b=1&p=0&a=0)

# Externals/Thanks
The project has been inspired by job done by [empierre](https://github.com/empierre/domoticz_gaspar) on project domoticz_gazpar and [beufanet](https://github.com/beufanet/gazpar) on project gazinflux availables on Github. I modified a bit the code to work and fit my needs.

# Requirements

## Python3 and libs

**python3** with its dependencies:

> pip install -r requirements.txt

If you want to debug, please set level=logging.INFO to level=logging.DEBUG

## GRDF Gazpar API

Verify you have gazpar data available on [GRDF Portal](https://monespace.grdf.fr/monespace/connexion)

Data provided is per day and per month.

Remember, kWh provided is conversion factor dependant. Please verify it's coherent with your provider bills.

## MQTT broker

A MQTT broker is required. Please check its configuration (hostname, port, remote access allowed if needed).
By default, retain flag is set to false, QOS is set to 1. You can update corresponding environment variables.

# MQTT publication topics

GRDF's values are published in the MQTT broker following topics.

Note : you can replace default topic prefix (*gazpar*) by another filling environnement variable **TOPIC**.

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

## Repository status
Work in progress....
