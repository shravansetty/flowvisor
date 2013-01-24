#!/usr/bin/env python
# Copyright (c) 2012-2013  The Board of Trustees of The Leland Stanford Junior University

import urllib2, urlparse, sys, getpass, functools, json
from optparse import OptionParser

def getPassword(opts):
    if opts.fv_passwdfile is None:
        passwd = getpass.getpass("Password: ")
    else:
        passwd = open(opts.fv_passwdfile, "r").read().strip()
    return passwd

def addCommonOpts (parser):
    parser.add_option("-n", "--hostname", dest="host", default="localhost")
    parser.add_option("-p", "--port", dest="port", default="8080")
    parser.add_option("--user", dest="fv_user", default="fvadmin")
    parser.add_option("--passwd-file", dest="fv_passwdfile", default=None)

def getUrl(opts):
    return URL % (opts.host, opts.port)#(opts.fv_user, getPassword(opts), opts.host, opts.port)

def buildRequest(data, url, cmd):
    j = { "id" : "fvctl", "method" : cmd, "jsonrpc" : "2.0" }
    h = {"Content-Type" : "application/json"}    
    if data is not None:
        j['params'] = data
    return urllib2.Request(url, json.dumps(j), h)

def getError(code):
    try:
        return ERRORS[code]
    except Exception, e:
        return "Unknown Error"
     

def pa_none(args):
    parser = OptionParser()
    addCommonOpts(parser)
    (options, args) = parser.parse_args(args)
    return options

def do_listSlices(opts):
    data = connect(opts, "list-slices")
    print data
    

def connect(opts, cmd, data=None):
    try:
        url = getUrl(opts)
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url,opts.fv_user, getPassword(opts))
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)

        req = buildRequest(data, url, cmd)
        ph = opener.open(req)
        return parseResponse(ph.read())
    except urllib2.HTTPError, e:
        if e.code == 401:
            print "Authentication failed: invalid password"
            sys.exit(1)
        elif e.code == 504:
            print "HTTP Error 504: Gateway timeout"
            sys.exit(1)
        else:
            print e
    except RuntimeError, e:
        print e

def parseResponse(data):
    j = json.loads(data)
    if 'error' in j:
        print "%s : %s" % (getError(j['error']['code']),j['error']['msg'])
        sys.exit(1)
    return j['result']



CMDS = {
    'list-slices' : (pa_none, do_listSlices)
#    'add-slice' : (pa_addSlice, do_addSlice),
#    'update-slice' : (pa_updateSlice, do_updateSlice),
#    'remove-slice' : (pa_removeSlice_parse_aergs, do_removeSlice),
#    'update-slice-password' : (pa_updateSlicePassword, do_updateSlicePassword),
#    'update-admin-password' : (pa_updateAdminPassword, do_updateAdminPassword),
#    'list-flowspace' : (pa_listFlowSpace, do_listFlowSpace),
#    'add-flowspace' : (pa_addFlowSpace, do_addFlowSpace),
#    'update-flowspace' : (pa_updateFlowSpace, do_updateFlowSpace),
#    'remove-flowspace' : (pa_removeFlowSpace, do_removeFlowSpace),
#    'list-version' : (pa_none, do_listVersion),
#    'save-config' : (pa_none, do_saveConfig),
#    'get-config' : (pa_getConfig, do_getConfig),
#    'set-config' : (pa_setConfig, do_setConfig),
#    'list-slice-info' : (pa_listSliceInfo, do_listSliceInfo),
#    'list-datapaths' : (pa_none, do_listDatapaths),
#    'list-datapath-info' : (pa_listDatapathInfo, do_listDatapathInfo),
#    'list-datapath-stats' : (pa_listDatapathStats, do_listDatapathStats),
#    'list-fv-health' : (pa_none, do_listFVHealth),
#    'list-links' : (pa_none, do_listLinks),
#    'list-slice-health' : (pa_listSliceHealth, do_listSliceHealth),
#    'list-slice-stats' : (pa_listSliceStats, do_listSliceStats)
}

ERRORS = {
    -32700 : "Parse Error",
    -32600 : "Invalid Request",
    -32601 : "Method not found",
    -32602 : "Invalid Params",
    -32603 : "Internal Error"
}

URL = "https://%s:%s"

if __name__ == '__main__':
  try:
    if sys.argv[1] == "--help":
      raise IndexError
    (parse_args, do_func) = CMDS[sys.argv[1]]
    opts = parse_args(sys.argv[2:])
    do_func(opts)
  except KeyError, e:
    print "'%s' is not a valid command" % (sys.argv[1])
  except IndexError, e:
    print "Valid commands are:"
    cmds = [x for x in CMDS.iterkeys()]
    cmds.sort()
    for x in cmds:
      print x

