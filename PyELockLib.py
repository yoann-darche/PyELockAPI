__author__ = 'daryo01'

import socket
import ssl


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
        msg = msg + "   DEV.TYPE  : {0:08b} [0x{1:02x}]\n".format(self.DevType, self.DevType)
        msg = msg + "   NUM.DEVICE: {0:08b} [0x{1:02x}]\n".format(self.NumDev, self.NumDev)

        if not(self.ExtMsg is None):
            msg = msg + "   Extent Raw Data:\n"
            for l in self.ExtMsg.split(b'\x00'):
                msg = msg + " >> " + str(l) + "\n"

        return msg

    def __len__(self):
        return self.Size

    def __bytes__(self):
        return self.RawMsg

    def encode(self):

        msg = bytearray([0, 0x00, self.Cmd & 0x0FF, self.DevType & 0x0FF, self.NumDev & 0x0FF000000, self.NumDev & 0x0FF0000, self.NumDev & 0x0FF00, self.NumDev & 0x0FF])
        self.Size = len(msg)
        msg[0] = len(msg)

        self.RawMsg = bytearray(msg)

    def decode(self):

        self.Size = self.RawMsg[0]
        self.RetCode = self.RawMsg[1]
        self.Cmd = self.RawMsg[2]
        self.DevType = self.RawMsg[3]
        self.NumDev = self.RawMsg[7] << 24 + self.RawMsg[6] << 16 + self.RawMsg[5] << 8 + self.RawMsg[4]

        if self.Size > 8:
            self.ExtMsg = self.RawMsg[8:]
        else:
            self.ExtMsg = None

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



class PyELockRelayMsg(PyELockMsg):

      def __init__(self, Cmd=0, DevType=PYELOCK_DEV_NODEVICE, NumDev=0, raw=None):
        pass



class PyELock:

    _host = None
    _port = 2013
    _TLSKeyFile = None
    _TLSCertFile = None
    cnx = None
    _setTempCfg = False


    def __init__(self, host, port=None, TLSClientKeyFile=None, TLSClientCertFile=None):
        self._host = host
        if port is not None:
            self._port = port

        self._TLSCertFile= TLSClientCertFile
        self._TLSKeyFile = TLSClientKeyFile


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
                                   ssl_version=ssl.PROTOCOL_TLSv1_2, ca_certs='./cacert.pem')

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
            return None

        len = self.cnx.recv(1)

        return PyELockMsg(raw=bytearray([len[0]] + list(self.cnx.recv(len[0]-1))))



    def getVersion(self):

        if self.cnx is None:
            return False

        msg = PyELockMsg(PYELOCK_CMD_SYS_GETVER, PYELOCK_DEV_NODEVICE, 0x00)

        print("Sended message : ", msg)

        #self.cnx.send(bytes(msg))
        self.cnx.send(msg.getbytearray())
        return self._readAnswer()


    def setRelays(self, relay1=None, relay2=None):

        # Check validity of parameters and connexion is up
        if (self.cnx is None) or ((self.cnx is None) and (self.cnx is None)):
            return False

        devNum = 0x00

        if relay1 is not None:
            devNum = PYELOCK_DEVNUM_RELAY1

        if relay2 is not None:
            devNum |= PYELOCK_DEVNUM_RELAY2


        msg = PyELockMsg(PYELOCK_CMD_WR_RELAY, PYELOCK_DEVTYPE_RELAY, devNum)

        msg.addRelayState(val)


        print(self.cnx.send(msg))


        return True

    def setTempCfg(self):
        msg = bytearray([0,
                         0x00,  # ret code
                         0x90,  # cmd
                         0x08,  # DevType
                         0x01, 0x00, 0x00, 0x00, # Device
                         0x01,  # Type
                         0x00, 0x00, 0x00, # Rsv[3]
                         0x00, 0x00, 0x00, 0x00, # Sample Period
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, # hyst1
                         0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00  # hyst2
                         ])

        msg[0] = len(msg)

        if self.cnx is None:
            return False

        print(self.cnx.send(msg))

        self._setTempCfg = True


    def getTempVal(self):

        if self.cnx is None:
            return False

        if not self._setTempCfg:
            self.setTempCfg()

        msg = bytearray([0,
                         0x00,  # RetCode
                         0x98,  # cmd
                         0x08,  # Device Type (I2C)
                         0x01, 0x00, 0x00, 0x00 # Device
                         ])

        msg[0] = len(msg)

        if self.cnx.send(msg) == msg[0]:
            # read Client answer
            ret = self.cnx.recv(msg[0])

            if len(ret) > 0:
                for i in ret:
                    print(i)





# void set_relays(int relay1, int relay2)
# {
#     unsigned int Action = 0x00000000;
#     s_SetRelay TxSetRelay;
#
#     if (relay1!=0) Action |= 0x00000001;
#     if (relay2!=0) Action |= 0x00000002;
#
#     TxSetRelay.Nb = sizeof(s_SetRelay);
#     TxSetRelay.RetCode = 0x00;
#     TxSetRelay.Cmd = 0x9c;
#     TxSetRelay.DevType = 0x02;
#     TxSetRelay.Device = SWAP32(0x00000003);
#     TxSetRelay.Action = SWAP32(Action);
#
#     if (TcpClientSend((unsigned char *)&TxSetRelay,TxSetRelay.Nb)!=TCPCLIENT_OK)
#     {
#         printf("Set relay error.\n");
#     }
#
#     print_data((unsigned char *)&TxSetRelay,TxSetRelay.Nb,1);
# }



# Main Program entry

if __name__ == "__main__":


    print("Creating the PyELock Object :")

    elock = PyELock('192.168.20.21',2013, TLSClientCertFile='./ISLclient-cert.pem', TLSClientKeyFile='./ISLclient-key.pem')

    print("Connecting to the ELock card....")
    elock.connect()

    print("Connected")

    v = (elock.getVersion())
    print(v)
    print(v.RawMsg)

    #input("Press enter to activate Relay 2")

    #elock.setRelays(0, 1)

    #input("Press enter to unactivate Relay 2")

    #elock.setRelays(0, 0)


    elock.disconnect()

