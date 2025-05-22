import blynklib_mp as blynklib 
import network 
import time 
from machine import Pin, ADC  # Added ADC for soil sensor 
# DHT driver already included into Micropython software as core module 
# so we just import it 
import dht 
 
# WiFi and Blynk credentials 
WIFI_SSID = 'Xiaomi 11i' 
WIFI_PASS = 'a1b2c3d4Jesus#@' 
BLYNK_AUTH = 'JJe94QAAk3P2d4yn2ILN6CCs6nSw8l81' 
GPIO_DHT11_PIN = 2 
SOIL_SENSOR_PIN = ADC(0) # Assuming the soil sensor is connected to GPIO 
35 
 
# Connect to WiFi 
print("Connecting to WiFi network '{}'".format(WIFI_SSID))  
wifi = network.WLAN(network.STA_IF) 
wifi.active(True) 
wifi.connect(WIFI_SSID, WIFI_PASS) 
while not wifi.isconnected(): 
    time.sleep(1) 
     print('WiFi connect retry ...') 
print('WiFi IP:', wifi.ifconfig()[0]) 
 
# Connect to Blynk 
print("Connecting to Blynk server...") 
blynk = blynklib.Blynk(BLYNK_AUTH, 
                       server='68.183.87.221', # set server address 
                       port=80,              # set server port 
                       heartbeat=30,          # set heartbeat to 30 secs 
                       ) 
# Colors for Blynk widgets 
T_COLOR = '#f5b041' 
H_COLOR = '#85c1e9' 
ERR_COLOR = '#444444' 
T_VPIN = 0 
H_VPIN = 1 
S_VPIN = 3 
 
# Initialize DHT22 sensor 
sensor = dht.DHT11(Pin(2)) 
soilsensor = ADC(0) # Initialize soil sensor 
 
# Blynk event handler to read sensor data 
@blynk.handle_event('read V{}'.format(T_VPIN)) 
def read_handler(vpin): 
    temperature = 0.0 
    humidity = 0.0 
 
    # Read sensor data 
    try: 
        sensor.measure() 
        temperature = sensor.temperature() 
        humidity = sensor.humidity() 
    except OSError as o_err: 
        print("Unable to get DHT11 sensor data: '{}'".format(o_err)) 
 
    # Update widget values and colors according to read results 
    if temperature != 0.0 and humidity != 0.0: 
        blynk.set_property(T_VPIN, 'color', T_COLOR) 
        blynk.set_property(H_VPIN, 'color', H_COLOR) 
        blynk.virtual_write(T_VPIN, temperature) 
        blynk.virtual_write(H_VPIN, humidity) 
    else: 
        blynk.set_property(T_VPIN, 'color', ERR_COLOR) 
        blynk.set_property(H_VPIN, 'color', ERR_COLOR) 
# Function to read the soil moisture sensor
def moist_sensor(): 
    soil = soilsensor.read() 
    blynk.virtual_write(S_VPIN, soil) 
    return soil 
 
# MQTT related code (assuming you have proper MQTT setup elsewhere in 
your script) 
def connect_mqtt(): 
    # Implement MQTT connection logic 
    pass 
 
def restart_and_reconnect(): 
    # Implement reconnect logic 
    pass 
# MQTT publishing loop 
try: 
    client = connect_mqtt() 
except OSError as e: 
    restart_and_reconnect() 
last_message = time.time() 
message_interval = 60  # 1 minute interval 
while True: 
    try: 
        if (time.time() - last_message) > message_interval: 
            temp, hum = sensor.temperature(), sensor.humidity()  # Get 
DHT11 readings 
            soil = moist_sensor()  # Get soil moisture reading 
            print(temp, hum, soil) 
            # Publish readings to MQTT topics 
            client.publish(topic_pub_temp, temp) 
            client.publish(topic_pub_hum, hum) 
            client.publish(topic_pub_soilhum, str(soil)) 
            last_message = time.time() 
    except OSError as e: 
        restart_and_reconnect() 
# Run Blynk process 
while True: 
    blynk.run() 
