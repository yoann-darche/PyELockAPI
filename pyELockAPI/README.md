
pyELockAPI Lib - A simple API to interface Python with the ELock card from Elektor (April 2014)
===============================================================================================

This module include ELock object that permit to initiate a secure communication between the python script and the
ELock card. So basic function has been added to get the temperature value, or set the relay state.

How to install:
---------------

   python setup.py install

How to use :
------------

    Before using you need to have the appropriate certificate and key. In the following code we make assumption that you
    have the following files :

      * ISLclient-cert.pem : TLS Client certificate
      * ISLclient-key.pem  : Client KEY
      * cacert.pem         : CA Certificate

      Please see the following documentation (Config Elock - Detailed steps.pdf) for more information on How to
      generate and setup these certificates.



Licence:
--------

        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2015 Yoann Darche <yoann d AT hot mail DOT com>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
