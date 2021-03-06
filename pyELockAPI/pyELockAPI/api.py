# -*- coding: utf-8 -*-

# pyELockAPI.api: The Elektor E-Lock card API interface
#
# Copyright (C) 2015 Yoann Darche <yoannd AT hotmail DOT com>
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#
# ELock card has been presented in the Elektor Magazine in April 2014
# More detail here :
#       http://www.elektor-labs.com/project/elektor-chip-e-lock-reference-project-130499130280.13916.html
#   and http://www.elektor.com/130280-91

__author__ = 'Yoann Darche'

import socket
import ssl


# Limit the scanning options
__all__ = ['PyELockMsg', 'PyELock']

# Command constants
PYELOCK_CMD_RD_EXTDEV       = 0x00
PYELOCK_CMD_WR_EXTDEV       = 0x01

PYELOCK_CMD_GET_CFG_EXTDEV  = 0x10
PYELOCK_CMD_SET_CFG_EXTDEV  = 0x10


PYELOCK_CMD_SET_CFG_SENSOR  = 0x90
PYELOCK_CMD_SET_CFG_RELAY   = 0x92
PYELOCK_CMD_GET_CFG_SENSOR  = 0x94
PYELOCK_CMD_RD_SENSOR       = 0x98
PYELOCK_CMD_RD_RELAY        = 0x9A
PYELOCK_CMD_WR_RELAY        = 0x9C

PYELOCK_CMD_SYS_GETVER      = 0xB0
PYELOCK_CMD_SYS_SET_CFG     = 0xD0

# Device constants
PYELOCK_DEV_GPI             = 0x01
PYELOCK_DEV_GPO             = 0x02
PYELOCK_DEV_GPIO            = 0x03
PYELOCK_DEV_ADC             = 0x04
PYELOCK_DEV_I2C             = 0x08
PYELOCK_DEV_DAC             = 0x10
PYELOCK_DEV_ETH             = 0x80

PYELOCK_DEV_NODEVICE        = 0xFF

# Device alias
PYELOCK_DEVTYPE_RELAY       = PYELOCK_DEV_GPO
PYELOCK_DEVTYPE_TEMP_SENSOR = PYELOCK_DEV_I2C

# Device number constants
PYELOCK_DEVNUM_RELAY1       = 0x01
PYELOCK_DEVNUM_RELAY2       = 0x02

PYELOCK_DEVNUM_TEMP_SENSOR  = 0x01

PYELOCK_DEVNUM_ADC1         = 0x01
PYELOCK_DEVNUM_ADC2         = 0x02
PYELOCK_DEVNUM_ADC3         = 0x04
PYELOCK_DEVNUM_ADC4         = 0x08

PYELOCK_DEVNUM_DAC0         = 0x01

PYELOCK_DEVNUM_I2C          = 0x02

PYELOCK_DEVNUM_GPIO0        = 0x01
PYELOCK_DEVNUM_GPIO1        = 0x02
PYELOCK_DEVNUM_GPIO2        = 0x04
PYELOCK_DEVNUM_GPIO3        = 0x08
PYELOCK_DEVNUM_GPIO4        = 0x10
PYELOCK_DEVNUM_GPIO5        = 0x20
PYELOCK_DEVNUM_GPIO6        = 0x40



