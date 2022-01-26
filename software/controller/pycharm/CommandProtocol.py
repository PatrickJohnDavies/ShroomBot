import zmq

class CommandProtocol():
    def __init__(self, mq_socket):
        self.mq_socket = mq_socket

    def read(self, flags):
        message = None
        try:
            message = self.mq_socket.recv_json(flags=flags)
            return message
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                # state changed since poll event
                pass
            else:
                raise
        return message

    def write(self, id, data=None):
        command = {'id':id, 'data':data}
        self.mq_socket.send_json(command)

    def writeAndReadData(self, flags, id, data=None):
        self.write(id, data)
        command = self.read(flags)
        if (command['id'] != id):
            raise('wrong reponse')
        return command['data']