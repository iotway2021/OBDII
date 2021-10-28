import threading
import time
import obd
import paho.mqtt.client as mqtt
import json
import sys
import geocoder
import ssl

Dict  = {}
DictlastPub ={}
PublishList =[]
def MQTTClientConnection():
    global mclient
    global IsMQTTConnectionisinProgress
    IsMQTTConnectionisinProgress =True
    while IsMQTTConnectionisinProgress:
        try:
            try:
                if mclient is not None:
                    mclient.disconnect()
            except:
                e = sys.exc_info()[0]
                print(e)

            mclient = mqtt.Client()
            mclient.username_pw_set("Demo","Demo123")
            print("Connecting MQTT!!!")

            IsMQTTConnected = mclient.connect("18.188.164.204",1884,10)
            mclient.on_connect = on_connect
            mclient.on_disconnect = on_disconnect
            mclient.loop_forever()
            print("Disconected from old thread")
            break
        except:
            e = sys.exc_info()[0]
            print(e)

        time.sleep(10)

def on_disconnect(client, userdata, rc):

    if not IsMQTTConnectionisinProgress:
        print("[INFO] DisConnected to broker")
        x3 = threading.Thread(target=MQTTClientConnection)
        x3.start()

def on_connect(client, userdata, flags, rc):
    global connected  # Use global variable
    global IsMQTTConnectionisinProgress
    if rc == 0:

        print("[INFO] Connected to broker")
        IsMQTTConnectionisinProgress = False
        connected = True  # Signal connection
    else:
        print("[INFO] Error,MQTT connection failed")

def OBDConnection():
    global IsOBDConnected

    global modeA
    modeA =None
    global modeB
    modeB =None
    global modeC
    modeC =None
    global modeD
    modeD =None

    IsOBDConnected=False

    while not IsOBDConnected:
        global connection
        connection=None
        global OBDConnectioninProgress
        OBDConnectioninProgress =True
        print("Connecting OBD!!!")
        try:
            connection = obd.OBD('\\.\\COM2', 38400)  # connect to the first port in the list
            IsOBDConnected = connection.is_connected()

            if IsOBDConnected:
                print("ODB Connected !!!")
                cmd = obd.commands[1][0]
                response = connection.query(cmd)  # send the command, and parse the response
                if not response.is_null():
                    modeA=response.value
                    print("modeA :")
                    print(modeA)
                    Dict[0] =str(modeA)
                cmd = obd.commands[1][32]
                response = connection.query(cmd)  # send the command, and parse the response
                if not response.is_null():
                    modeB = response.value
                    print("modeB:")
                    print(modeB)
                    Dict[32] = str(modeB)
                cmd = obd.commands[1][64]
                response = connection.query(cmd)  # send the command, and parse the response
                if not response.is_null():
                    modeC = response.value
                    print("modeC :")
                    print(modeC)
                    print(modeB)
                    Dict[64] = str(modeC)
                cmd = obd.commands[1][96]
                response = connection.query(cmd)  # send the command, and parse the response
                if not response.is_null():
                    modeD = response.value
                    print("modeD :")
                    print(modeD)
                    Dict[96] = str(modeD)
                OBDConnectioninProgress = False
                break
        except:
            e = sys.exc_info()[0]
            print(e)
        Dict["OBD Communication Status"] = "Connected" if IsOBDConnected  else "Disconnceted"
        time.sleep(30)

