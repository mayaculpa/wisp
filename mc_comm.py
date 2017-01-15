# -*- coding: utf-8 -*-
#!/usr/bin/env python

# HAPI Master Controller v1.0
# Author: Tyler Reed
# Release: June 2016 Alpha
#*********************************************************************
#Copyright 2016 Maya Culpa, LLC
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
#*********************************************************************

import telnetlib
import time
import serial
import logging

class MCCommunicator(object):
    def __init__(self):
        pass

    def send_to_mc(self, address, port, timeout, command):
        logger = logging.getLogger('shop_log')
        try:
            connection = telnetlib.Telnet()
            #connection.open(address, port, 5)
            connection.open(address, port)
            command = command.encode('utf-8')
            print "Sending", command, "to Master Controller", "at", address, ":", port, timeout
            connection.write(command.strip() + "\n")
            time.sleep(0.25)
            response = connection.read_until("\n")
            print "Response received:", response
            time.sleep(0.25)
            connection.write("logout" + "\n")
            #time.sleep(0.25)
            connection.close()
        except Exception, excpt:
            logger.exception('mc_comm::send_to_mc: Error communicating with Master Controller: %s', excpt) # or pass an error message, see comment

        return response
