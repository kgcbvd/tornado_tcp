from tornado import gen, ioloop, iostream, tcpserver, web

list_msg = []

class TcpClient(object):

    def __init__(self, stream):
        super().__init__()
        self.stream = stream
        self.stream.set_close_callback(self.disconnect)

    @gen.coroutine
    def disconnect(self):
        yield []

    @gen.coroutine
    def messages(self, name):
        try:
            while True:
                line = yield self.stream.read_until(b'\n')
                text_line = line.decode('utf-8').strip()
                if text_pattern(text_line):
                    list_msg.append(name + ' ' + text_line.replace(':: ', ' | '))
                if line == b'End\n':
                    self.stream.close()
        except iostream.StreamClosedError:
            pass

    @gen.coroutine
    def connect(self):
        line_auth = yield self.stream.read_until(b'\n')
        text_auth = line_auth.decode('utf-8').strip()
        if text_pattern(text_auth) and text_auth.split(':: ')[0] == 'Auth':
            name = '[%s]' % text_auth.split(':: ')[1]
            yield self.messages(name)
        else:
            self.stream.close()


def text_pattern(string):
    if ' :: ' not in string and len(string.split(':: ')) == 2:
        return True

class TcpServer(tcpserver.TCPServer):

    @gen.coroutine
    def handle_stream(self, stream, address):
        connection = TcpClient(stream)
        yield connection.connect()


class MainHandler(web.RequestHandler):
    def get(self):
        self.render('main.html', items=list_msg)

if __name__ == '__main__':
    tcp = TcpServer()
    tcp.listen(8001)

    app = web.Application([(r"/", MainHandler)])
    app.listen(8002)

    ioloop.IOLoop.instance().start()


