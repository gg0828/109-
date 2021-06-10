# -*- coding: utf-8 -*-
import json
import paho.mqtt.client as mqtt
import time
import dht11
import lineTool
import speech_recognition as sr

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
temp_humi = 0.0
temp_temp = 0.0
instance = dht11.DHT11(pin=DHT_PIN)
day_of_low_humi = 0
turn_on = 0
message = "need water !!!!"
token = "7CpnztNzkcG64XFkbz4KMsxD6rXIWD57TpqSKudl395"


#line robot
def linenotify(tt,mm):
    lineTool.lineNotify(tt,mm) # to send message through line

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
    global temp2,temp_temp,temp_humi
    temp = json.loads(msg.payload)
   
    temp2 = float(temp['value'][0])
    if temp2 != 0:
        print(temp['id'])
        if str(temp['id']) == temp_sensorId:
            temp_temp = temp2
            print("temp = ",temp_temp)
            
        else:
            temp_humi = temp2
            print("humi = ",temp_humi)
        

    
    


# subscribe 消息
def on_subscribe():
    mqttClient.subscribe("/v1/device/"+deviceId+"/sensor/"+temp_sensorId+"/rawdata", 1)
    mqttClient.subscribe("/v1/device/"+deviceId+"/sensor/"+humi_sensorId+"/rawdata", 1)
    mqttClient.on_message = on_message_come # 消息到来处理函数

def voice():
    global turn_on
    r=sr.Recognizer()
    m=sr.Microphone()
    with m as source:
        #listen for 1 seconds and create the ambient noise energy level 
        r.adjust_for_ambient_noise(source)
        print("Say something!") 
        audio=r.record(source=m, duration=3)
    # recognize speech using Google Speech Recognition 
    try:
        print(r.recognize_google(audio))
        if r.recognize_google(audio) == 'water':
            turn_on = 1
            print('Watering success')
        elif r.recognize_google(audio) == 'close':
            turn_on = 0
            print('Watering closed')

    except sr.UnknownValueError:
        print("Do nothing")
    except sr.RequestError as e:
        print("No response : {0}".format(e))


def main():
    on_mqtt_connect()
    #data=[{"id":"cin","value":["test"]}]
    #on_publish("/v1/device/115355/rawdata", json.dumps(data), 1)
    on_subscribe()
    global day_of_low_humi,temp_temp,temp_humi,turn_on
    while True:

        voice()
       
        if temp_humi !=0 and temp_temp !=0:
            if temp_humi < 85:
                day_of_low_humi = day_of_low_humi + 1
                print("day cnt = ",day_of_low_humi)
                if day_of_low_humi > 19 :
                    linenotify(token,message)
                    day_of_low_humi = 0
            else:
                day_of_low_humi = 0   
        
        if turn_on == 0:
            data=[{"id":water_sensorId,"value":[0]}]
            on_publish("/v1/device/"+deviceId+"/rawdata",json.dumps(data),1)
        elif turn_on == 1:
            data=[{"id":water_sensorId,"value":[1]}]
            on_publish("/v1/device/"+deviceId+"/rawdata",json.dumps(data),1)



        time.sleep(0.5)    
 


        

        """
        
        data=[{"id":sensorId,"value":[i]}]
        on_publish("/v1/device/"+deviceId+"/rawdata",json.dumps(data),1)
        print("publish")
        time.sleep(5)
        
        """
        
        



if __name__ == '__main__':
    main()



