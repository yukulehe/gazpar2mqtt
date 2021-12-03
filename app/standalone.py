### Define Standalone functionality. ###

# Constants for topics

## Daily
TOPIC_DAILY_DATE = "/daily/date"
TOPIC_DAILY_KWH = "/daily/kwh"
TOPIC_DAILY_MCUBE = "/daily/mcube"
TOPIC_DAILY_INDEX = "/daily/index"

## Status
TOPIC_STATUS_DATE = "/status/date"
TOPIC_STATUS_VALUE = "/status/value"


class Standalone:
  
  # Constructor
  def __init__(self,prefix):
    
    self.prefix = prefix
    
    self.statusDateTopic = prefix + TOPIC_STATUS_DATE
    self.statusValue = prefix + TOPIC_STATUS_VALUE
    
    self.daily_date = prefix + TOPIC_DAILY_DATE
    self.daily_kwh = prefix + TOPIC_DAILY_KWH
    self.daily_mcube = prefix + TOPIC_DAILY_MCUBE
    self.daily_index = prefix + TOPIC_DAILY_INDEX
    
    
