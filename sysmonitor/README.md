# blink(1) System Monitor

This provides a service to monitor system information and set the color on a 
blink(1) accordingly.  Currently only a systemd style service file is provided. 
A config file needs to be specified on the command line.

## Required Packages

 * [PyUSB](http://sourceforge.net/projects/pyusb/)
 * [psutil](http://code.google.com/p/psutil/)

## Config File Options
### Required Options:
 * __pid_file__ path to write the pid file to
### Optional Options:
 * __setuid__ UID to use for dropping privileges
 * __setgid__ GID to use for dropping privileges