class PyELockMsg:
    """
    This class handle coding and decoding a ELock bytes message
    """
    RawMsg = None
    Size = 8
    RetCode = 0
    Cmd = 0
    DevType = PYELOCK_DEV_NODEVICE
    NumDev = 0
    ExtMsg = None


    def __init__(self, Cmd=0, DevType=PYELOCK_DEV_NODEVICE, NumDev=0, raw=None):

        if raw is None:
            self.Cmd = Cmd
            self.DevType = DevType
            self.NumDev = NumDev
            self.encode()
        else:
            self.RawMsg = raw
            self.decode()


    def __repr__(self):

        return "<<PyELockMsg: Len {0}[{0:#x}], [{1:#x}]{2}, CMD={3:#x}, DEV.TYPE={4:#x}, NUM.DEV={5:#x} DATA={6}>>".format(self.Size,
                                        self.RetCode, self.getRetCodeStr(), self.Cmd, self.DevType, self.NumDev, self.ExtMsg)

    def __str__(self):

        msg =       "PyElockMsg   : Len[{0:#x}]({0}) Status[{1:#x}]:{2}\n".format(self.Size, self.RetCode, self.getRetCodeStr())
        msg = msg + "   Cmd       : {0:#x}\n".format(self.Cmd)
        msg = msg + "   DEV.TYPE  : [0x{1:02x}] {0:08b}\n".format(self.DevType, self.DevType)
        msg = msg + "   NUM.DEVICE: [0x{1:04x}] {0:032b}\n".format(self.NumDev, self.NumDev)

        #if not(self.ExtMsg is None):
        #    msg = msg + "   Extent Raw Data:\n"
        #    for l in self.ExtMsg.split(b'\x00'):
        #        msg = msg + " >> " + str(l) + "\n"

        msg = msg + "   Extent Raw Data:\n{0}".format(self.ExtMsg)

        return msg

    def __len__(self):
        return self.Size

    def __bytes__(self):
        return self.RawMsg

    def __bool__(self):
        return self.RetCode == 0x00

    def encode(self):

        # Generating the Header
        t = bytearray([0, 0x00, self.Cmd & 0x0FF, self.DevType & 0x0FF, self.NumDev & 0x0FF000000, self.NumDev & 0x0FF0000, self.NumDev & 0x0FF00, self.NumDev & 0x0FF])

        # if any Extended data exist, add them to the message
        if self.ExtMsg is not None:
            self.RawMsg = t + self.ExtMsg
        else:
            self.RawMsg = t

        self.Size = len(self.RawMsg)
        self.RawMsg[0] = self.Size


    def decode(self):

        self.Size = self.RawMsg[0]
        self.RetCode = self.RawMsg[1]
        self.Cmd = self.RawMsg[2]
        self.DevType = self.RawMsg[3]
        self.NumDev = (self.RawMsg[4] << 24) + (self.RawMsg[5] << 16) + (self.RawMsg[6] << 8) + self.RawMsg[7]


        if self.Size > 8:
            self.ExtMsg = self.RawMsg[8:]
        else:
            self.ExtMsg = None

    def setxdata(self, data):
        """
        This function permit to add Data to the message, generally required to configure, set the state etc..
        :param data: bytearray containning extended data
        :return: True/False
        """

        if type(data) == bytearray:
            self.ExtMsg = data
            self.encode()
        else:
            raise TypeError('Bad type passed to PyELockMsg:setxdata')
            return False

        return True



    def getbytearray(self):
        return self.RawMsg

    def getRetCodeStr(self):

        if self.RetCode == 0:
            return "Success"

        # Generic error code
        elif self.RetCode == 0x80:
            return "ELock:Gen Frame error"
        elif self.RetCode == 0x81:
            return "ELock:Gen Command error"
        elif self.RetCode == 0x82:
            return "ELock:Gen Device type error"
        elif self.RetCode == 0x83:
            return "ELock:Gen Device number error"
        elif self.RetCode == 0x84:
            return "ELock:Gen Data error"
        elif self.RetCode == 0xFF:
            return "ELock:Gen Internal operation error"

        # I2C sensor code
        elif self.RetCode == 0x90:
            return "ELock:I2C Baud rate error"
        elif self.RetCode == 0x91:
            return "ELock:I2C Mode error"
        elif self.RetCode == 0x92:
            return "ELock:I2C Station address error"
        elif self.RetCode == 0x93:
            return "ELock:I2C Device address error"
        elif self.RetCode == 0x94:
            return "ELock:I2C No device on bus"
        elif self.RetCode == 0x95:
            return "ELock:I2C NACK reply"

        # ADC error code
        elif self.RetCode == 0xA0:
            return "ELock:ADC busy"
        elif self.RetCode == 0xA1:
            return "ELock:ADC ADC not complete conversion"

        return "PyELock : Unknown error"


