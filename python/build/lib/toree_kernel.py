import os
import signal
import sys
import time
import io

from os import O_NONBLOCK, read
from fcntl import fcntl, F_GETFL, F_SETFL
from  subprocess import Popen, PIPE
from metakernel import MetaKernel
from py4j.java_gateway import JavaGateway, CallbackServerParameters, java_import
from py4j.protocol import Py4JError

class TextOutput(object):
    """Wrapper for text output whose repr is the text itself.
       This avoids `repr(output)` adding quotation marks around already-rendered text.
    """
    def __init__(self, output):
        self.output = output

    def __repr__(self):
        return self.output

class ToreeKernel(MetaKernel):
    implementation = 'toree_kernel'
    implementation_version = '0.1'
    langauge = 'scala'
    language_version = '2.11'
    banner = "toree_kernel"
    language_info = {'name': 'scala',
                     'mimetype': 'application/scala',
                     'file_extension': '.scala'}

    kernel_json = {
            'argv': [
                'python', '-m', 'toree_kernel', '-f', '{connection_file}'],
            'display_name': 'Toree Client',
            'language': 'scala',
            'name': 'toree_kernel'
            }

    def __init__(self, **kwargs):
        super(ToreeKernel, self).__init__(**kwargs)
        #self._start_toree_client()

    #def sig_handler(signum, frame):
        #self.gateway_proc.terminate()

    def do_shutdown(self, restart):
        super(ToreeKernel, self).do_shutdown(restart)
        #self.gateway_proc.terminate()

    def _start_toree_client(self):
        args = [
            "java",
            "-classpath",
            "../target/toree_client-0.1-jar-with-dependencies.jar",
            "com.ibm.ToreeClient"
        ]

        self.gateway_proc = Popen(args, stderr=PIPE, stdout=PIPE)
        time.sleep(1.5)
        self.gateway = JavaGateway(
                start_callback_server=True,
                callback_server_parameters=CallbackServerParameters())

        flags = fcntl(self.gateway_proc.stdout, F_GETFL) # get current p.stdout flags
        fcntl(self.gateway_proc.stdout, F_SETFL, flags | O_NONBLOCK)

        flags = fcntl(self.gateway_proc.stderr, F_GETFL) # get current p.stdout flags
        fcntl(self.gateway_proc.stderr, F_SETFL, flags | O_NONBLOCK)

        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGHUP, self.sig_handler)


    def Error(self, output):
        if not output:
            return
        
        super(ToreeKernel, self).Error(output)

    def handle_output(self, fd, fn):
        stringIO = io.StringIO()
        while True:
            try:
                b = read(fd.fileno(), 1024)
                if b:
                    stringIO.write(b.decode('utf-8'))
            except OSError:
                break

        s = stringIO.getvalue()
        if s:
            fn(s.strip())

        stringIO.close()

    def do_execute_direct(self, code, silent=False):
        """
        :param code:
            The code to be executed.
        :param silent:
            Whether to display output.
        :return:
            Return value, or None

        MetaKernel code handler.
        """

        """
        if not code.strip():
            return None

        retval = None
        try:
            retval = self.gateway.entry_point.eval(code.rstrip())
            self.handle_output(self.gateway_proc.stdout, self.Print)
            self.handle_output(self.gateway_proc.stderr, self.Error)
        except Py4JError as e:
            if not silent:
                self.Error(e.cause)

        if retval is None:
            return
        elif isinstance(retval, str):
            return TextOutput(retval)
        else:
            return retval
        """
        return "happy"

if __name__ == '__main__':
    ToreeKernel.run_as_main()
