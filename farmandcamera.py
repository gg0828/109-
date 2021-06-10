# -*- coding: utf-8 -*-
import json
import paho.mqtt.client as mqtt
import time
import dht11

import RPi.GPIO as GPIO
LED_PIN = 12
DHT_PIN = 3
GPIO.setmode(GPIO.BOARD) #z shape
GPIO.setup(LED_PIN, GPIO.OUT)

MQTTHOST = "iot.cht.com.tw"
MQTTPORT = 1883
mqttClient = mqtt.Client()
apikey = "DKR40A7A1U2T9FX1YZ"

temp_sensorId = "planet_temp"
humi_sensorId = "planet_hum"
water_sensorId = "Turn_on_water"
deviceId = "21955419281"  
temp2  = 0.0
instance = dht11.DHT11(pin=DHT_PIN)

from flask import Flask, render_template, Response
from camera_pi import Camera

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('stream.html')

def gen(camera):
    time_first = time.time()
    while True:
        now_time = time.time()
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if now_time - time_first > 5:
            time_first = time.time()
            result= instance.read()
            temperature = result.temperature
            humi = result.humidity
            if humi > 0 and temperature > 0:
                print("temperature=",temperature)
                print('humi= ',humi)
                data=[{"id":temp_sensorId,"value":[temperature]}]
                on_publish("/v1/device/"+deviceId+"/rawdata",json.dumps(data),1)
                data=[{"id":humi_sensorId,"value":[humi]}]
                on_publish("/v1/device/"+deviceId+"/rawdata",json.dumps(data),1)
                print("publish")
        

@app.route('/video_feed')
def video_feed():
    
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# 连接MQTT服务器
def on_mqtt_connect():
    mqttClient.username_pw_set(username=apikey,password=apikey)
    mqttClient.connect(MQTTHOST, MQTTPORT, 61)
    mqttClient.loop_start()
    #mqttClient.loop_forever()


# publish 消息
def on_publish(topic, payload, qos):
    mqttClient.publish(topic, payload, qos)

# 消息处理函数
def on_message_come(lient, userdata, msg):
    global temp2
    temp = json.loads(msg.payload)
    temp2 = int(temp['value'][0])
    if temp2 == 1:
        print("turn on")
        GPIO.output(LED_PIN, GPIO.HIGH)
    else:
        print("turn off")
        GPIO.output(LED_PIN, GPIO.LOW)

   
    


# subscribe 消息
def on_subscribe():
    mqttClient.subscribe("/v1/device/"+deviceId+"/sensor/"+water_sensorId+"/rawdata", 1)
    mqttClient.on_message = on_message_come # 消息到来处理函数


def main():
    on_mqtt_connect()
    #data=[{"id":"cin","value":["test"]}]
    #on_publish("/v1/device/115355/rawdata", json.dumps(data), 1)
    on_subscribe()
    """
    while True:
        result= instance.read()
        temperature = result.temperature
        humi = result.humidity
        print("temperature=",temperature)
        print('humi= ',humi)
        data=[{"id":temp_sensorId,"value":[temperature]}]
        on_publish("/v1/device/"+deviceId+"/rawdata",json.dumps(data),1)
        data=[{"id":humi_sensorId,"value":[humi]}]
        on_publish("/v1/device/"+deviceId+"/rawdata",json.dumps(data),1)
        print("publish")
        

    
        time.sleep(5)
        

       
        
        data=[{"id":sensorId,"value":[i]}]
        on_publish("/v1/device/"+deviceId+"/rawdata",json.dumps(data),1)
        print("publish")
        time.sleep(5)
        
    """
        
        



if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=80, debug=True)
    



