#!/usr/bin/env python
# <bitbar.title>Ubiquiti mFi Power</bitbar.title>
# <bitbar.author></bitbar.author>
# <bitbar.author.github>one4many</bitbar.author.github>
# <bitbar.desc>Switch on/off mFi Power sockets</bitbar.desc>
# <bitbar.dependencies>python,requests</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/one4many/mFiPowerBar</bitbar.abouturl>

import sys
import os
import os.path
import time
import argparse
import urllib
import json
import base64
from mFiPower import mFiPower

# see the README.md for username and password
MFIPDEVS = [
#    { 'NAME': 'dev1', 'HOST': '192.168.1.44', 'USER': 'username', 'PASSWD': 'password' },
#    { 'NAME': 'dev2', 'HOST': '192.168.1.45', 'USER': 'username', 'PASSWD': 'password' },
]

if not MFIPDEVS:
    print("ERROR| color=red")
    print("---")
    print("edit the plugin and set NAME, HOST, USER and PASSWD for your mFi Power devices|color=red")
    print("file: " + os.path.abspath(__file__) + "|color=red")
    sys.exit(1)

def make_call(prog, *args):
    res = []
    res.append('bash="{0}"'.format(prog))
    for i, arg in enumerate(args):
        res.append('param{0}="{1}"'.format(i + 1, arg))
    return " ".join(res)

def main(device=None, action=None):
    parser = argparse.ArgumentParser(description='mFi Power devices')
    parser.add_argument('--data', help='JSON B64 encoded data')

    args = parser.parse_args()

    try:
        mFi = mFiPower(MFIPDEVS)
    except Exception as e:
        print(str(e))
        sys.exit(1)

    if args.data is not None:
        data = json.loads(base64.decodestring(urllib.unquote(args.data)))
        device = mFi.getDevice(data['devicename'])
        if device is not None:
            if data['action'] == "on":
                device.turnOnSocket(data['socket'])
            elif data['action'] == "off":
                device.turnOffSocket(data['socket'])
            device.update(force=True)

    sockets_on = []
    sockets_off = []
    total_power = 0

    for device in mFi.getDeviceList():
        for socketname in sorted(device.getSocketList(), key=lambda a: a):
            socket = device.getSocketData(socketname)
            power = socket['power']
            if socket['output'] == 0:
                sockets_off.append([device, socketname])
            else:
                sockets_on.append([device, socketname])
                total_power += power

    if sockets_on:
        print("%d On (%d W)| color=red" % (len(sockets_on), total_power))
    else:
        print("All Off| color=green")
    print("---")
    for device in mFi.getDeviceList():
        if device.getStatus() != 'OK':
            print("Device %s: %s| color=red" %(device.getName(), device.getStatus()))
    for (device, socket) in sockets_on:
        text = ":full_moon: {1} @ {0} is using {2:.2f} W (ON)".format(device.getName(), socket, device.getSocketData(socket)['power'])
        data = {
            'devicename': device.getName(),
            'socket': socket,
            'action': "off",
        }
        action = make_call(sys.argv[0], "--data", "%s" %(urllib.quote(base64.encodestring(json.dumps(data)))))
        print("%s|%s terminal=false refresh=true" % (text, action))
    for (device, socket) in sockets_off:
        text = ":new_moon: {1} @ {0} (OFF)".format(device.getName(), socket)
        data = {
            'devicename': device.getName(),
            'socket': socket,
            'action': "on",
        }
        action = make_call(sys.argv[0], "--data", "%s" %(urllib.quote(base64.encodestring(json.dumps(data)))))
        print("%s|%s terminal=false refresh=true" % (text, action))
    mFi.logOutAll()    

if __name__ == '__main__':
    main()
