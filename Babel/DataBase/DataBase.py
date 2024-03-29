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

import logging

from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import sessionmaker

####################################################################################################

from .SqlAlchemyBase import autoload_table

####################################################################################################

class DataBase(object):

    _logger = logging.getLogger(__name__)

    ##############################################

    def __init__(self, connection_string, echo=False):

        self._engine = create_engine(connection_string, echo=echo)
        self.session = sessionmaker(bind=self._engine)()
        self._declarative_base_class = None

    ###############################################

    @property
    def inspector(self):

        return Inspector.from_engine(self._engine)

    ###############################################

    def has_table(self, table_name):

        # Fixme: give acces to engine ?

        return self._engine.has_table(table_name)

    ###############################################

    def table_columns(self, table_name):

        table = autoload_table(self._engine, table_name)
        return [column.name for column in table.columns]

    ###############################################

    def table_has_columns(self, table_name, columns):

        table_columns = self.table_columns(table_name)
        for column in columns:
            if column not in table_columns:
                return False
        return True

    ###############################################

    def close_session(self):

        self.session.close()

    ###############################################

    def reflect_unknown_columns(self, table_class):

        unknown_columns = {}
        for column_dict in self.inspector.get_columns(table_class.__tablename__):
            #? column_dict = dict(column_dict)
            column_name = column_dict['name']
            if column_name not in table_class.__dict__:
                column_type = column_dict['type'].__class__
                del column_dict['type']
                column_dict['info'] = {'title':column_name, 'unknown':True}
                unknown_columns[column_name] = Column(column_type, **column_dict)

        return unknown_columns
