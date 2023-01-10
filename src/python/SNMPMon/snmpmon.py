#!/usr/bin/env python3
"""
    SNMPMonitoring gets all information from switches using SNMP
    Cloned and modified from SiteRM - to have it separated SNMPMon Process:
    https://github.com/sdn-sense/siterm/blob/master/src/python/SiteFE/SNMPMonitoring/snmpmon.py

Authors:
  Justas Balcas jbalcas (at) caltech.edu

Date: 2022/11/21
"""
import sys
import simplejson as json
from easysnmp import Session
from easysnmp.exceptions import EasySNMPUnknownObjectIDError
from easysnmp.exceptions import EasySNMPTimeoutError
from SNMPMon.utilities import getConfig
from SNMPMon.utilities import getTimeRotLogger

class SNMPMonitoring():
    """SNMP Monitoring Class"""
    def __init__(self, config, logger=None):
        super().__init__()
        self.config = config
        self.logger = getTimeRotLogger(**config['logParams'])

    def _writeOutFile(self, out):
        return out

    def startwork(self):
        """Scan all switches and get snmp data"""
        err = []
        jsonOut = {}
        for host in self.config['snmpMon']:
            if 'snmpParams' not in self.config['snmpMon'][host]:
                self.logger.info(f'Host: {host} config does not have snmpParams parameters.')
                continue
            session = Session(**self.config['snmpMon'][host]['snmpParams'])
            out = {}
            for key in ['ifDescr', 'ifType', 'ifMtu', 'ifAdminStatus', 'ifOperStatus',
                        'ifHighSpeed', 'ifAlias', 'ifHCInOctets', 'ifHCOutOctets', 'ifInDiscards',
                        'ifOutDiscards', 'ifInErrors', 'ifOutErrors', 'ifHCInUcastPkts',
                        'ifHCOutUcastPkts', 'ifHCInMulticastPkts', 'ifHCOutMulticastPkts',
                        'ifHCInBroadcastPkts', 'ifHCOutBroadcastPkts']:
                try:
                    allvals = session.walk(key)
                except EasySNMPUnknownObjectIDError as ex:
                    self.logger.warning(f'Got exception for key {key}: {ex}')
                    err.append(ex)
                    continue
                except EasySNMPTimeoutError as ex:
                    self.logger.warning(f'Got SNMP Timeout Exception: {ex}')
                    err.append(ex)
                    continue
                for item in allvals:
                    indx = item.oid_index
                    out.setdefault(indx, {})
                    out[indx][key] = item.value.replace('\x00', '')
            jsonOut[host] = out
        self._writeOutFile(out)
        if err:
            raise Exception(f'SNMP Monitoring Errors: {err}')


def execute(config=None):
    """Main Execute."""
    if not config:
        config = getConfig('/etc/snmp-mon.yaml')
    snmpmon = SNMPMonitoring(config)
    snmpmon.startwork()


if __name__ == '__main__':
    print('WARNING: ONLY FOR DEVELOPMENT!!!!. Number of arguments:', len(sys.argv), 'arguments.')
    print(sys.argv)
    execute()
