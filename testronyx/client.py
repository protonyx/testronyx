import requests
import threading
import logging
import time
from app.lib.jsonrpc import *


class RpcClient(object):
    """
    Establishes a TCP connection to the server through which all requests are
    send and responses are received. This is a blocking operation, so only one
    request can be sent at a time.

    :param uri:     HTTP URI
    :type uri:      str
    :param timeout: Request timeout (seconds)
    :type timeout:  float
    :param logger:  Logging instance
    :type logger:   logging.Logger object
    """

    DEFAULT_TIMEOUT = 10.0
    RETRY_ATTEMPTS = 3
    RPC_MAX_PACKET_SIZE = 1048576 # 1MB

    CLIENT_HEADERS = {
        'user-agent': 'TESTRONYX-RPC/1.0.0'
    }

    def __init__(self, uri, **kwargs):

        self.uri = uri
        self.timeout = kwargs.get('timeout', self.DEFAULT_TIMEOUT)
        self.logger = kwargs.get('logger', logging)

        # Decode URI
        import urllib
        self.uri_type, uri = urllib.splittype(uri)
        host, self.path = urllib.splithost(uri)

        if ':' in host:
            self.host, self.port = host.split(':')
        else:
            self.host = host

        # Encode/Decode Engine, jsonrpc is the default
        self.engine = {
            encode: encode,
            decode: decode
        }

        self._reqSession = requests.session()
        # Disable proxy settings from the host
        self._reqSession.trust_env = False

        self.rpc_lock = threading.Lock()

        self.methods = []

    def _handleException(self, exception_object):
        """
        Subclass hook to handle exceptions raised during RPC calls

        :param exception_object: Exception object
        """
        # Try to decode server exceptions
        if isinstance(exception_object, RpcServerException):
            exc_type, exc_msg = exception_object.message.split('|')

            import exceptions
            if hasattr(exceptions, exc_type):
                raise getattr(exceptions, exc_type)(exc_msg)
            else:
                raise exception_object

        else:
            raise exception_object

    def _getMethods(self):
        resp_data = self.__sendGetRequest()

        return json.loads(resp_data).get('methods')

    @staticmethod
    def __getNextId():
        next_id = 0

        while 1:
            next_id += 1
            yield next_id

    def __sendGetRequest(self):
        resp_data = self._reqSession.get(self.uri, headers=self.CLIENT_HEADERS, timeout=self.timeout)

        return resp_data.text

    def __sendPostRequest(self, rpc_request):
        for attempt in range(1, self.RETRY_ATTEMPTS + 1):
            try:
                # Encode the RPC Request
                data = self.engine.encode([rpc_request], [])

                # Send the encoded request
                with self.rpc_lock:
                    resp_data = self._reqSession.post(self.uri, data, headers=self.CLIENT_HEADERS, timeout=self.timeout)

                # Check status code
                if resp_data.status_code is not 200:
                    raise RpcError("Server returned error code: %d" % resp_data.status_code)

                return resp_data.text

            except requests.ConnectionError:
                if attempt == self.RETRY_ATTEMPTS:
                    raise RpcServerNotFound()
                else:
                    time.sleep(0.5)

            except requests.Timeout:
                raise RpcTimeout()

    def __decodeResponse(self, data):
        rpc_requests, rpc_responses, rpc_errors = self.engine.decode(data)

        if len(rpc_errors) > 0:
            # There is a problem if there are more than one errors,
            # so just check the first one
            recv_error = rpc_errors[0]
            if isinstance(recv_error, RpcMethodNotFound):
                raise AttributeError()
            else:
                # Call the exception handling hook
                try:
                    self._handleException(recv_error)
                except NotImplementedError:
                    raise recv_error

        elif len(rpc_responses) == 1:
            resp = rpc_responses[0]
            return resp.result

        else:
            raise RpcInvalidPacket("An incorrectly formatted packet was received")

    def _rpcCall(self, remote_method, *args, **kwargs):
        """
        Calls a function on the remote host with both positional and keyword
        arguments

        Exceptions:
        :raises AttributeError: when method not found (same as if a local call)
        :raises RuntimeError: when the remote host sent back a server error
        :raises RpcTimeout: when the request times out
        """
        req = RpcRequest(method=remote_method, args=args, kwargs=kwargs, id=self.__getNextId().next())

        # Decode the returned data
        data = self.__sendPostRequest(req)

        return self.__decodeResponse(data)

    def _rpcNotify(self, remote_method, *args, **kwargs):
        req = RpcRequest(method=remote_method, args=args, kwargs=kwargs)

        self.__sendPostRequest(req)

    def __str__(self):
        return '<RPC @ %s>' % (self.uri)

    class _RpcMethod(object):
        """
        RPC Method generator to bind a method call to an RPC server. Supports nested calls

        Based on xmlrpclib
        """

        def __init__(self, rpc_call, method_name):
            self.__rpc_call = rpc_call
            self.__method_name = method_name

        def __getattr__(self, name):
            # supports "nested" methods (e.g. examples.getStateName)
            return self._RpcMethod(self.__rpc_call, "%s.%s" % (self.__method_name, name))

        def __call__(self, *args, **kwargs):
            return self.__rpc_call(self.__method_name, *args, **kwargs)

    def __getattr__(self, name):
        return self._RpcMethod(self._rpcCall, name)