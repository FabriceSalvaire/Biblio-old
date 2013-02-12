####################################################################################################
# 
# Babel - A Bibliography Manager 
# Copyright (C) Salvaire Fabrice 2013 
# 
####################################################################################################

####################################################################################################
#
#                                              Audit
#
# - 02/05/2011 Fabrice
#   - add dict interface ?
#
####################################################################################################

####################################################################################################

import ctypes
import os
import platform
import sys

from PyQt4 import QtCore, QtGui

####################################################################################################

from Babel.Tools.EnumFactory import EnumFactory

####################################################################################################

platform_enum = EnumFactory('PlatformEnum', ('linux', 'windows', 'macosx'))

####################################################################################################
#
# xdpyinfo
# screen #0:
#   dimensions:    1280x1024 pixels (382x302 millimeters)
#   resolution:    85x86 dots per inch
#
# x11info = QtGui.QX11Info()
# dpi = x11info.appDpiX(screen), x11info.appDpiY(screen)
#
####################################################################################################

class Platform(object):

    ##############################################

    def __init__(self, application=None):

       self.python_version = platform.python_version()
       self.qt_version = QtCore.QT_VERSION_STR
       self.pyqt_version = QtCore.PYQT_VERSION_STR

       self.os = self._get_os()
       self.node = platform.node()
       self.distribution = ' '.join(platform.dist())
       self.machine = platform.machine()
       self.architecture = platform.architecture()[0]

       # CPU
       self.cpu = self._get_cpu()
       # self.number_of_cores = 
       self.cpu_khz = self._get_cpu_khz()

       # RAM
       self.memory_size_kb = self._get_memory_size_kb()

       # Screen
       if application is not None:
           self.desktop = application.desktop()
           self.number_of_screens = self.desktop.screenCount() 
       else:
           self.desktop = None
           self.number_of_screens = 0
       self.screens = []
       for i in xrange(self.number_of_screens):
           self.screens.append(Screen(self, i))

       # OpenGL
       self.gl_renderer = None
       self.gl_version = None
       self.gl_vendor = None
       self.gl_extensions = None

    ##############################################

    def _get_os(self):

        if os.name in 'nt':
            return platform_enum.windows
        elif sys.platform in 'linux2':
            return platform_enum.linux
        else:
            raise RuntimeError('unknown platform')

    ##############################################

    def _get_cpu(self):

        if self.os == platform_enum.linux:
 
            with open('/proc/cpuinfo', 'rt') as cpuinfo:
                for line in cpuinfo:
                    if 'model name' in line:
                        s = line.split(':')[1]
                        return s.strip().rstrip()

        elif self.os == platform_enum.windows:
            raise NotImplementedError

    ##############################################

    def _get_number_of_cores(self):

        if self.os == platform_enum.linux:
 
            number_of_cores = 0
            with open('/proc/cpuinfo', 'rt') as cpuinfo:
                for line in cpuinfo:
                    if 'processor' in line:
                        number_of_cores += 1
            return number_of_cores

        elif self.os == platform_enum.windows:

            return int(os.getenv('NUMBER_OF_PROCESSORS'))

    ##############################################

    def _get_cpu_khz(self):

        if self.os == platform_enum.linux:

            with open('/proc/cpuinfo', 'rt') as cpuinfo:
                for line in cpuinfo:
                    if 'cpu MHz' in line:
                        s = line.split(':')[1]
                        return int(1000 * float(s))

        if self.os == platform_enum.windows:
            raise NotImplementedError

    ##############################################

    def _get_memory_size_kb(self):

        if self.os == platform_enum.linux:

            with open('/proc/meminfo', 'rt') as cpuinfo:
                for line in cpuinfo:
                    if 'MemTotal' in line:
                        s = line.split(':')[1][:-3]
                        return int(s)

        if self.os == platform_enum.windows:
            raise NotImplementedError

    ##############################################

    def query_opengl(self):
        
        import OpenGL.GL as GL
        
        self.gl_renderer = GL.glGetString(GL.GL_RENDERER)
        self.gl_version = GL.glGetString(GL.GL_VERSION)
        self.gl_vendor = GL.glGetString(GL.GL_VENDOR)
        self.gl_extensions = GL.glGetString(GL.GL_EXTENSIONS)

    ##############################################

    def __str__(self):

        if self.os == platform_enum.linux:
            os = 'Linux'
        elif self.os == platform_enum.windows:
            os = 'Windows'
        elif self.os == platform_enum.macosx:
            os = 'Mac OSX'

        data = {'node':self.node,
 
                'machine':self.machine,
                'architecture':self.architecture,
                'cpu':self.cpu,
                'number_of_cores':self.number_of_cores,
                'cpu_mhz':self.cpu_khz/1000,
                'memory_size_mb':self.memory_size_kb/1024,
                
                'gl_renderer': self.gl_renderer,
                'gl_version': self.gl_version,
                'gl_vendor': self.gl_vendor,
                'gl_extensions': self.gl_extensions,
                
                'number_of_screens':self.number_of_screens,
                
                'os':os,
                'distribution':self.distribution,
                'python_version':self.python_version,
                'qt_version':self.qt_version,
                'pyqt_version':self.pyqt_version,
                }
        
        message_template = '''
Platform %(node)s
'''
        message = message_template % data

        message_template = '''
  Hardware:
    Machine: %(machine)s
    Architecture: %(architecture)s
    CPU: %(cpu)s
      Number of Cores: %(number_of_cores)u
      CPU Frequence: %(cpu_mhz)u MHz
    Memory: %(memory_size_mb)u MB
   OpenGL
     Render: %(gl_renderer)s
     Version: %(gl_version)s
     Vendor: %(gl_vendor)s
   Number of Screens: %(number_of_screens)u
'''
        message += message_template % data

        for screen in self.screens:
            message += str(screen)
        
        message_template = '''
  Software Versions:
    OS: %(os)s
    Distribution: %(distribution)s
    Python: %(python_version)s
    Qt: %(qt_version)s
    PyQt: %(pyqt_version)s
'''
        message += message_template % data
        
        return message

####################################################################################################

class Screen(object):

    ##############################################

    def __init__(self, platform, screen_id):

        self.screen_id = screen_id

        qt_screen_geometry = platform.desktop.screenGeometry(screen_id)
        self.screen_width, self.screen_height = qt_screen_geometry.width(), qt_screen_geometry.height()

        widget = platform.desktop.screen(screen_id)
        self.dpi =  widget.physicalDpiX(), widget.physicalDpiY() 

        # qt_available_geometry = self.desktop.availableGeometry(screen_id)

    ##############################################

    def __str__(self):

        message_template = '''
    Screen %(screen_id)u
     geometry   %(screen_width)ux%(screen_height)u px
     resolution %(dpi)s dpi
'''
        
        return message_template % {'screen_id':self.screen_id,
                                   'screen_width':self.screen_width,
                                   'screen_height':self.screen_height,
                                   'dpi':self.dpi,
                                   }

####################################################################################################
#
# End
#
####################################################################################################
