import json
import pickle
from device import Device
from PyQt5.QtCore import QSettings


class SBSerializer:
    __VERSION__ = 1

    def __init__(self, raw_data):
        self.raw_data = raw_data.copy()

    def check_upgrade(self):
        version = self.version
        if version < self.__VERSION__:
            upgrade_method = getattr(self, 'upgrade{}'.format(version),
                                     lambda: self.upgrade(version))
            upgrade_method()
        elif version > self.__VERSION__:
            msg = 'Trying to load data from a newer Version of SuperBoucle. ' \
                  'Consider Upgrading SuperBoucle.'
            raise self.OutdatedException(version, msg)
        return self.raw_data

    @property
    def version(self):
        return self.raw_data.get('__VERSION__', 0)

    def set_version(self):
        self.raw_data['__VERSION__'] = self.__VERSION__
        return self.raw_data

    def upgrade(self, from_data_version):
        raise NotImplementedError

    @classmethod
    def import_data(cls, data):
        raise NotImplementedError

    @classmethod
    def export_data(cls, device):
        raise NotImplementedError

    @classmethod
    def load_data(cls):
        raise NotImplementedError

    @classmethod
    def save_data(cls, data):
        raise NotImplementedError

    class OutdatedException(Exception):
        def __init__(self, version, message):
            super().__init__(message)
            self.version = version


class DeviceSerializer(SBSerializer):
    @classmethod
    def import_data(cls, data):
        serializer = cls(json.loads(data))
        mapping = serializer.check_upgrade()
        return Device(mapping)

    @classmethod
    def export_data(cls, device):
        assert isinstance(device, Device)
        export_mapping = cls(device.mapping).set_version()
        return json.dumps(export_mapping)

    @classmethod
    def load_data(cls):
        device_settings = QSettings('superboucle', 'devices')
        devices = []
        if ((device_settings.contains('devices')
             and device_settings.value('devices'))):
            for raw_device in device_settings.value('devices'):
                raw_data = pickle.loads(raw_device)
                mapping = cls(raw_data).check_upgrade()
                devices.append(Device(mapping))
        else:
            devices.append(Device({'name': 'No Device',}))

        return devices

    @classmethod
    def save_data(cls, data):
        device_settings = QSettings('superboucle', 'devices')
        v_data = [cls(dev.mapping).set_version() for dev in data]

        device_settings.setValue('devices',
                                 [pickle.dumps(x) for x in v_data])

    def upgrade(self, from_data_version):
        print('Upgrading Device from version {} to {}'
              ''.format(from_data_version, self.__VERSION__))
