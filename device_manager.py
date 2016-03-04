from PyQt5.QtWidgets import QDialog
from device_manager_ui import Ui_Dialog
from learn import LearnDialog
from device import Device
from clip import verify_ext
from serializer import DeviceSerializer


class ManageDialog(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(ManageDialog, self).__init__(parent)
        self.gui = parent
        self.setupUi(self)
        for device in self.gui.devices[1:]:
            self.list.addItem(device.name)
        self.editButton.clicked.connect(self.onEdit)
        self.deleteButton.clicked.connect(self.onDelete)
        self.importButton.clicked.connect(self.onImport)
        self.exportButton.clicked.connect(self.onExport)
        self.finished.connect(self.onFinished)
        self.show()

    def onEdit(self):
        if self.list.currentRow() != -1:
            device = self.gui.devices[self.list.currentRow() + 1]
            self.gui.learn_device = LearnDialog(self.gui,
                                                self.updateDevice,
                                                device)
            self.gui.is_learn_device_mode = True

    def onDelete(self):
        if self.list.currentRow() != -1:
            device = self.gui.devices[self.list.currentRow() + 1]
            self.gui.devices.remove(device)
            self.list.takeItem(self.list.currentRow())

    def onImport(self):
        file_name, a = self.gui.getOpenFileName('Open Device',
                                                'Super Boucle Mapping (*.sbm)',
                                                self)
        with open(file_name, 'r') as f:
            read_data = f.read()
        device = DeviceSerializer.import_data(read_data)
        self.list.addItem(device.name)
        self.gui.devices.append(device)

    def onExport(self):
        device = self.gui.devices[self.list.currentRow() + 1]
        file_name, a = self.gui.getSaveFileName('Save Device',
                                                'Super Boucle Mapping (*.sbm)',
                                                self)
        if file_name:
            file_name = verify_ext(file_name, 'sbm')
            with open(file_name, 'w') as f:
                device_string = DeviceSerializer.export_data(device)
                f.write(device_string)

    def onFinished(self):
        self.gui.updateDevices()

    def updateDevice(self, device):
        self.list.clear()
        for device in self.gui.devices[1:]:
            self.list.addItem(device.name)
        self.gui.is_learn_device_mode = False
        self.gui.redraw()
