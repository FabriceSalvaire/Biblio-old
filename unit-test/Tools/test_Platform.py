####################################################################################################
#
# Babel - A Bibliography Manager
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

####################################################################################################

import unittest

from PyQt5 import QtWidgets

####################################################################################################

from Babel.Tools.Platform import *

####################################################################################################

class TestPlatform(unittest.TestCase):

    ##############################################

    def test_platform(self):

        application = QtWidgets.QApplication(sys.argv)
        platform = Platform(application)
        print(platform)

####################################################################################################

if __name__ == '__main__':

    unittest.main()
