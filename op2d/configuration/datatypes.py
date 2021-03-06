
import os
import re

from sipsimple.configuration.datatypes import List

from op2d.resources import ApplicationData

__all__ = ['ApplicationDataPath', 'CustomSoundFile', 'DefaultPath', 'SoundFile', 'SpeedDialingList']


class ApplicationDataPath(unicode):

    def __new__(cls, path):
        path = os.path.normpath(path)
        if path.startswith(ApplicationData.directory+os.path.sep):
            path = path[len(ApplicationData.directory+os.path.sep):]
        return unicode.__new__(cls, path)

    @property
    def normalized(self):
        return ApplicationData.get(self)


class DefaultPath(object):

    def __repr__(self):
        return self.__class__.__name__


class SoundFile(object):

    def __init__(self, path, volume=100):
        self.path = path
        self.volume = int(volume)
        if not (0 <= self.volume <= 100):
            raise ValueError('illegal volume level: %d' % self.volume)

    def __getstate__(self):
        return u'%s,%s' % (self.__dict__['path'], self.volume)

    def __setstate__(self, state):
        try:
            path, volume = state.rsplit(u',', 1)
        except ValueError:
            self.__init__(state)
        else:
            self.__init__(path, volume)

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.path, self.volume)

    def _get_path(self):
        return ApplicationData.get(self.__dict__['path'])
    def _set_path(self, path):
        path = os.path.normpath(path)
        if path.startswith(ApplicationData.directory+os.path.sep):
            path = path[len(ApplicationData.directory+os.path.sep):]
        self.__dict__['path'] = path
    path = property(_get_path, _set_path)
    del _get_path, _set_path


class CustomSoundFile(object):

    def __init__(self, path=DefaultPath, volume=100):
        self.path = path
        self.volume = int(volume)
        if not (0 <= self.volume <= 100):
            raise ValueError('illegal volume level: %d' % self.volume)

    def __getstate__(self):
        if self.path is DefaultPath:
            return u'default'
        else:
            return u'file:%s,%s' % (self.__dict__['path'], self.volume)

    def __setstate__(self, state):
        match = re.match(r'^(?P<type>default|file:)(?P<path>.+?)?(,(?P<volume>\d+))?$', state)
        if match is None:
            raise ValueError('illegal value: %r' % state)
        data = match.groupdict()
        if data.pop('type') == 'default':
            data['path'] = DefaultPath
        data['volume'] = data['volume'] or 100
        self.__init__(**data)

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.path, self.volume)

    def _get_path(self):
        path = self.__dict__['path']
        return path if path is DefaultPath else ApplicationData.get(path)
    def _set_path(self, path):
        if path is not DefaultPath:
            path = os.path.normpath(path)
            if path.startswith(ApplicationData.directory+os.path.sep):
                path = path[len(ApplicationData.directory+os.path.sep):]
        self.__dict__['path'] = path
    path = property(_get_path, _set_path)
    del _get_path, _set_path


class SpeedDialingEntry(object):

    def __init__(self, name, uri):
        if '|' in name:
            raise ValueError('invalid entry name: %s' % name)
        self.name = name
        self.uri = str(uri)

    def __getstate__(self):
        return u'%s|%s' % (self.name, self.uri)

    def __setstate__(self, state):
        name, uri = state.split(u'|', 1)
        self.__init__(name, uri)

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.name, self.uri)

    @classmethod
    def from_description(cls, value):
        name, uri = value.split(u'|', 1)
        return cls(name, uri)


class SpeedDialingList(List):
    type = SpeedDialingEntry

