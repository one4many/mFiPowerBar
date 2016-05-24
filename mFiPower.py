#!/usr/bin/env python

# Small mFi Power helper module
# Feel free to extend, but feed back to me any changes, bugfixes and enhancements

import requests
import time
from random import randint

def gGET(url, cookie, allow_redirects = True):
    cookies = {}
    if cookie:
        cookies['AIROS_SESSIONID'] = '%s' %(cookie)
    r = requests.get(url, cookies=cookies, allow_redirects=allow_redirects)
    if r.status_code == 200:
        return r.json()
    return None

def gPUT(url, payload, cookie=None, json=True):
    headers = {}
    cookies = {}
    headers['content-type'] = 'application/x-www-form-urlencoded'
    if cookie:
        cookies['AIROS_SESSIONID'] = '%s' %(cookie)
    r = requests.put(url, data=payload, headers=headers, cookies=cookies)
    if r.status_code == 200:
        if json:
            return r.json()
        else:
            return r.text
    return None
 
def gPOST(url, payload, cookie=None, json=True, debug=False):
    headers = {}
    cookies = {}
    headers['content-type'] = 'application/x-www-form-urlencoded'
    if cookie:
        cookies['AIROS_SESSIONID'] = '%s' %(cookie)
    r = requests.post(url, data=payload, headers=headers, cookies=cookies)
    if debug:
        print '----- DEBUG: %s %s ----' %(url,payload)
        print 'status code:', r.status_code
        print 'text:', r.text
        print '----- END DEBUG ----'
    if r.status_code == 200:
        if json:
            return r.json()
        else:
            return r.text
    return None

class mFiPowerDevice:
    def __init__(self, name, host, user, passwd):
        self.name = name
        self.user = user
        self.passwd = passwd
        self.url = 'http://%s' %(host)
        self.cookie = None
        self.sensors = {}
        self.sockets = {}
        self.lastUpdate = float(0)
        self.update(force = True)

    def login(self):
        c = randint(10**31, (10**32)-1)
        r = gPOST('%s/login.cgi' %(self.url), 'username=%s&password=%s' %(self.user, self.passwd), c, json=False, debug=False)
        if r:
            self.cookie = c
            return True
        return False

    def logout(self):
        if self.cookie:
            r = gGET('%s/logout.cgi' %(self.url), self.cookie, allow_redirects=False)
            if r:
                return True
        return False

    def update(self, force = False):
        if self.lastUpdate-time.time() < 60:
            if not force:
                return True
        if not self.cookie:
            self.login()
        r = gGET('%s/sensors' %(self.url), self.cookie)
        if r and 'success' in r['status']:
            self.sensors = r['sensors']
            self.lastUpdate = time.time()
            self.sensorStatus()
            return True
        self.sensors = {}
        self.lastUpdate = time.time()
        return False

    def sensorStatus(self):
        for sensor in self.sensors:
            if 'label' in sensor:
                self.sockets[sensor['label']] = {'label': sensor['label'], 'port': sensor['port'], 'output': sensor['output'], 'power': sensor['power'] }

    def getName(self):
        return self.name

    def getSocketList(self):
        return self.sockets.keys()

    def getSocketData(self, socket):
        if socket in self.sockets:
            return self.sockets[socket]
        return {}

    def turnOnSocket(self, socket):
        if socket in self.sockets:
            r = gPUT('%s/sensors/%s' %(self.url, self.sockets[socket]['port']), 'output=1', self.cookie)
            if r and 'success' in r['status']:
                return True            
        return False

    def turnOffSocket(self, socket):
        if socket in self.sockets:
            r = gPUT('%s/sensors/%s' %(self.url, self.sockets[socket]['port']), 'output=0', self.cookie)
            if r and 'success' in r['status']:
                return True            
        return False

class mFiPower:
    def __init__(self, config = []):
        self.config = config
        self.devices = {}
        for conf in config:
            td = self._addDevice(conf['NAME'], conf['HOST'], conf['USER'], conf['PASSWD'])
            if td:
                self.devices[conf['NAME']] = td

    def _addDevice(self, name, host, user, passwd):
        try:
            dev = mFiPowerDevice(name, host, user, passwd)
        except:
            import traceback
            print traceback.format_exc()
            dev = None
        return dev

    def getDeviceList(self):
        d = []
        for device in self.devices:
            d.append(self.devices[device])
        return d

    def getDeviceNameList(self):
        return self.devices

    def printDeviceStatus(self, name):
        if name in self.devices:
            print self.devices[name].update(force = True)
            print self.devices[name].sensorStatus()

    def getDevice(self, device):
        if device in self.devices:
            return self.devices[device]
        return None

    def logOutAll(self):
        for device in self.devices:
            return self.devices[device].logout()
    
def main():
    # Main is for dev and testing purposes only
    MFIPDEVS = [
        { 'NAME': 'hexa', 'HOST': '172.16.1.10', 'USER': 'ubnt', 'PASSWD': 'notrAndom42!' },
    ]
    mFiP = mFiPower(MFIPDEVS)
    hexa = mFiP.getDevice('hexa')
    hexsoc = hexa.getSocketList()
    for i in hexsoc:
        print i, hexa.getSocketData(i)
        print hexa.turnOnSocket(i)
        time.sleep(10)
        print hexa.turnOffSocket(i)
    mFiP.logOutAll()

if __name__ == '__main__':
    main()