class PyELock:

    _host = None
    _port = 2013
    _TLSKeyFile = None
    _TLSCertFile = None
    cnx = None
    _setTempCfg = False


    def __init__(self, host, port=None, TLSClientKeyFile=None, TLSClientCertFile=None, TLSCaCert=None):
        self._host = host
        if port is not None:
            self._port = port

        self._TLSCertFile= TLSClientCertFile
        self._TLSKeyFile = TLSClientKeyFile
        self._TLSCaCert  = TLSCaCert


    def connect(self):


        # Primary check
        if self._TLSKeyFile is None or self._TLSCertFile is None:
            return -1

        sck = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        addr = (self._host, self._port)

        # perform the connexion
        sck.connect(addr)

        # add the TLS layer
        self.cnx = ssl.wrap_socket(sck,  keyfile=self._TLSKeyFile, certfile=self._TLSCertFile, cert_reqs=ssl.CERT_OPTIONAL,
                                   ssl_version=ssl.PROTOCOL_TLSv1_2, ca_certs=self._TLSCaCert)

    def disconnect(self):

        if self.cnx is None:
            return False

        self.cnx.shutdown(socket.SHUT_RDWR)
        self.cnx.close()

        self.cnx = None
        self._setTempCfg = False

        return True

    def _readAnswer(self):

        if self.cnx is None:
            raise ConnectionError("PyELock::_readAnswer: Not connected to ELock card !")

        # get the len of the answer
        len = self.cnx.recv(1)

        # read the answer
        return PyELockMsg(raw=bytearray([len[0]] + list(self.cnx.recv(len[0]-1))))



    def getVersion(self):

        if self.cnx is None:
            raise ConnectionError("PyELock::getVersion: Not connected to ELock card !")

        msg = PyELockMsg(PYELOCK_CMD_SYS_GETVER, PYELOCK_DEV_NODEVICE, 0x00)

        print("Sended message : ", msg)

        #self.cnx.send(bytes(msg))
        self.cnx.send(msg.getbytearray())
        return self._readAnswer()


    def setRelays(self, relay1=None, relay2=None):

        # Check validity of parameters and connexion is up
        if (self.cnx is None) or ((self.cnx is None) and (self.cnx is None)):
            return False

        devnum = 0x00

        if relay1 is not None:
            devnum = PYELOCK_DEVNUM_RELAY1

        if relay2 is not None:
            devnum |= PYELOCK_DEVNUM_RELAY2

        msg = PyELockMsg(PYELOCK_CMD_WR_RELAY, PYELOCK_DEVTYPE_RELAY, devnum)

        if relay1 != 0:
            val = 0x01

        if relay2 != 0:
            val |= 0x02

        val = bytearray([0x0, 0x0, 0x0, val])
        msg.setxdata(val)

        # print("Sended message : ", msg)
        self.cnx.send(msg.getbytearray())

        return self._readAnswer()



    def setTempCfg(self, sample_periode=1, hyst1=None, hyst2=None):
        """
        Set the configuration for Temperature sensor (Sample rate, Hysteresis}
        Should be call at least one time before using getTempVal()

        :param sample_periode: Period to scan the value of the temperature sensor 1 (s) - 86400 (24h)
        :param hyst1: Hysteresis on Relay 1 { Low: <value>, 'High': <value>, 'Action': 0 (On) | 1 (Off) }
        :param hyst2: Hysteresis on Relay 2 { Low: <value>, 'High': <value>, 'Action': 0 (On) | 1 (Off) }
                <value> should be between -40 and 100 (°c)
        :return: answer: PyELockMsg
        """


        def __MakeHyst(v):

            r = int(v['High']).to_bytes(4, 'big', signed=True)
            r += int(v['Low']).to_bytes(4, 'big', signed=True)
            r += int(v['Action']).to_bytes(1, 'big', signed=False)
            r += bytearray([0x0, 0x0, 0x0])
            return(r)



        if self.cnx is None:
            raise ConnectionError("PyELock::setTempCfg: Not connected to ELock card !")

        msg = PyELockMsg(PYELOCK_CMD_SET_CFG_SENSOR, PYELOCK_DEVTYPE_TEMP_SENSOR, PYELOCK_DEVNUM_TEMP_SENSOR)
        ext = bytearray([0x01, 0x00, 0x00, 0x00]) # Type = Temperature, 3 bytes reserved
        ext += sample_periode.to_bytes(4, 'big', signed=False)

        print(ext)

        if hyst1 is None:
            ext += int(0).to_bytes(12, 'big')
        else:
            ext += __MakeHyst(hyst1)

        if hyst2 is None:
            ext += int(0).to_bytes(12, 'big')
        else:
            ext += __MakeHyst(hyst2)

        msg.setxdata(ext)

        #print('Setup Temperature Msg:',msg)

        self._setTempCfg = True

        self.cnx.send(msg.getbytearray())

        return self._readAnswer()


    def getTempVal(self):

        if self.cnx is None:
            raise ConnectionError("PyELock::getTempVal: Not connected to ELock card !")

        # if the temperature sensor is not yet configured, set default configuration
        if not self._setTempCfg:
            self.setTempCfg(1, None, None)

        msg = PyELockMsg(PYELOCK_CMD_RD_SENSOR, PYELOCK_DEVTYPE_TEMP_SENSOR, PYELOCK_DEVNUM_TEMP_SENSOR)


        self.cnx.send(msg.getbytearray())

        ret = self._readAnswer()

        # make conversion if we get a result, other wise None
        if ret:
            return int.from_bytes(ret.ExtMsg, 'big', signed=True)
        else:
            return None
