#!/usr/bin/env python3
"""
Viewer Qt GUI for viewing, sorting, browsing files saved by the OnionLogger
"""
__author__ = 'jorxster@gmail.com'
__date__ = '27 May 2018'
__version__ = "0.1.0"

import os, sys, time
from PySide2 import QtCore, QtWidgets, QtGui

THIS_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(THIS_PATH)
import OnionLogger

print(OnionLogger)


class Viewer(QtWidgets.QMainWindow):
    """
    Primary window for loading .olog files
    """

    def __init__(self, parent=None):
        super(Viewer, self).__init__(parent)
        self.filename = None

        # Widgets
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setObjectName("tree")
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(['func', 'level', 'time', 'message'])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.acceptRejectBox = QtWidgets.QDialogButtonBox()
        self.acceptRejectBox.setOrientation(QtCore.Qt.Horizontal)
        self.acceptRejectBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.acceptRejectBox.setObjectName("acceptRejectBox")

        self.verticalLayout = QtWidgets.QVBoxLayout(central_widget)
        self.verticalLayout.addWidget(self.tree)
        self.verticalLayout.addWidget(self.acceptRejectBox)

        QtCore.QObject.connect(
            self.acceptRejectBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(
            self.acceptRejectBox, QtCore.SIGNAL("rejected()"), self.reject)

        # actions
        open_action = QtWidgets.QAction("&Open...", self)
        open_action.setShortcut(QtGui.QKeySequence.Open)
        open_action.setToolTip('Open an existing image file')
        open_action.triggered.connect(self.file_open)

        quit_action = QtWidgets.QAction("&Quit", self)
        quit_action.setShortcuts(["Ctrl+Q", "Esc"])
        quit_action.setToolTip('Close the application')
        quit_action.triggered.connect(self.reject)

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(open_action)
        self.fileMenu.addAction(quit_action)

        self.setWindowTitle("OnionLog Viewer")
        self.resize(900, 600)

        self.font_size = 12
        self.installEventFilter(self)

    def eventFilter(self, qobject, event):
        """
        Ctrl+scroll to resize
        """
        if event.type() == QtCore.QEvent.Wheel:
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ControlModifier:
                if event.delta() > 0:
                    self.font_size += 1
                elif self.font_size > 1:
                    self.font_size -= 1

                self.setStyleSheet('font-size: {}pt'
                                   ''.format(self.font_size))
                self.resize_columns()
                return True
            return False
        else:
            # standard event processing
            return False

    def file_open(self):
        dir_ = os.path.dirname(self.filename) if self.filename is not None else "."
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose File", dir_, "Onion Logs (*.olog)")
        if path:
            self.file_load(path[0])

    def file_load(self, path):

        onion = OnionLogger.load_from_disk(path)

        top_item = QtWidgets.QTreeWidgetItem([onion.name])
        self.tree.addTopLevelItem(top_item)
        top_item.setExpanded(True)

        for msg in onion.messages:
            entry = LoggerEntry(
                [msg._function,
                 str(msg._level),
                 time.ctime(msg._time),
                 msg.message]
            )
            entry.setSortData(2, msg._time)
            top_item.addChild(entry)

        self.resize_columns()

    def resize_columns(self):
        for i in range(4):
            self.tree.resizeColumnToContents(i)

    def accept(self):
        self.close()

    def reject(self):
        confirm = QtWidgets.QMessageBox(self)
        confirm.setWindowTitle("Quit?")
        confirm.setText("Are you sure you want to quit?")
        confirm.addButton("Yes, quit", QtWidgets.QMessageBox.AcceptRole)
        confirm.addButton("No", QtWidgets.QMessageBox.RejectRole)
        ret = confirm.exec_()

        if ret == QtWidgets.QMessageBox.RejectRole:
            return
        self.close()


class LoggerEntry(QtWidgets.QTreeWidgetItem):
    def __lt__(self, other):
        if not isinstance(other, LoggerEntry):
            return super(LoggerEntry, self).__lt__(other)

        tree = self.treeWidget()
        if not tree:
            column = 0
        else:
            column = tree.sortColumn()

        return self.sortData(column) < other.sortData(column)

    def __init__(self, *args):
        super(LoggerEntry, self).__init__(*args)
        self._sortData = {}

    def sortData(self, column):
        return self._sortData.get(column, self.text(column))

    def setSortData(self, column, data):
        self._sortData[column] = data


def run():
    app = QtWidgets.QApplication(sys.argv)
    #app.setWindowIcon(QtWidgets.QIcon(":/icons/NukeApp32.png"))
    f = Viewer()
    f.show()
    if len(sys.argv) > 1:
        f.file_load(sys.argv[-1])

    app.exec_()


if __name__ == '__main__':
    run()