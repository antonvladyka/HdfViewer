# -*- coding: utf-8 -*-
"""
Created on Sun May  9 17:33:55 2021

@author: anvlad
"""

# ------------------------------------------------- ----- 
# ---------------------- main.py ------------------- ---- 
# --------------------------------------------- --------- 
from  PyQt5.QtWidgets  import QMainWindow, QApplication, QTreeWidgetItem, QFileDialog
from  PyQt5.uic  import  loadUi
from PyQt5.QtCore import Qt, QAbstractTableModel#QObject, pyqtSignal, QRunnable, QThreadPool#, pyqtSlot
#from PyQt5.QtGui import QFont
#import time
import  numpy  as  np 
#import  random
import h5py

class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)
        #return self._data.shape[0]

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])
        #return self._data.shape[1]
            
class Window(QMainWindow):
    
    def  __init__(self):
        QMainWindow.__init__(self)
        loadUi("hdfviewer.ui" , self)
        self.btnOpen.clicked.connect(self.open)
        
    
    def open(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Load HDF file", "",
                                                  "HDF files (*.hdf, *.hdf5);;All files (*.*)", options=options)
        if fileName:
            f = h5py.File(fileName, "r")
            self.f = f
            self.s = Window.hdfanalyse(f)
            self.treeWidget.setColumnCount(2)
            self.treeWidget.setHeaderLabels(['key', 'shape'])
            self.addRow(self.s, self.treeWidget)
            self.treeWidget.itemClicked.connect(self.showData)
            
    
    def addRow(self, x, parent):
        if self.cboxLimit.isChecked():
            keys = list(x.keys())[:100]
        else:
            keys = list(x.keys())
        for key in keys:
            w = QTreeWidgetItem(parent)
            w.setText(0, key)
            if not type(x[key]) is tuple:
                self.addRow(x[key], w)
                w.setExpanded(False)
            else:
                w.setText(1, str(x[key]))    
            self.treeWidget.setCurrentItem(w)
   
    def showData(self):
        w = self.treeWidget.currentItem()
        if w.childCount() == 0:
            keys = []
            while not w is None:
                keys.append(w.data(0,0))
                w = w.parent()
            keys = keys[::-1]
            data = self.f[keys[0]]
            for key in keys[1:]:
                data = data[key]
            data = data[()]
            if data.ndim == 1:
                data = data[:, None]
            elif data.ndim == 0:
                data = np.array([[data]])
            self.model = TableModel(data.tolist())
            self.tableView.setModel(self.model)
            
    @staticmethod
    def hdfanalyse(file):
        keys = file.keys()
        s = {}
        for key in keys:
            if isinstance(file[key], h5py.Dataset):
                if file[key].ndim == 0:
                    s[key] = (1, 1)
                else:
                    s[key] = file[key].shape
            elif isinstance(file[key], h5py.Group):
                s[key] = Window.hdfanalyse(file[key])
        return s

    def closeEvent(self, event):
        # then stop the app
        event.accept()
        
        
app = QApplication([]) 
window = Window() 


window.show() 
app.exec_()