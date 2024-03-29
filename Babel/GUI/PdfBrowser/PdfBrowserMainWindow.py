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
import os
import subprocess

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

####################################################################################################

from .DirectoryListWidget import DirectoryListWidget
from .DirectoryTocWidget import DirectoryTocWidget
from .DocumentDirectory import DocumentDirectory
from .PdfViewer import ViewerController
from Babel.FileSystem.AutomaticFileRename import AutomaticFileRename
from Babel.FileSystem.DirectoryToc import DirectoryToc
from Babel.GUI.Base.MainWindowBase import MainWindowBase
from Babel.GUI.Widgets.IconLoader import IconLoader
from Babel.GUI.Widgets.MessageBox import MessageBox
from Babel.GUI.Widgets.PathNavigator import PathNavigator
from Babel.Tools.Container import EmptyRingError

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class PdfBrowserMainWindow(MainWindowBase):

    _logger = _module_logger.getChild('PdfBrowserMainWindow')

    ##############################################

    def __init__(self, parent=None):

        super(PdfBrowserMainWindow, self).__init__(title='Babel PDF Browser', parent=parent)

        self._current_path = None
        self._init_ui()

    ##############################################

    def _init_ui(self):

        self._central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self._central_widget)

        self._viewer_controller = ViewerController()

        self._message_box = MessageBox(self)
        self._path_navigator = PathNavigator(self)
        self._file_name_label = QtWidgets.QLabel()
        self._file_counter_label = QtWidgets.QLabel()
        self._directory_toc = DirectoryTocWidget()
        image_widget = self._viewer_controller.image_widget

        # Fixme: add funcs ?
        self._document_widgets = (self._file_name_label, self._file_counter_label,
                                  image_widget)

        self._vertical_layout = QtWidgets.QVBoxLayout(self._central_widget)
        self._vertical_layout.addWidget(self._message_box)
        self._vertical_layout.addWidget(self._path_navigator)
        horizontal_layout = QtWidgets.QHBoxLayout()
        # Fixme: layout
        horizontal_layout.addWidget(self._file_name_label)
        horizontal_layout.addWidget(self._file_counter_label)
        self._vertical_layout.addLayout(horizontal_layout)
        self._vertical_layout.addWidget(self._directory_toc)
        self._vertical_layout.addWidget(image_widget)

        self.statusBar()
        self._create_actions()
        self._create_toolbar()

        self._directory_list_dock_widget = QtWidgets.QDockWidget(self)
        self._directory_list_dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self._directory_list = DirectoryListWidget(self)
        self._directory_list_dock_widget.setWidget(self._directory_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._directory_list_dock_widget)

        self._path_navigator.path_changed.connect(self.open_directory)
        self._directory_toc.path_changed.connect(self.open_directory)
        self._directory_list.move_file.connect(self.move_file)
        self._directory_list.move_current_file.connect(self.move_current_file)

        self._directory_toc_mode()

    ##############################################

    def _create_actions(self):

        icon_loader = IconLoader()

        self._directory_toc_mode_action = \
            QtWidgets.QAction(icon_loader['folder-blue'],
                          'Directory toc mode',
                          self,
                          toolTip='Directory toc mode',
                          triggered=self._directory_toc_mode,
                          shortcut='Ctrl+D',
                          shortcutContext=Qt.ApplicationShortcut,
                          )

        self._pdf_browser_mode_action = \
            QtWidgets.QAction(icon_loader['application-pdf'],
                          'PDF browser mode',
                          self,
                          toolTip='PDF browser mode',
                          triggered=self._pdf_browser_mode,
                          shortcut='Ctrl+P',
                          shortcutContext=Qt.ApplicationShortcut,
                          )

        self._previous_document_action = \
            QtWidgets.QAction(icon_loader['arrow-left'],
                          'Previous document',
                          self,
                          toolTip='Previous Document',
                          triggered=self.previous_document,
                          shortcut='Backspace',
                          shortcutContext=Qt.ApplicationShortcut,
                          )

        self._next_document_action = \
            QtWidgets.QAction(icon_loader['arrow-right'],
                          'Next document',
                          self,
                          toolTip='Next Document',
                          triggered=self.next_document,
                          shortcut='Space',
                          shortcutContext=Qt.ApplicationShortcut,
                          )

        self._select_action = \
            QtWidgets.QAction(icon_loader['get-hot-new-stuff'],
                          'Select document',
                          self,
                          toolTip='Select Document',
                          triggered=self.select_document,
                          shortcut='Ctrl+S',
                          shortcutContext=Qt.ApplicationShortcut,
                          )

        self._open_pdf_action = \
            QtWidgets.QAction(icon_loader['document-export'],
                          'Open PDF',
                          self,
                          toolTip='Open PDF',
                          triggered=lambda x: self.open_current_document(extern=True),
                          shortcut='Ctrl+O',
                          shortcutContext=Qt.ApplicationShortcut,
                          )

        self._open_pdf_viewer_action = \
            QtWidgets.QAction(icon_loader['text-field'],
                          'Open PDF Viewer',
                          self,
                          toolTip='Open PDF Viewer',
                          triggered=lambda x: self.open_current_document(extern=False),
                          shortcut='Ctrl+V',
                          shortcutContext=Qt.ApplicationShortcut,
                          )

    ##############################################

    def _create_toolbar(self):

        self._main_tool_bar = self.addToolBar('Main')
        for item in (self._directory_toc_mode_action,
                     self._pdf_browser_mode_action,
                    ):
            self._main_tool_bar.addAction(item)

        self._document_tool_bar = self.addToolBar('Document')
        for item in (self._previous_document_action,
                     self._next_document_action,
                     self._select_action,
                     self._open_pdf_action,
                     self._open_pdf_viewer_action,
                    ):
            self._document_tool_bar.addAction(item)

        self.addToolBar(self._viewer_controller.tool_bar)
        self.addToolBar(self._viewer_controller.page_controller.tool_bar)

    ##############################################

    def init_menu(self):

        super(PdfBrowserMainWindow, self).init_menu()

    ##############################################

    def show_message(self, message=None, timeout=0, warn=False):

        """ Hides the normal status indications and displays the given message for the specified
        number of milli-seconds (timeout). If timeout is 0 (default), the message remains displayed
        until the clearMessage() slot is called or until the showMessage() slot is called again to
        change the message.

        Note that showMessage() is called to show temporary explanations of tool tip texts, so
        passing a timeout of 0 is not sufficient to display a permanent message.
        """

        if warn:
            self._message_box.push_message(message)
        else:
            status_bar = self.statusBar()
            if message is None:
                status_bar.clearMessage()
            else:
                status_bar.showMessage(message, timeout)

    ##############################################

    def _directory_toc_mode(self):

        self._directory_toc.show()
        for widget in self._document_widgets:
            widget.hide()

    ##############################################

    def _pdf_browser_mode(self):

        self._directory_toc.hide()
        for widget in self._document_widgets:
            widget.show()

    ##############################################

    def open_directory(self, path):

        self._logger.info("open directory {}".format(str(path)))
        # Fixme: move to application?
        self._current_path = path
        self._directory_toc.update(DirectoryToc(path))
        self._path_navigator.set_path(path) # Fixme: path_navigator -> open_directory -> path_navigator
        self._document_directory = DocumentDirectory(path)
        if bool(self._document_directory):
            self._show_document()
        else:
            for widget in self._document_widgets:
                widget.clear()

    ##############################################

    @property
    def current_path(self):

        return self._current_path

    ##############################################

    @property
    def current_document(self):

        return self._document_directory.current_item

    ##############################################

    def previous_document(self):

        try:
            self._document_directory.previous()
            self._show_document()
        except StopIteration:
            pass

    ##############################################

    def next_document(self):

        try:
            next(self._document_directory)
            self._show_document()
        except StopIteration:
            pass

    ##############################################

    def _show_document(self):

        try:
            document = self.current_document
            self._file_name_label.setText(str(document.path.filename_part()))
            self._file_counter_label.setText('{} / {}'.format(self._document_directory.current_index +1,
                                                              len(self._document_directory)))
            self._viewer_controller.document = document.document # Fixme:
        except EmptyRingError:
            # self._logger.info('EmptyRingError')
            # Fixme: cf. open_directory
            for widget in self._document_widgets:
                widget.clear()

    ##############################################

    def select_document(self):

        pass
        # try:
        #     document = self.current_document
        #     document.selected = not document.selected
        #     self._viewer_controller.update_style()
        # except EmptyRingError:
        #     pass

    ##############################################

    def open_current_document(self, extern=True):

        try:
            document = self.current_document
            document_path = str(document.path)
            if extern:
                subprocess.call(('xdg-open', document_path))
            else:
                from Babel.GUI.PdfViewer.PdfViewerMainWindow import PdfViewerMainWindow
                pdf_viewer_window = PdfViewerMainWindow(document_path, parent=self)
                pdf_viewer_window.showMaximized()
        except EmptyRingError:
            pass

    ##############################################

    def _delete_file_from_browser(self, file_path):

        current_document = self.current_document # should not raise EmptyRingError
        if current_document.path != file_path:
            self._document_directory.delete(current_document)
        else:
            if not self._document_directory.delete_path(file_path):
                raise NameError("File {} not in the current directory".format(file_path))
        self._show_document()

    ##############################################

    def move_current_file(self, dst_path):

        self.move_file(self.current_document.path, dst_path)

    ##############################################

    def move_file(self, file_path, dst_path):

        # Fixme: here ?

        to_file_path = dst_path.join_filename(file_path.filename_part())

        # Test if the destination directory has already a file with the same name
        overwrite = False
        if bool(to_file_path):
            if file_path.shasum == to_file_path.shasum:
                # self.show_message("Destination has a duplicate of this file", warn=True)
                rc = QtWidgets.QMessageBox.question(self,
                                                    "",
                                                    "Destination has a duplicate of this file.\n"
                                                    "Remove this file instead?")
                if rc == QtWidgets.QMessageBox.Yes:
                    self._logger.info("Delete {}".format(str(file_path)))
                    file_path.delete()
                    self._delete_file_from_browser(file_path)
                return # delete or do nothing
            else:
                # self.show_message("Destination has a file with the same name", warn=True)
                to_file_path2 = AutomaticFileRename(to_file_path).generate()
                filename, ok = QtWidgets.QInputDialog.getText(self,
                                                              "Destination has a file with the same name",
                                                              "Rename to:",
                                                              text=to_file_path2.filename)
                # Fixme: implement overwrite
                if ok:
                     to_file_path = dst_path.join_filename(filename)
                else:
                    return # do nothing

        if file_path == to_file_path:
            self.show_message("Tried to move file {} to same place".format(str(file_path)), warn=True)
        else:
            # Last check
            if bool(to_file_path) and not overwrite:
                self.show_message("Tried to overwrite file {}".format(str(file_path)), warn=True)

            self._logger.info("Move {} to {}".format(str(file_path), str(to_file_path)))
            os.rename(str(file_path), str(to_file_path))
            self._delete_file_from_browser(file_path)
