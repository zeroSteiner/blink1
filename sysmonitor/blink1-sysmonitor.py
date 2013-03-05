#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (c) 2013, Spencer J. McIntyre
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  

import os
import sys
import usb.core
import psutil
import blink1

def service():
	blink1_device = None
	while True:
		while blink1_device == None:
			try:
				blink1_device = blink1.Blink1()
			except:
				blink1_device = None
		blink1_device.pattern_stop()
		blink1_device.off()
		while True:
			cpu_percentage = psutil.cpu_percent(interval = 2)
			if cpu_percentage >= 80:
				color = 'red'
			elif cpu_percentage >= 60:
				color = 'orange'
			elif cpu_percentage >= 40:
				color = 'yellow'
			else:
				color = 'green'
			try:
				blink1_device.set_color(color, fade = 0.5)
			except usb.core.USBError:
				blink1_device = None
				break

if __name__ == '__main__':
	pid = os.fork()
	if pid:
		pid_file = os.path.splitext(os.path.basename(sys.argv[0]))[0]
		pid_file = '/run/' + pid_file + '.pid'
		pid_file_h = open(pid_file, 'w')
		pid_file_h.write(str(pid))
		sys.exit(0)
	service()
