#!/usr/bin/env python3
### Define Standalone functionality. ###

# Constants for topics
TOPIC_LAST = "/last" # Last
TOPIC_PUBLISHED = "/published" # published
TOPIC_HISTO = "/histo" # Histo
TOPIC_STATUS = "/status" # status
TOPIC_THRESOLD = "/thresold" # Thresold


class Standalone:
  
  # Constructor
  def __init__(self,prefix):
    
    self.prefix = prefix
    
    self.lastTopic = prefix + TOPIC_LAST + '/'
    self.publishedTopic = prefix + TOPIC_PUBLISHED + '/'
    self.histoTopic = prefix + TOPIC_HISTO + '/'
    self.statusTopic = prefix + TOPIC_STATUS + '/'
    self.thresoldTopic = prefix + TOPIC_THRESOLD + '/'
    
