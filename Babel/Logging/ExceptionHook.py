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

from datetime import datetime
import io
import sys
import traceback

####################################################################################################

from Babel.Logging.Email import Email
from Babel.Tools.Platform import Platform
from Babel.Tools.Singleton import singleton

####################################################################################################

def format_exception(exception_type, exception_value, exception_traceback):

    """ Format an exception to string. """

    # traceback.format_exc()
    traceback_string_io = io.StringIO()
    traceback.print_exception(exception_type, exception_value, exception_traceback, file=traceback_string_io)

    return traceback_string_io.getvalue()

####################################################################################################

@singleton
class DispatcherExceptionHook(object):

    """ DispatcherExceptionHook install an exception hook in the Python interpreter. This class is a
    singleton and follows the Observer Pattern.  When an exception is raised, it is catched by the
    hook, that calls the method :meth:`notify` for each registered observer.
    """

    ##############################################

    def __init__(self):

        self._observers = []

        sys.excepthook = self._exception_hook

    ##############################################

    def __iter__(self):

        return iter(self._observers)

    ##############################################

    def __getitem__(self, exception_hook_class):

        for observer in self:
            if isinstance(observer, exception_hook_class):
                return observer
        else:
            return None

    ##############################################

    def register_observer(self, observer):

        """ Register an observer, that must have a :meth:`notify` method. """

        self._observers.append(observer)

    ##############################################

    def _exception_hook(self, exception_type, exception_value, exception_traceback):

        for observer in self:
            observer.notify(exception_type, exception_value, exception_traceback)

####################################################################################################

class ExceptionHook(object):

    ##############################################

    def __init__(self, context=''):

        self.context = context

        # DispatcherExceptionHook().register_observer(self)

####################################################################################################

class StderrExceptionHook(ExceptionHook):

    """ Log exception on stderr. """

    _line_width = 80
    _line = '='*_line_width

    ##############################################

    def __init__(self, context=''):

        super(StderrExceptionHook, self).__init__(context)

    ##############################################

    def notify(self, exception_type, exception_value, exception_traceback):

        print(self._line, '\n', file=sys.stderr)
        print('StderrExceptionHook'.center(self._line_width), '\n', file=sys.stderr)
        # traceback.print_exc()
        traceback.print_exception(exception_type, exception_value, exception_traceback)
        print('\n', self._line, file=sys.stderr)

####################################################################################################

class EmailExceptionHook(ExceptionHook):

    """ Send per email exception. """

    ##############################################

    def __init__(self, context='', recipients=[]):

        """ The mandatory recipient is set in :attr:`Config.Email.to_address`. Additional recipients
        can be added using the list *recipients*. A context string can be set using *context*.
        """

        self._recipients = recipients

        super(EmailExceptionHook, self).__init__(context)

    ##############################################

    def notify(self, exception_type, exception_value, exception_traceback):

        template_message = '''
Object: An exception occurred in Babel software on %(date)s UTC

---------------------------------------------------------------------------------

Context:
%(context)s

---------------------------------------------------------------------------------
%(platform)s
---------------------------------------------------------------------------------

%(traceback)s

---------------------------------------------------------------------------------
'''

        traceback = format_exception(exception_type, exception_value, exception_traceback)
        now = datetime.utcnow()
        platform = Platform()

        message = template_message % {'date': now.strftime('%Y-%m-%d %H:%M'),
                                      'context': str(self.context),
                                      'platform': str(platform),
                                      'traceback': traceback,
                                      }

        email = Email(subject='An exception occurred in Babel software',
                      recipients=Config.Email.to_address,
                      message=message,
                      )
        email.add_recipients(self._recipients)
        email.send()
