####################################################################################################
#
# This file is Autogenerated by make-ConfigInstall
#
####################################################################################################

####################################################################################################

import os

####################################################################################################

import Babel.Tools.Path as PathTools # due to Path class

####################################################################################################

_this_file = PathTools.to_absolute_path(__file__)

class Path(object):

    babel_module_directory = PathTools.parent_directory_of(_this_file, step=2)
    config_directory = os.path.dirname(_this_file)
    share_directory = os.path.realpath(os.path.join(config_directory, '..', '..', 'share'))

####################################################################################################

class Logging(object):

    default_config_file = 'logging.yml'
    directories = (Path.config_directory,)

    ##############################################

    @staticmethod
    def find(config_file):

        return PathTools.find(config_file, Logging.directories)

####################################################################################################

class Icon(object):

    icon_directory = os.path.join(Path.share_directory, 'icons')

    ##############################################

    @staticmethod
    def find(file_name, size):

        icon_directory = os.path.join(Icon.icon_directory, '%ux%u' % (size, size))
        return PathTools.find(file_name, (icon_directory,))

####################################################################################################

class WordDataBase(object):

    lexique_module_path = os.path.join(Path.babel_module_directory, 'Lexique')

    bnc_database_path = os.path.join(lexique_module_path,
                                     'BritishNationalCorpus', 'bnc.sqlite')
