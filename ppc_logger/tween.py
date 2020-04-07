import re
import logging
from xml.etree import ElementTree
from datetime import datetime

from dateutil.tz import tzlocal


DOWNLOAD_DELETE_RE = re.compile(r'^/api/package/.+/(.+)$')
SEARCH_XML_XPATH = './/*[name="name"]//value/string'
LOCAL_TZ = tzlocal()


class PPCLoggerTween(object):
    """ Pyramid tween for logging pypicloud operations with packages. """

    LOG_FORMAT = ('%(CLIENT_ADDR)s - %(USERNAME)s [%(TIMESTAMP)s] '
                  '"%(OPERATION)s %(FILENAME)s %(HTTP_VERSION)s" '
                  '%(STATUS)d %(SIZE)d "%(REFERER)s" "%(USER_AGENT)s"')

    DT_FORMAT = '%d/%b/%Y:%H:%M:%S %z'

    class PackageSizeCounter(object):
        """ Counter to get size of uploaded package """

        def __init__(self, f):
            self.f = f
            self.size = 0

        def read(self, size=-1):
            buf = self.f.read(size)
            self.size += len(buf)
            return buf

        def close(self):
            self.f.close()

    def __init__(self, handler, registry):
        self.handler = handler

        log_level_name = registry.settings.get('ppc_logger.log_level', 'INFO')
        self.log_level = logging.getLevelName(log_level_name)
        if not isinstance(self.log_level, int):
            raise ValueError('Unknown logging level name "%s"' % log_level_name)

        self.log_format = registry.settings.get('ppc_logger.log_format',
                                                self.LOG_FORMAT)

        self.dt_format = registry.settings.get('ppc_logger.dt_format',
                                               self.DT_FORMAT)

        logger_name = registry.settings.get('ppc_logger.logger_name',
                                            'pypicloud-logger')
        self.logger = logging.getLogger(logger_name)

    def __call__(self, request):
        request_timestamp = datetime.now(tz=LOCAL_TZ)
        operation = None
        package_filename = None

        if request.method == 'GET' and '/api/package/' in request.path:
            m = DOWNLOAD_DELETE_RE.match(request.path)
            if m:
                operation = 'DOWNLOAD'
                package_filename = m.group(1)

        elif (request.method == 'POST' and
              'multipart/form-data' in request.content_type):
            operation = 'UPLOAD'
            package_filename = request.POST['content'].filename
            request.POST['content'].file = self.PackageSizeCounter(
                request.POST['content'].file)

        elif (request.method == 'POST' and
              'text/xml' in request.content_type):
            operation = 'SEARCH'
            # log all search words as package filename
            root = ElementTree.fromstring(request.body)
            package_filename = ','.join([e.text.strip() for e in
                                         root.findall(SEARCH_XML_XPATH)])

        elif request.method == 'DELETE' and '/api/package/' in request.path:
            operation = 'DELETE'
            m = DOWNLOAD_DELETE_RE.match(request.path)
            if m:
                package_filename = m.group(1)

        response = self.handler(request)

        if not operation:
            return response

        if operation == 'SEARCH':
            # log search result
            root = ElementTree.fromstring(response.body)
            operation_size = len([e.text for e in
                                  root.findall(SEARCH_XML_XPATH)])

        elif operation == 'UPLOAD':
            # get uploaded size
            operation_size = request.POST['content'].file.size

        else:
            operation_size = response.content_length

        params = {
            'CLIENT_ADDR': request.client_addr,
            'USERNAME': request.authenticated_userid or '-',
            'TIMESTAMP': request_timestamp.strftime(self.dt_format),
            'OPERATION': operation,
            'FILENAME': package_filename,
            'HTTP_VERSION': request.http_version or '-',
            'STATUS': response.status_int,
            'SIZE': operation_size,
            'REFERER': (request.referer or '-').replace('"', '\\"'),
            'USER_AGENT': (request.user_agent or '-').replace('"', '\\"')
        }

        self.logger.log(self.log_level, self.log_format, params)

        return response
