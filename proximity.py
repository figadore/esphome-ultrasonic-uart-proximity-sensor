# -*- coding:utf-8 -*-
'''
  # Connect board with raspberryPi.
  # Run this script.
  #
  # Connect A02 to UART
  # get the distance value
  #
  # Copyright   [DFRobot](http://www.dfrobot.com), 2016
  # Copyright   GNU Lesser General Public License
'''
import time
import traceback
import datetime
import requests

from DFRobot_RaspberryPi_A02YYUW import DFRobot_A02_Distance as Board

print("Initializing...")

board = Board()

def check_status(dis):
  # We want to check the status often and print errors if there are any
  if board.last_operate_status == board.STA_OK:
    return True
  elif board.last_operate_status == board.STA_ERR_CHECKSUM:
    print("ERROR")
  elif board.last_operate_status == board.STA_ERR_SERIAL:
    print("Serial open failed!")
  elif board.last_operate_status == board.STA_ERR_CHECK_OUT_LIMIT:
    print("Above the upper limit: %d" %dis)
  elif board.last_operate_status == board.STA_ERR_CHECK_LOW_LIMIT:
    print("Below the lower limit: %d" %dis)
  elif board.last_operate_status == board.STA_ERR_DATA:
    print("No data! Green disconnected?")
  return False

def update_ha(distance):
  url = f"http://{os.getenv('HOME_ASSISTANT_URL')}:8123/api/states/sensor.sump_pump_level"
  headers = {
    "Authorization": f"Bearer {os.getenv('HOME_ASSISTANT_BEARER_TOKEN')}",
    "Content-Type": "application/json"
  }
  # Send update with timestamp to force state's last_updated field to change
  # This is useful for checking whether the sensor has been offline for too long (loss of power?)
  timestamp = datetime.datetime.now().isoformat()
  json = {"state": distance, "attributes": {"unit_of_measurement": "mm", "time": timestamp}}
  try:
    response = requests.post(url, headers=headers, json=json)
  except Exception as e:
    print(e)
    print(traceback.format_exc())

if __name__ == "__main__":
  dis_min = 1   #Minimum ranging threshold: capable of 0cmm, but 0 also shows up when proximity not detected
  dis_max = 1000 #Highest ranging threshold: 4500mm was the default, but should never detect water more than 1m away
  board.set_dis_range(dis_min, dis_max)
  # Get initial values for distance and last reported
  distance = board.getDistance()
  # Set initial values in case first reading is an error
  last_reported_time = 0
  last_reported_value = 0
  status_ok = check_status(distance)
  if status_ok:
    print("Distance %d mm" %distance)
    update_ha(distance)
    last_reported_time = time.time()
    last_reported_value = distance
  # Read sensor every 1 second. Report value every 60 seconds, or when value has changed 20mm since last update
  polling_interval = 1
  update_interval = 60
  # up is the direction of water draining
  up_change_threshold = 20
  down_change_threshold = -10
  spurious_change_threshold = 100
  while True:
    distance = board.getDistance()
    status_ok = check_status(distance)
    since_last_reported_time = time.time() - last_reported_time
    # Only update HA if the sensor is working properly and distance is changing significantly or update interval reached
    quick_change = (distance - last_reported_value) >= up_change_threshold or (distance - last_reported_value) <= down_change_threshold
    spurious_change = abs(distance - last_reported_value) > spurious_change_threshold
    if status_ok and (since_last_reported_time > update_interval or (quick_change and not spurious_change)):
      print("Distance %d mm" %distance)
      update_ha(distance)
      last_reported_time = time.time()
      last_reported_value = distance
    time.sleep(polling_interval) #Delay time < 0.6s (not sure what this means)