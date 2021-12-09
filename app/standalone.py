#!/usr/bin/env python3
### Define Standalone functionality. ###

# Constants for topics

## Last measure
TOPIC_LAST = "/last"

## Calculated measure
TOPIC_HISTO_GAS = "/histo/gas"

## Status
TOPIC_STATUS = "/status"


class Standalone:
  
  # Constructor
  def __init__(self,prefix):
    
    self.prefix = prefix
    
    self.lastTopic = prefix + TOPIC_LAST + '/'
    self.histoGasTopic = prefix + TOPIC_HISTO_GAS + '/'
    self.statusTopic = prefix + TOPIC_STATUS + '/'
    
