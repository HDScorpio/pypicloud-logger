pypicloud-logger
================
*pypicloud-logger* is a pyramid `tween`_ that logs `PyPICloud`_ requests for
package statistics.

Standard way of logging requests (Apache/uWSIG logging, middleware
`TransLogger`_ etc.) does not allow track package names on upload and keywords
on search requests because of POST method.


What logged?
------------
The *pypicloud-logger* tween logs 4 operations:

- **UPLOAD** - uploading packages.
- **DOWNLOAD** - downloading packages.
- **SEARCH** - search for packages.
- **DELETE** - deleting packages.

By default, logs are in Apache combined format::

 %(CLIENT_ADDR)s - %(USERNAME)s [%(TIMESTAMP)s] "%(OPERATION)s %(FILENAME)s %(HTTP_VERSION)s" %(STATUS)d %(SIZE)d "%(REFERER)s" "%(USER_AGENT)s"

Here available next fields:

- ``CLIENT_ADDR`` - client IP address. If `PyPICloud`_ is behind the proxy,
  then the value of the X-Forwarded-For header is used.
- ``USERNAME`` - user login.
- ``TIMESTAMP`` - timestamp of request with local timezone.
- ``OPERATION`` - operation name.
- ``FILENAME`` - package filename.
- ``HTTP_VERSION`` - HTTP protocol version.
- ``STATUS`` - response status code.
- ``SIZE`` - the size of package or result of operation (see below).
- ``REFERER`` - referer of the request. Double quotes are escaped.
- ``USER_AGENT`` - user agent. Double quotes are escaped.


Upload logs
***********
Upload log looks like this::

 127.0.0.1 - - [06/Apr/2020:12:16:59 +0500] "UPLOAD pypicloud-1.0.13.tar.gz HTTP/1.1" 200 503416 "-" "twine/1.15.0 pkginfo/1.5.0.1 requests/2.23.0 setuptools/44.1.0 requests-toolbelt/0.9.1 tqdm/4.44.1 CPython/2.7.17"

If package already exists (409 response status), then filed ``%(SIZE)s`` is zero
because data is not read.


Download logs
*************
Download log looks like this::

 127.0.0.1 - - [06/Apr/2020:12:18:59 +0500] "DOWNLOAD pypicloud-1.0.13.tar.gz HTTP/1.1" 200 503416 "-" "pip/20.0.2 {\"ci\":null,\"cpu\":\"x86_64\",\"distro\":{\"id\":\"tricia\",\"libc\":{\"lib\":\"glibc\",\"version\":\"2.27\"},\"name\":\"Linux Mint\",\"version\":\"19.3\"},\"implementation\":{\"name\":\"CPython\",\"version\":\"2.7.17\"},\"installer\":{\"name\":\"pip\",\"version\":\"20.0.2\"},\"openssl_version\":\"OpenSSL 1.1.1  11 Sep 2018\",\"python\":\"2.7.17\",\"setuptools_version\":\"44.1.0\",\"system\":{\"name\":\"Linux\",\"release\":\"5.0.0-37-generic\"}}"


Search logs
***********
Search log looks like this::

 127.0.0.1 - - [06/Apr/2020:12:22:17 +0500] "SEARCH pypi,beaker HTTP/1.1" 200 5 "-" "pip/20.0.2 {\"ci\":null,\"cpu\":\"x86_64\",\"distro\":{\"id\":\"tricia\",\"libc\":{\"lib\":\"glibc\",\"version\":\"2.27\"},\"name\":\"Linux Mint\",\"version\":\"19.3\"},\"implementation\":{\"name\":\"CPython\",\"version\":\"2.7.17\"},\"installer\":{\"name\":\"pip\",\"version\":\"20.0.2\"},\"openssl_version\":\"OpenSSL 1.1.1  11 Sep 2018\",\"python\":\"2.7.17\",\"setuptools_version\":\"44.1.0\",\"system\":{\"name\":\"Linux\",\"release\":\"5.0.0-37-generic\"}}"

Here fileid ``%(FILENAME)s`` is comma-separated keywords of search request
and ``%(SIZE)s`` is number of packages found.

For log above was executed next command:

.. code-block::

    $ pip search pypi beaker
    beaker (1.11.0)           - A Session and Caching library with WSGI Middleware
    pypicloud-logger (0.0.1)  - Logger of requests to PyPICloud service
      INSTALLED: 0.0.1 (latest)
    twine (3.1.1)             - Collection of utilities for publishing packages on PyPI
      INSTALLED: 1.15.0
      LATEST:    3.1.1
    pypicloud-swift (0.2.0)   - OpenStack Swift storage for PyPI Cloud
    pypicloud (1.0.13)        - Private PyPI backed by S3
      INSTALLED: 1.0.13 (latest)


Delete logs
***********
Delete log looks like this::

 127.0.0.1 - - [06/Apr/2020:12:24:35 +0500] "DELETE pypicloud-1.0.13.tar.gz HTTP/1.1" 200 0 "http://127.0.0.1:6543/" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0"

Here field ``%(SIZE)s`` is always zero because data is not read.


Configure
---------
Use the ``pyramid.tweens`` settings value to configure *pypicloud-logger*:

.. code-block:: ini

    [app:main]
    use = egg:pypicloud
    ...
    pyramid.tweens =
        ppc_logger.tween.PPCLoggerTween
        pyramid_tm.tm_tween_factory
        pyramid.tweens.excview_tween_factory

The *pypicloud-logger* tween has the following settings:

- ``ppc_logger.logger_name`` - the name of the logger,
  default is ``pypicloud-logger``.
- ``ppc_logger.log_level`` - the level of log entries, default is ``INFO``.
- ``ppc_logger.log_format`` - the format of the log entries,
  default is Apache log format (see above).
- ``ppc_logger.dt_format`` - the `datetime.strftime`_ format of the filed
  ``%(TIMESTAMT)s``, default is ``%d/%b/%Y:%H:%M:%S %z``.

To configure logger use `logging configuration`_. Example configuration:

.. code-block:: ini

    [app:main]
    use = egg:pypicloud
    ...
    pyramid.tweens =
        ppc_logger.tween.PPCLoggerTween
        pyramid_tm.tm_tween_factory
        pyramid.tweens.excview_tween_factory
    ...

    ppc_logger.logger_name = pypi-ops
    ppc_logger.log_level = DEBUG
    ppc_logger.log_format = %%(TIMESTAMP)s - %%(FILENAME)s %%(SIZE)d %%(STATUS)d
    ppc_logger.dt_format = %%Y-%%m-%%d %%H:%%M:%%S

    [loggers]
    keys = ppclogger

    [handlers]
    keys = console

    [formatters]
    keys = default

    [logger_ppclogger]
    level = DEBUG
    qualname = pypi-ops
    handlers = console
    propagate = 0

    [handler_console]
    class = StreamHandler
    args = (sys.stderr,)
    level = DEBUG
    formatter = default

    [formatter_default]
    format = %(message)s


.. _PyPICloud: https://pypicloud.readthedocs.io/en/latest/index.html
.. _TransLogger: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/logging.html#request-logging-with-paste-s-translogger
.. _tween: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/hooks.html#registering-tweens
.. _datetime.strftime: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
.. _logging configuration: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/logging.html
