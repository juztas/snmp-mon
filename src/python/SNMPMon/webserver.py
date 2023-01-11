import os
from prometheus_client import generate_latest, CollectorRegistry
from prometheus_client import Enum, Info, CONTENT_TYPE_LATEST
from prometheus_client import Gauge
import cherrypy
from SNMPMon.utilities import getConfig
from SNMPMon.utilities import getTimeRotLogger
from SNMPMon.utilities import getFileContentAsJson
from SNMPMon.utilities import isValFloat

class HTTPExpose():
    def __init__(self, config, logger=None):
        super().__init__()
        self.config = config
        self.logger = getTimeRotLogger(**config['logParams'])

    def startwork(self):
        """Start Cherrypy Worker"""
        cherrypy.server.socket_host = '0.0.0.0'
        cherrypy.quickstart(CherryPyThread(self.config))


class CherryPyThread():
    def __init__(self, config):
        self.config = config

    @cherrypy.expose
    def index(self):
        """Index Page"""
        return "Hello world!. Looking for something? :)"

    @staticmethod
    def __cleanRegistry():
        """Get new/clean prometheus registry."""
        registry = CollectorRegistry()
        return registry

    def __getLatestOutput(self):
        allfiles = os.listdir(self.config['tmpdir'])
        fname = ""
        if allfiles:
            needFile = True
            counter = -1
            while needFile:
                fname = allfiles[counter]
                if fname.endswith('.tmp'):
                    counter -= 1
                    continue
                needFile = False
            return getFileContentAsJson(os.path.join(self.config['tmpdir'], fname))
        return {}

    def __getSNMPData(self, registry, **kwargs):
        """Add SNMP Data to prometheus output"""
        # Here get info from DB for switch snmp details
        output = self.__getLatestOutput()
        if not output:
            return
        snmpGauge = Gauge('interface_statistics', 'Interface Statistics', ['ifDescr', 'ifType', 'ifAlias', 'hostname', 'Key'], registry=registry)
        for hostname, vals in output.items():
            for key, val in vals.items():
                keys = {'ifDescr': val.get('ifDescr', ''), 'ifType': val.get('ifType', ''), 'ifAlias': val.get('ifAlias', ''), 'hostname': hostname}
                for key1 in ['ifMtu', 'ifAdminStatus', 'ifOperStatus', 'ifHighSpeed', 'ifHCInOctets', 'ifHCOutOctets', 'ifInDiscards', 'ifOutDiscards',
                             'ifInErrors', 'ifOutErrors', 'ifHCInUcastPkts', 'ifHCOutUcastPkts', 'ifHCInMulticastPkts', 'ifHCOutMulticastPkts',
                             'ifHCInBroadcastPkts', 'ifHCOutBroadcastPkts']:
                    if key1 in val and isValFloat(val[key1]):
                        keys['Key'] = key1
                        snmpGauge.labels(**keys).set(val[key1])

    def __metrics(self):
        """Return all available Hosts, where key is IP address."""
        registry = self.__cleanRegistry()
        self.__getSNMPData(registry)
        data = generate_latest(registry)
        return iter([data])

    @cherrypy.expose
    def prometheus(self):
        """Return prometheus stats."""
        return self.__metrics()



if __name__ == '__main__':
    print("WARNING: Use this only for development!")
    config = getConfig('/etc/snmp-mon.yaml')
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(CherryPyThread(config))