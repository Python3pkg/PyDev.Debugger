import sys
IS_PY2 = sys.version_info < (3,)

import threading

import time

import socket

import select

if IS_PY2:
    import _thread
    import queue as _queue
    import xmlrpc.client
    import xmlrpc.server as _pydev_SimpleXMLRPCServer
    import http.server
else:
    import _thread as thread
    import queue as _queue
    import xmlrpc.client as xmlrpclib
    import xmlrpc.server as _pydev_SimpleXMLRPCServer
    import http.server as BaseHTTPServer