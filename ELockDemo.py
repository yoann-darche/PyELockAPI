# -*- coding: utf-8 -*-

__author__ = 'daryo01'

import PyELockApi.pyELockAPI.api as el

if __name__ == "__main__":

    print("*******************************************************")
    print("*   Basic Test script V1.00 (cc) Yoann Darche 2015    *")
    print("*-----------------------------------------------------*")
    print("* The script expect to access to the following files: *")
    print("*  ./ISLclient-cert.pem : Client certificate          *")
    print("*  ./ISLclient-key.pem  : Client key                  *")
    print("*  ./cacert.pem         : CA certificate              *")
    print("*******************************************************\n\n")

    print("Creating the PyELock Object :")

    elock = el.PyELock('192.168.20.21',2013, TLSClientCertFile='./ISLclient-cert.pem', TLSClientKeyFile='./ISLclient-key.pem', TLSCaCert='./cacert.pem')

    print("Connecting to the ELock card....")
    elock.connect()

    print("Connected")

    v = (elock.getVersion())
    print(v)
    print(v.RawMsg)

    # input("Press enter to activate Relay 2")
    #print(elock.setRelays(None, 0))

    #input("Press enter to unactivate Relay 2")
    #print(elock.setRelays(None, 1))

    print("Temparture configuartion sesnsor")
    print(elock.setTempCfg(1, None, None))

    e = ''
    while e != 'q' and e != 'Q':
        print("Temperature : ", elock.getTempVal())
        e = input("(Q)uit ?")


    print("Disconnecting from ELock card...")
    elock.disconnect()

