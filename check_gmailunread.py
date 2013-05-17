#!/usr/bin/env python
import imaplib,getopt,sys

#
#    Copyright 2012 Peter Dyson <peter.dyson@geekpete.com>
#    https://github.com/geekpete/nagiosplugins/ 
#
#    Licensed under the GNU General Public License Version 3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
#
# check_gmailunread.py
# Nagios plugin to check number of unread emails in a gmail account
#
# This script logs into a given gmail account and counts the unread emails.
# It will then alert based on the WARN and CRITICAL thresholds.
#
################################################################################

### Define required nagios script settings.

# define script name.
scriptName=sys.argv[0] 

# define script version.
scriptVersion = "v0.1.0"

# Nagios plugin exit codes
STATE_OK       = 0
STATE_WARNING  = 1
STATE_CRITICAL = 2
STATE_UNKNOWN  = 3

# Clear default variable states
nagiosState = ""
gmailUser = ""
gmailPassword = ""

#####

class Usage(Exception):
    def __init__(self, err):
        self.msg = err

def usage():
    print "Usage: check_gmailunread.py -u email_user -p email_password -w warn_unread -c crit_unread"
    print "       check_gmailunread.py -h for detailed help"
    print "       check_gmailunread.py -V for version information"

def detailedUsage():
    print "Nagios plugin to check how many unread emails are in a gmail account"
    print 
    usage()
    print 
    print "Options:"
    print "  -h"
    print "     Print this help message."
    print "  -V"
    print "     Print version information then exit."
    print "  -u gmail_user"
    print "     User name of the gmail account."
    print "     For google enterprise accounts use the full email address:"
    print "     eg, your.email@yourcompany.com"
    print "  -p gmail_password "
    print "     Password of the gmail account."
    print "  -w warn_count" 
    print "     Warning threshold count for unread emails."
    print "  -c crit_count"
    print "     Critical threshold count for unread emails."
    print 


# parse the command line switches and arguments
try:
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hVH:u:p:w:c:v", ["help", "output="])
    except getopt.GetoptError, err:
        # print help information and exit:
        raise Usage(err)
except Usage, err:
    print >>sys.stderr, err.msg
    usage()
    sys.exit(STATE_UNKNOWN)


# gather values from given parameter switches
for o, a in opts:
        if o == "-w":
            unreadWARNING = int(a)
        elif o == "-c":
            unreadCRITICAL = int(a)
        elif o == "-u":
            gmailUser = a
        elif o == "-p":
            gmailPassword = a
        elif o in ("-V","-v","--version"):
            print scriptName + " " + scriptVersion
            usage()
            sys.exit()
        elif o in ("-h", "--help"):
            detailedUsage()
            sys.exit()
        else:
            assert False, "unhandled option"

# Check to see if a host has been specified, throw an error if not.
if gmailUser=="":
    print "Error: no gmail user specified."
    usage()
    sys.exit()
elif gmailPassword=="":
	print "Error: no gmail password specified."
	usage()
	sys.exit()
elif unreadWARNING=="":
	print "Error: no unread WARNING threshhold specified."
	usage()
	sys.exit()
elif unreadCRITICAL=="":
	print "Error: no unread CRITICAL threshold specified."
	usage()
	sys.exit()


# open an SSL imap4 connection to gmail, fail if unsuccessful
try:
    # Open imap4 conection to imap.gmail.com.
	gmailconnection = imaplib.IMAP4_SSL('imap.gmail.com',993)

except Exception:
    print "UNKNOWN: error connecting to imap.gmail.com on tcp port 993"
    sys.exit(3)

# try to use the gmail login on the newly opened imap connection, fail if unsuccessful
try:
    # log in with gmail account and password
	gmailconnection.login(gmailUser,gmailPassword)

except Exception:
    print "UKNOWN: error authenticating against opened gmail imap connection with provided credentials"
    sys.exit(3)

# attempt to count the unread emails for this gmail account now that we've logged in
try:
    # log in with gmail account and password
	gmailconnection.select()
	unreadEmailCount=int(len(gmailconnection.search(None, 'UnSeen')[1][0].split()))

except Exception:
    print "UKNOWN: error reading number of unread emails for gmail account %s" % gmailUser
    sys.exit(3)


# check the response time of the url
if unreadEmailCount >= unreadCRITICAL:
    checkResult="CRITICAL"
    nagiosState=STATE_CRITICAL
elif unreadEmailCount >= unreadWARNING:
    checkResult="WARNING"
    nagiosState=STATE_WARNING
else:
    # otherwise it's ok
    checkResult="OK"
    nagiosState=STATE_OK
    
# display output of the metrics and any warnings
print "Unread email count for %s is %d: %s" % (gmailUser, unreadEmailCount, checkResult)
sys.exit(nagiosState)
