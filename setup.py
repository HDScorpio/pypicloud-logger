from setuptools import setup


setup(
    name='pypicloud-logger',
    version='0.0.1',
    description='Pyramid tween that logs PyPICloud requests for package '
                'statistics',
    long_description=open("README.rst").read(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Systems Administration',
    ],
    license='MIT',
    author='Andrey Ulagashev',
    author_email='ulagashev.andrey@gmail.com',
    url='https://github.com/HDScorpio/pypicloud-logger',
    keywords='pypi package ',
    platforms='any',
    install_requires=['python-dateutil'],
    packages=['ppc_logger']
)
