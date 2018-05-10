#!/usr/bin/python3
# Copyright 2018 Angrysoft (Sebastian Zwierzchowski) sebastian.zwierzchowski(AT)gmail DOT com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Sebastian Zwierzchowski'
__copyright__ = 'Copyright 2018 Angrysoft Sebastian Zwierzchowski'
__license__ = 'Apache 2.0'
__version__ = '1.0'

import signal
import argparse
import json
import sys
import os
import tarfile
import datetime
import subprocess
import gzip
import bz2
import lzma


class ValidationError(Exception):
    def __init__(self, value):
        self.value = 'Missing arg: '
        self.value += value

    def __str__(self):
        return repr(self.value)


class Config:
    def __init__(self, fileName):
        self.type = None
        self.backup_dir = None
        self.compression = None
        self.path = None
        self.name = None
        self.dbname = None
        self.mode = None
        self.user = None
        self.password = None

        args = {'all': ['type', 'backup_dir', 'compression'],
                'dir': ['path', 'name'],
                'files': ['path', 'name'],
                'mariadb': ['dbname', 'mode', 'user', 'password']}

        with open(fileName, 'r') as jconfig:
            conf = json.load(jconfig)
            for a in args['all']:
                if conf.get(a):
                    exec('self.{} = "{}"'.format(a, conf.get(a)))
                else:
                    raise ValidationError(a)
            for b in args.get(conf.get('type'), []):
                if conf.get(b):
                    exec('self.{} = conf.get(b)'.format(b,))
                else:
                    raise ValidationError(b)


class Backup:
    def __init__(self, config):
        self.config = config
        self.compressionTypes = ['gz', 'bz2', 'xz']

    def run(self):
        print(self.config)

        configPath = self.config.dir
        if os.path.isdir(configPath):
            if self.config.configs:
                configList = self.config.configs
            else:
                configList = os.listdir(configPath)

            for c in configList:
                if c.endswith('.json'):
                    self.parseConfig(os.path.join(configPath, c))
                else:
                    self._info('File "{}" not end with .json SKIPING'.format(c))
        else:
            self._info('Config directory not exitsts : {}'.format(configPath))

    def parseConfig(self, configFile):
        try:
            conf = Config(configFile)
        except ValidationError as err:
            self._error(err)
            return

        if conf.type == 'dir':
            self._backupDir(conf)
        elif conf.type == 'files':
            self._backupFiles(conf)
        elif conf.type == 'mariadb':
            if conf.mode == 'dump':
                self._backupMariadbDump(conf)
            elif conf.mode == 'json':
                self._backupMariadbJson(conf)
        else:
            self._error('not recogize type: {}'.format())

    def _backupDir(self, conf):
        compression = self._getCompressionType(conf.compression)
        # TODO hym nie podoba mi się to 
        suffix = ''
        if compression:
            suffix = '.{}'.format(compression)
        name = os.path.join(conf.backup_dir,
                            '{}_{}.tar'.format(conf.name, self._getTimeStamp()))
        self._info('Backup directory {}'.format(conf.path))

        try:
            tar = tarfile.open(name=name, mode='w:{}'.format(compression))
            tar.add(conf.path)
            if self.config.verbose:
                tar.list(verbose=True)
            tar.close()
        except PermissionError as err:
            self._error(err)
            tar.close()
            os.unlink(name)
        except FileNotFoundError as err:
            self._error(err)
            tar.close()
            os.unlink(name)

    def _backupFiles(self, conf):
        compression = self._getCompressionType(conf.compression)
        suffix = ''
        if compression:
            suffix = '.{}'.format(compression)

        name = os.path.join(conf.backup_dir,
                            '{}_{}.tar{}'.format(conf.name, self._getTimeStamp(), suffix))

        if not type(conf.path) == list:
            self._error('TypeError: path is not a list')
            print(conf.path, type(conf.path))
            return

        tar = tarfile.open(name=name, mode='w:{}'.format(compression))

        for f in conf.path:
            self._info('Backup file {}'.format(f))

            try:
                tar.add(f)
            except PermissionError as err:
                self._error(err)
                tar.close()
                os.unlink(name)
                break
            except FileNotFoundError as err:
                self._error(err)
                tar.close()
                os.unlink(name)
                break

        if self.config.verbose and not tar.closed:
            tar.list(verbose=True)
        tar.close()

    def _backupMariadbDump(self, conf):
        args = ['mysqldump']
        name = 'mariadb'
        if conf.dbname == '*' or not conf.dbname:
            args.append('--all-databases')
        else:
            args.append(conf.dbname)
            name = conf.dbname
        args.append('-u')
        args.append(conf.user)
        args.append('--password={}'.format(conf.password))

        self._info('Dumping DB {}'.format(name))

        ret = subprocess.run(args, stdout=subprocess.PIPE)
        if ret.returncode == 0:
            self._saveToFile(conf.backup_dir,
                             name,
                             ret.stdout,
                             suffix='.sql',
                             compression=conf.compression)
        else:
            self._info('Something was wrong :(')

    def _backupMariadbJson(self, conf):
        self._info('dumping json {}'.format(conf.dbname))

    def _saveToFile(self, path, name, data, suffix='', compression=None):
        output = os.path.join(path, '{}_{}{}'.format(name, self._getTimeStamp(), suffix))
        self._info('Saving file {}.gz'.format(output))
        if not type(data) == bytes:
            data = data.encode()

        if compression == 'gz':
            with gzip.open('{}.gz'.format(output), 'wb') as gzFile:
                gzFile.write(data)
        elif compression == 'bz2':
            with bz2.open('{}.bz2'.format(output), 'wb') as bzFile:
                bzFile.write(data)
        elif compression == 'xz':
            with lzma.open('{}.xz'.format(output), 'wb') as xzFile:
                xzFile.write(data)
        else:
            with open(output, 'wb') as oFile:
                oFile.write(data)

    def _getCompressionType(self, compression):
        if compression in self.compressionTypes:
            return compression
        else:
            return ''

    def _info(self, msg):
        if self.config.verbose:
            print('>> {}'.format(msg))

    def _error(self, msg):
        if not self.config.quiet:
            sys.stderr.write('!! {}\n'.format(msg))

    @staticmethod
    def _getTimeStamp():
        return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")


def stop_program(signal, frame):
    """stop_program"""
    print('\nExit Program')
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop_program)
    parser = argparse.ArgumentParser(usage='%(prog)s [options]')
    parser.add_argument('-v', '--verbose', action="store_true", help="verbose")
    parser.add_argument('-q', '--quiet', action="store_true", help="Be Quiet")
    parser.add_argument('-d', '--dir', type=str, default='/etc/PyBackup/',
                        help='Directory path for config files')
    parser.add_argument('-c', '--configs', nargs='+', type=str,
                        help='Use list of configs in directory path. Default use all .json')

    b = Backup(parser.parse_args())
    b.run()
