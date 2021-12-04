#!/usr/bin/env python3
### Define Standalone functionality. ###

# Constants for topics

## Index
TOPIC_INDEX = "/index"

## Daily
TOPIC_DAILY_DATE = "/daily/date"
TOPIC_DAILY_KWH = "/daily/kwh"
TOPIC_DAILY_MCUBE = "/daily/mcube"


## Status
TOPIC_STATUS_DATE = "/status/date"
TOPIC_STATUS_VALUE = "/status/value"


class Standalone:
  
  # Constructor
  def __init__(self,prefix):
    
    self.prefix = prefix
    
    self.statusDateTopic = prefix + TOPIC_STATUS_DATE
    self.statusValueTopic = prefix + TOPIC_STATUS_VALUE
    
    self.dailyDateTopic = prefix + TOPIC_DAILY_DATE
    self.dailyKwhTopic = prefix + TOPIC_DAILY_KWH
    self.dailyMcubeTopic = prefix + TOPIC_DAILY_MCUBE
    
    self.indexTopic = prefix + TOPIC_INDEX
    
    
