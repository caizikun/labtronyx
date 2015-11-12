import json
import logging
import threading

import requests
# Local imports
from . import errors

__all__ = ['RpcClient']


class RpcRequest(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.method = kwargs.get('method', '')
        self.args = kwargs.get('args', [])
        self.kwargs = kwargs.get('kwargs', {})

    def call(self, target):
        # Invoke target method with stored arguments
        # Don't attempt to catch exceptions here, let them bubble up
        return target(*self.args, **self.kwargs)


class RpcResponse(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.result = kwargs.get('result', None)


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
    RPC_MAX_PACKET_SIZE = 1048576 # 1MB

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
        from . import jsonrpc
        self.engine = jsonrpc

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
        if isinstance(exception_object, errors.RpcServerException):
            exc_type, exc_msg = exception_object.message.split('|')

            import exceptions
            if hasattr(exceptions, exc_type):
                raise getattr(exceptions, exc_type)(exc_msg)
            else:
                raise exception_object

        else:
            raise exception_object

    def _getMethods(self):
        resp_data = requests.get(self.uri)

        return json.loads(resp_data.text).get('methods')

    @staticmethod
    def __getNextId():
        next_id = 0

        while 1:
            next_id += 1
            yield next_id

    def __sendRequest(self, rpc_request):
        try:
            # Encode the RPC Request
            data = self.engine.encode([rpc_request], [])

            headers = {
                'user-agent': 'Labtronyx-RPC/1.0.0'
            }

            # Send the encoded request
            with self.rpc_lock:
                resp_data = self._reqSession.post(self.uri, data, headers=headers, timeout=self.timeout)

            # Check status code
            if resp_data.status_code is not 200:
                raise errors.RpcError("Server returned error code: %d" % resp_data.status_code)

            return resp_data.text

        except requests.ConnectionError:
            raise errors.RpcServerNotFound()

        except requests.Timeout:
            raise errors.RpcTimeout()

    def __decodeResponse(self, data):
        rpc_requests, rpc_responses, rpc_errors = self.engine.decode(data)

        if len(rpc_errors) > 0:
            # There is a problem if there are more than one errors,
            # so just check the first one
            recv_error = rpc_errors[0]
            if isinstance(recv_error, errors.RpcMethodNotFound):
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
            raise errors.RpcInvalidPacket("An incorrectly formatted packet was received")

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
        data = self.__sendRequest(req)

        return self.__decodeResponse(data)

    def _rpcNotify(self, remote_method, *args, **kwargs):
        req = RpcRequest(method=remote_method, args=args, kwargs=kwargs)

        self.__sendRequest(req)

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