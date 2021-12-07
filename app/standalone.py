#!/usr/bin/env python3
### Define Standalone functionality. ###

# Constants for topics

## Index
TOPIC_INDEX = "/index"

## Last measure
TOPIC_LAST_DATE = "/last/date"
TOPIC_LAST_KWH = "/last/kwh"
TOPIC_LAST_MCUBE = "/last/mcube"

## Calculated measure
TOPIC_HISTO_MCUBE = "/histo/mcube"

## Status
TOPIC_STATUS_DATE = "/status/date"
TOPIC_STATUS_VALUE = "/status/value"


class Standalone:
  
  # Constructor
  def __init__(self,prefix):
    
    self.prefix = prefix
    
    self.statusDateTopic = prefix + TOPIC_STATUS_DATE
    self.statusValueTopic = prefix + TOPIC_STATUS_VALUE
    
    self.lastDateTopic = prefix + TOPIC_LAST_DATE
    self.lastKwhTopic = prefix + TOPIC_LAST_KWH
    self.lastMcubeTopic = prefix + TOPIC_LAST_MCUBE
    
    self.histoMcubeTopic = prefix + TOPIC_HISTO_MCUBE
    
    self.indexTopic = prefix + TOPIC_INDEX
    
    
