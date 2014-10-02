# -*- coding: utf-8 -*-

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

from PyQt4 import QtGui

####################################################################################################

from Babel.Logging.Email import Email
from Babel.Tools.Platform import Platform
import Babel.Config.Config as Config
import Babel.Version as Version

####################################################################################################

from Babel.GUI.ui.email_bug_form_ui import Ui_email_bug_form

####################################################################################################

class EmailBugForm(QtGui.QDialog):

    ###############################################

    def __init__(self, traceback=''):

        super(EmailBugForm, self).__init__()

        self._traceback = traceback

        form = self._form = Ui_email_bug_form()
        form.setupUi(self)

        form.send_email_button.clicked.connect(self.send_email)

    ##############################################

    def send_email(self):

        form = self._form

        from_address = unicode(form.from_line_edit.text())
        if not from_address:
            from_address = Config.Email.from_address
        
        # Fixme: test field ?
        # QtGui.QMessageBox.critical(None, title, message)

        template_message = """
Bug description:
%(description)s

---------------------------------------------------------------------------------
Babel Version:
  %(babel_version)s

---------------------------------------------------------------------------------
%(traceback)s

---------------------------------------------------------------------------------
%(platform)s

---------------------------------------------------------------------------------
"""

        application = QtGui.QApplication.instance()

        # Fixme: singleton ?
        platform = Platform(application)
        platform.query_opengl()
       
        message = template_message % {'description': unicode(form.description_plain_text_edit.toPlainText()),
                                      'babel_version': unicode(Version.babel),
                                      'platform': unicode(platform),
                                      'traceback': self._traceback,
                                      }

        email = Email(from_address=from_address,
                      subject='Babel Bug: ' + unicode(form.subject_line_edit.text()),
                      recipients=Config.Email.to_address,
                      message=message,
                      )
        recipients = unicode(form.recipients_line_edit.text())
        if recipients:
            email.add_recipients_from_string(recipients)
        email.send()

        self.accept()

####################################################################################################
#
# End
#
####################################################################################################