def ReadData():
    while True:
        if (connection is not None) and (connection.is_connected()):
            if modeA is not None:
                for pidindex in range(0, len(modeA)):
                    if modeA[pidindex]:
                        pidA = 1 + pidindex
                        if(pidA >= 32):
                            continue;
                        cmd = obd.commands[1][pidA]
                        response = connection.query(cmd)  # send the command, and parse the response
                        if not response.is_null():
                            #if response.value is obd.OBDResponse.Status:
                                #Dict[pidA+"(MIL)"] = obd.OBDResponse.Status(response.value).MIL
                            data = str(response.value).replace(str(response.unit), "").strip()
                            Dict[pidA] = data
                            #print(str(pidA) + ":" + data)

                            time.sleep(0.002)
                        #else:
                            #print("pid not response:" + str(pidA))

            if modeB is not None:
                for pidindex in range(0, len(modeB)):
                    if modeB[pidindex]:
                        pidB= 33 + pidindex
                        if (pidB >= 64):
                            continue;
                        cmd = obd.commands[1][pidB]
                        response = connection.query(cmd)  # send the command, and parse the response
                        if not response.is_null():
                            data = str(response.value).replace(str(response.unit), "").strip()
                            Dict[pidB] = data
                            #print(str(pidB) + ":" + data)
                            time.sleep(0.002)
                        #else:
                            #print("pid not response:" + str(pidB))
            if modeC is not None:
                for pidindex in range(0, len(modeC)):
                    if modeC[pidindex]:
                        pidC = 65 + pidindex
                        if (pidB >= 96):
                            continue;
                        cmd = obd.commands[1][pidC]
                        response = connection.query(cmd)  # send the command, and parse the response
                        if not response.is_null():
                            data = str(response.value).replace(str(response.unit), "").strip()
                            Dict[pidC] = data
                           # print(str(pidC) + ":" + data)
                            time.sleep(0.002)
                        #else:
                            #print("pid not response:" + str(pidC))

            if modeD is not None:
                for pidindex in range(0, len(modeD)):
                    if modeD[pidindex]:
                        pidD = 97 + pidindex
                        if (pidB >= 128):
                            continue;
                        cmd = obd.commands[1][pidD]
                        response = connection.query(cmd)  # send the command, and parse the response
                        if not response.is_null():
                            data = str(response.value).replace(str(response.unit), "").strip()
                            Dict[pidD] = data
                            # print(str(pidC) + ":" + data)
                            time.sleep(0.002)
                        # else:
                        # print("pid not response:" + str(pidC))

            IsDataReadOnce =True

        elif (connection is not None) and (not connection.is_connected()):
            if not OBDConnectioninProgress:
                print("Requesting ReadData thread to reconnect OBD")
                y1 = threading.Thread(target=OBDConnection, name='y1')
                y1.start()

        time.sleep(30)

def StorePublishData():
    while True:
        if not IsDataReadOnce:
            time.sleep(1000)
            continue
        includethiskey = False
        myPublishlist = []
        for key in Dict.keys() :
            includethiskey = False
            if key in DictlastPub:
                if not DictlastPub[key]  == Dict[key]:
                    includethiskey = True
            else:
                DictlastPub[key] = Dict[key]
                includethiskey =True

            if includethiskey:
                myPublishlist.append(str(key) + ":"+Dict[key])
        if len(myPublishlist) > 0:
            if len(PublishList) >= 30:
                PublishList.pop(0)

            PublishList.append(myPublishlist)
            print(myPublishlist)
            print(len(PublishList))
        time.sleep(30)

def MQTTPublishData():
    while True:
        time.sleep(1)
        if len(PublishList) > 0:
            if mclient.is_connected():
                pdata= PublishList.pop(0)
                jsonStr = json.dumps(pdata)
                mclient.publish("Cartest",jsonStr)


if __name__ == "__main__":
    g = geocoder.ip('me')
    print(g.latlng)
    for pid in range(0,200):
        Dict[pid] = "NA"

    global IsDataReadOnce
    IsDataReadOnce =False
    x = threading.Thread(target=MQTTClientConnection)
    x.start()
    time.sleep(2)
    y = threading.Thread(target=OBDConnection, name='y')
    y.start()
    time.sleep(5)
    z = threading.Thread(target=ReadData,  name='z')
    z.start()
    time.sleep(30)
    a = threading.Thread(target=StorePublishData, name='a')
    a.start()
    b= threading.Thread(target=MQTTPublishData, name='b')
    b.start()


