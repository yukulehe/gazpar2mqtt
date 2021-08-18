#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Work in progress...

import os
import sys
import datetime
#import schedule
import time
import locale
from dateutil.relativedelta import relativedelta
import gazpar
import mqttpub
import json

import argparse
import logging
import pprint
from envparse import env


PFILE = "/.params"
DOCKER_MANDATORY_VARENV=['GRDF_USERNAME','GRDF_PASSWORD','MQTT_HOSTNAME','MQTT_PORT']
DOCKER_OPTIONAL_VARENV=['MQTT_CLIENTID','MQTT_QOS', 'MQTT_TOPIC', 'MQTT_RETAIN']
