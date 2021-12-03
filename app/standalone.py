### Define Standalone functionality. ###

# Constants for topics

## Daily
TOPIC_DAILY_DATE = "/daily/date"
TOPIC_DAILY_KWH = "/daily/kwh"
TOPIC_DAILY_MCUBE = "/daily/mcube"

## Monthly
TOPIC_MONTHLY_DATE = "/monthly/month"
TOPIC_MONTHLY_KWH = "/monthly/kwh"
TOPIC_MONTHLY_KWH_TSH = "/monthly/kwh/threshold"
TOPIC_MONTHLY_KWH_PREV = "/monthly/kwh/previous"
TOPIC_MONTHLY_MCUBE = "/monthly/mcube"
TOPIC_MONTHLY_MCUBE_PREV = "/monthly/kwh/previous"


## Status
TOPIC_STATUS_DATE = "/status/date"
TOPIC_STATUS_VALUE = "/status/value"


class Standalone:
  
  # Constructor
  def __init__(self):
    
    
