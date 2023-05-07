from setuptools import setup

setup(
    name='stretch_remote',
    version='0.1',
    description='library to remotely command and listen to stretch robot',
    url='https://github.com/Healthcare-Robotics/stretch_remote',
    author='auth',
    author_email='tan_you_liang@hotmail.com',
    license='MIT',
    install_requires=['zmq', 'typing'],
    zip_safe=False
)
