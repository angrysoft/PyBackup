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
        with open(configFile, 'r') as jconfig:
            conf = json.load(jconfig)
            t = conf.get('type')
            if t == 'dir':
                self._backupDir(conf)
            elif t == 'mariadb':
                if conf.get('mode') == 'dump':
                    self._backupMariadbDump(conf)
                elif conf.get('mode') == 'json':
                    self._backupMariadbJson(conf)

    def _backupDir(self, conf):
        compression = self._getCompressionType(conf.get('compression'))
        name = os.path.join(conf.get('backup_dir', '.'),
                            '{}_{}'.format(conf.get('name'), self._getTimeStamp()))
        self._info('Backup directory {}'.format(conf.get('path')))

        try:
            tar = tarfile.open(name=name, mode='w:{}'.format(compression))
            tar.add(conf.get('path'))
            if self.config.verbose:
                tar.list(verbose=True)
            tar.close()
        except PermissionError as err:
            self._info(err)
            tar.close()
            os.unlink(name)
        except FileNotFoundError as err:
            self._info(err)
            tar.close()
            os.unlink(name)

    def _backupMariadbDump(self, conf):
        args = ['mysqldump']
        name = 'mariadb'
        if conf.get('dbname') == '*' or not conf.get('dbname'):
            args.append('--all-databases')
        else:
            args.append(conf.get('dbname'))
            name = conf.get('dbname')
        args.append('-u')
        args.append(conf.get('user', 'root'))
        args.append('--password={}'.format(conf.get('password', '')))

        self._info('Dumping DB {}'.format(name))

        ret = subprocess.run(args, stdout=subprocess.PIPE)
        if ret.returncode == 0:
            self._saveToFile(conf.get('backup_dir', '.'),
                             name,
                             ret.stdout,
                             suffix='.sql',
                             compression=conf.get('compression'))
        else:
            self._info('Something was wrong :(')

    def _backupMariadbJson(self, conf):
        print('dumping json {}'.format(conf.get('dbname')))

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
    parser.add_argument('-d', '--dir', type=str, default='/etc/PyBackup/',
                        help='Directory path for config files')
    parser.add_argument('-c', '--configs', nargs='+', type=str,
                        help='Use list of configs in directory path')

    b = Backup(parser.parse_args())
    b.run()
