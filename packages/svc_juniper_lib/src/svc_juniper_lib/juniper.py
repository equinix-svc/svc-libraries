from jnpr.junos import Device

from .junos_mx_routing_instance import MXRouteInstance
from .junos_mx_port_descriptions import MXPhysicalTable
from .junos_mx_port_descriptions import MXLogicalTable
from .junos_mx_chassis_hardware_sfp import MXChassisHardware
from .junos_qfx_vlan import QFXVlanTable
from .junos_qfx_ex_port_descriptions import QFXEXPhysicalTable
from .junos_qfx_ex_chassis_hardware_sfp import QFXEXChassisHardware
from .junos_mx_svc_public_routes import br1svcat1corpequinixcom
from .junos_mx_svc_public_routes import br1svcch3corpequinixcom
from .junos_mx_svc_public_routes import br1svcda6corpequinixcom
from .junos_mx_svc_public_routes import br1svcdc6corpequinixcom
from .junos_mx_svc_public_routes import br1svcla3corpequinixcom
from .junos_mx_svc_public_routes import br1svcmi1corpequinixcom
from .junos_mx_svc_public_routes import br1svcny5corpequinixcom
from .junos_mx_svc_public_routes import br1svcse3corpequinixcom
from .junos_mx_svc_public_routes import br1svcsv5corpequinixcom
from .junos_mx_svc_public_routes import svcbr1am3corpeuequinixcom
from .junos_mx_svc_public_routes import svcbr1fr4corpeuequinixcom
from .junos_mx_svc_public_routes import svcbr1ld5corpeuequinixcom
from .junos_mx_svc_public_routes import br1svchk2apequinixcom
from .junos_mx_svc_public_routes import br1svcos1apequinixcom
from .junos_mx_svc_public_routes import br1svcsg2apequinixcom
from .junos_mx_svc_public_routes import br1svcsy4apequinixcom
from .junos_mx_svc_public_routes import br1svcty4apequinixcom
from .junos_mx_svc_public_routes import br1svctr2corpequinixcom
from .junos_mx_version import MXVersion
from .junos_qfx_version import QFXVersion
from .junos_ex2200_version import EX2200Version
from .junos_ex3400_version import EX3400Version


# Juniper MX only: The purpose of this function is to return a dictionary of subinterfaces/vlans (key) and description
# (value) configured on the MX
# EXAMPLE: {2001: 'SVC: THOUSANDEYES AWS IPV4', 2002: 'SVC: THOUSANDEYES AZURE PRIMARY',
# 2107: 'POC: CISCO VIRTUAL LAB BD-5'}
def juniper_get_mx_interface_vlans_dictionary(fqdn, username, password):
    # Netconf session to a juniper device
    with Device(host=fqdn, user=username, password=password, port='22', timeout=300) as dev:
        ports = MXLogicalTable(dev)
        ports.get()

    # create a dictionary of subinterfaces/vlans (key) and the description (value)
    results = {}

    for key, value in ports.items():
        subinterface = key.split('.')

        if 'xe' in subinterface[0] or 'ge' in subinterface[0] or 'ae' in subinterface[0] or 'ms' in subinterface[0]:
            if 1 < int(subinterface[1]) < 4095:
                if value[0][1]:
                    results.update({int(subinterface[1]): value[0][1]})
                else:
                    results.update({int(subinterface[1]): 'None'})

    return results


# Juniper QFX only: The purpose of this function is to return a dictionary of vlan ids (key) and descriptions (value)
# configured on the QFX
# EXAMPLE: {3047: 'BILL_BLAKE_DEMO_3047', 3048: 'BILL_BLAKE_DEMO_3048', 3049: 'BILL_BLAKE_DEMO_3049',
# 3051: 'BILL_BLAKE_DEMO_3051'}
def juniper_get_qfx_vlans_dictionary(fqdn, username, password):
    # Netconf session to a juniper device
    with Device(host=fqdn, user=username, password=password, port='22', timeout=300) as dev:
        vlans = QFXVlanTable(dev)
        vlans.get()

    # create a dictionary of vlan tags (key) and vlan names (value)
    results = {}

    for key, value in vlans.items():
        results.update({int(key): value[0][1]})

    return results


# Juniper QFX only: The purpose of this function is to return a dictionary with the interface name (key) pointing to
# another dictionary (value) containing
# the interface description, type of SFP and the SFP speed
# EXAMPLE: {'ge-0/0/0': {'description': 'POC: LS5.SV5 0/1/1', 'speed': '1Gbps', 'type': 'SMF'}}
def juniper_get_qfx_interfaces(fqdn, username, password):

    # Netconf session to a juniper device
    with Device(host=fqdn, user=username, password=password, port='22', timeout=300) as dev:
        phy_port = QFXEXPhysicalTable(dev)
        sfp_info = QFXEXChassisHardware(dev)
        phy_port.get()
        sfp_info.get()

    # create a dictionary of interface names with another dictionary with port description, sfp type and speed
    results = {}
    for key, value in phy_port.items():
        if value[0][1] == None:
            results.update({key: {'description': ''}})
        else:
            results.update({key: {'description': value[0][1]}})
        # change 1000mbps to 1Gbps to match Netbox tag
        if value[1][1] == '1000mbps' or value[1][1] == '1000 Mbps':
            results[key]['speed'] = '1Gbps'
        elif value[1][1] == 'Auto':
            results[key]['speed'] = '10Gbps'
        elif value[1][1] == None:
            results[key]['speed'] = 'None'
        else:
            results[key]['speed'] = value[1][1]

        # for em interfaces set type to copper
        if 'em' in key:
            results[key]['type'] = 'copper'
        elif 'ae' in key:
            results[key]['type'] = 'lag'
    for key, value in sfp_info.items():
        # construct interface from fpc, pic, port and sfp description
        if '10G' in value[1][1]:
            type = 'xe-'
        else:
            type = 'ge-'
        fpc = value[4][1].replace('FPC ', '')
        pic = value[3][1].replace('PIC ', '')
        port = key.replace('Xcvr ', '')

        # match chassis hardware description to netbox tags
        if int(port) < 48:
            try:
                if value[1][1] == 'SFP+-10G-LR' or value[1][1] == 'SFP-LX10' or value[1][1] == 'QSFP+-40G-LR4':
                    results[type+fpc+'/'+pic+'/'+port]['type'] = 'SMF'
                elif value[1][1] == 'SFP+-10G-SR' or value[1][1] == 'SFP-SX':
                    results[type + fpc + '/' + pic + '/' + port]['type'] = 'MMF'
                else:
                    results[type + fpc + '/' + pic + '/' + port]['type'] = 'copper'
            except:
                pass
    return results


# Juniper MX only: The purpose of this function is to return a dictionary with the interface name (key) pointing to another dictionary (value) containing
# the interface description, type of SFP and the SFP speed
# EXAMPLE: {'ge-1/0/0': {'description': '', 'speed': '1Gbps', 'type': 'copper'},
def juniper_get_mx_interfaces(fqdn, username, password):
    # Netconf session to a juniper device
    with Device(host=fqdn, user=username, password=password, port='22',timeout=300) as dev:
        ports = MXPhysicalTable(dev)
        sfp = MXChassisHardware(dev)
        ports.get()
        sfp.get()
    # create a dictionary of interface names with another dictionary with port description, sfp type and speed
    results = {}
    for key, value in ports.items():
        if value[0][1] is None:
            results.update({key: {'description': ''}})
        else:
            results.update({key: {'description': value[0][1]}})

        # change 1000mbps to 1Gbps to match Netbox tag
        if value[1][1] == '1000mbps' or value[1][1] == '1000 Mbps':
            results[key]['speed'] = '1Gbps'
            results[key]['type'] = 'copper'
        else:
            results[key]['speed'] = value[1][1]

        # for ae interfaces set type to lag, anything else set to None
        if 'ae' in key:
            results[key]['type'] = 'lag'
        elif 'ge' in key:
            results[key]['type'] = 'copper'
        else:
            results[key]['type'] = 'No SFP'

    for key,value in sfp.items():
        #construct interface from fpc, pic, port and sfp description
        if '10G' in value[1][1]:
            type = 'xe-'
        else:
            type = 'ge-'
        fpc = value[4][1].replace('FPC ', '')
        pic = value[2][1].replace('PIC ', '')
        port = key.replace('Xcvr ', '')

        #match chassis hardware description to netbox tags
        try:
            if value[1][1] == 'SFP+-10G-LR' or value[1][1] == 'SFP-LX10' or value[1][1] == 'QSFP+-40G-LR4' or value[1][1] == 'XFP-10G-LR':
                results[type+fpc+'/'+pic+'/'+port]['type']='SMF'
            elif value[1][1] == 'SFP+-10G-SR' or value[1][1] == 'SFP-SX':
                results[type + fpc + '/' + pic + '/' + port]['type'] = 'MMF'
            else:
                results[type + fpc + '/' + pic + '/' + port]['type'] = 'copper'
        except:
            pass
    return results


# Juniper EX only: The purpose of this function is to return a dictionary with the interface name (key) pointing to another dictionary (value) containing
# the interface description, type of SFP and the SFP speed
# EXAMPLE: {'ge-0/1/0': {'description': 'SVC: CSW1-SVC.CH3 0/0/43', 'speed': '1Gbps', 'type': 'SMF'},
def juniper_get_ex_interfaces(fqdn, username, password):
    # Netconf session to a juniper device
    with Device(host=fqdn, user=username, password=password, port='22',timeout=300) as dev:
        ports = QFXEXPhysicalTable(dev)
        sfp = QFXEXChassisHardware(dev)
        ports.get()
        sfp.get()

    # create a dictionary of interface names with another dictionary with port description, sfp type and speed
    results = {}
    for key,value in ports.items():
        if value[0][1] == None:
            results.update({key: {'description': ''}})
        else:
            results.update({key:{'description':value[0][1]}})
        #change 1000mbps to 1Gbps to match Netbox tag
        if value[1][1] == '1000mbps' or value[1][1] == '1000 Mbps' or value[1][1] == 'Auto':
            results[key]['speed'] = '1Gbps'
            results[key]['type'] = 'copper'
        elif value[1][1] == '100mbps':
            results[key]['speed'] = '100mbps'
            results[key]['type'] = 'copper'
        else:
            results[key]['speed'] = value[1][1]

        # for ae interfaces set type to lag
        if 'ae' in key:
            results[key]['type'] = 'lag'

    for key,value in sfp.items():
        #construct interface from fpc, pic, port and sfp description
        if '10G' in value[1][1]:
            type = 'xe-'
        else:
            type = 'ge-'
        fpc = value[4][1].replace('FPC ', '')
        pic = value[3][1].replace('PIC ', '')
        port = key.replace('Xcvr ','')

        #match chassis hardware description to netbox tags
        if int(port) < 48:
            try:
                if value[1][1] == 'SFP+-10G-LR' or value[1][1] == 'SFP-LX10' or value[1][1] == 'QSFP+-40G-LR4':
                    results[type+fpc+'/'+pic+'/'+port]['type']='SMF'
                elif value[1][1] == 'SFP+-10G-SR' or value[1][1] == 'SFP-SX':
                    results[type + fpc + '/' + pic + '/' + port]['type'] = 'MMF'
                else:
                    results[type + fpc + '/' + pic + '/' + port]['type'] = 'copper'
            except:
                pass

    return results

# The purpose of this function to get all the public ips in use at a specfic SVC location
# EXAMPLE: {'64.191.201.2/31': 'SVC: THOUSANDEYES AWS IPV4', '64.191.201.4/30': 'SVC: THOUSANDEYES AZURE PRIMARY'}
# NOTE: PUBLIC NETWORKS ARE ADDED MANUALLY TO THE YML FILE
def juniper_get_mx_ipv4_public_routes(fqdn,site,username,password):
    # Netconf session to a juniper device
    with Device(host=fqdn, user=username, password=password, port='22', timeout=300) as dev:
        if site =='at1':
            routes = br1svcat1corpequinixcom(dev)
        elif site =='ch3':
            routes = br1svcch3corpequinixcom(dev)
        elif site =='da6':
            routes = br1svcda6corpequinixcom(dev)
        elif site =='dc6':
            routes = br1svcdc6corpequinixcom(dev)
        elif site =='la3':
            routes = br1svcla3corpequinixcom(dev)
        elif site =='mi1':
            routes = br1svcmi1corpequinixcom(dev)
        elif site =='ny5':
            routes = br1svcny5corpequinixcom(dev)
        elif site =='se3':
            routes = br1svcse3corpequinixcom(dev)
        elif site =='sv5':
            routes = br1svcsv5corpequinixcom(dev)
        elif site =='am3':
            routes = svcbr1am3corpeuequinixcom(dev)
        elif site =='fr4':
            routes = svcbr1fr4corpeuequinixcom(dev)
        elif site =='ld5':
            routes = svcbr1ld5corpeuequinixcom(dev)
        elif site =='hk2':
            routes = br1svchk2apequinixcom(dev)
        elif site =='os1':
            routes = br1svcos1apequinixcom(dev)
        elif site =='sg2':
            routes = br1svcsg2apequinixcom(dev)
        elif site =='sy4':
            routes = br1svcsy4apequinixcom(dev)
        elif site =='ty4':
            routes = br1svcty4apequinixcom(dev)
        elif site =='tr2':
            routes = br1svctr2corpequinixcom(dev)
        routes.get()

        ports = MXLogicalTable(dev)
        ports.get()

    # create a dictionary of routes and descriptions (based on interface description)
    results = {}
    for key, value in routes.items():
        if value[3][1] is None and value[4][1] is None:
            if value[2][1] in ports:
                results.update({key: ports[value[2][1]]['description']})
    return results


#This purpose of this function is to get the routing instance information from the MX router
#EXAMPLE: {'RI-BBVA': {'instance_type': 'vpls', 'route_distinguisher': '0:0', 'instance_interface': ['xe-2/0/1.3031', 'ae0.3031', 'xe-2/0/1.3030', 'ae0.3030']}}
def juniper_get_instance(fqdn, site, username, password):
    # Netconf session to a juniper device
    with Device(host=fqdn, user=username, password=password, port='22',timeout=300) as dev:
        instance=MXRouteInstance(dev)
        instance.get()

    results={}
    for key,value in instance.items():
        if '__' not in key and 'master' not in key and 'junos' not in key:
            if value[1][1]=='0:0':
                results.update({key: {'instance_type': value[0][1], 'route_distinguisher': None,
                                  'instance_interface': value[2][1]}})
            elif key == "RI-VRF-Internet-2":
                if value[1][1] == None:
                    results.update({site.upper() + ' ' + key: {'instance_type': value[0][1], 'route_distinguisher':value[1][1],
                                                                   'instance_interface': value[2][1]}})
                else:
                    results.update({site.upper()+' '+key: {'instance_type': value[0][1], 'route_distinguisher': site +' '+value[1][1],
                                                               'instance_interface': value[2][1]}})

            else:
                if value[1][1] == None:
                    results.update({key: {'instance_type': value[0][1], 'route_distinguisher': value[1][1],
                                          'instance_interface': value[2][1]}})
                else:
                    results.update(
                        {key: {'instance_type': value[0][1], 'route_distinguisher': site + ' ' + value[1][1],
                               'instance_interface': value[2][1]}})

    return results


#this will get the version of code on an MX
def juniper_get_mx_version(fqdn, username, password):

    dev = Device(host=fqdn, user=username, password=password, port='22',timeout=300).open()
    mx_version = MXVersion(dev)
    mx_version.get()

    results=mx_version[0].version
    return results



#this will get the version of code on an QFX
def juniper_get_qfx_version(fqdn, username, password):

    dev = Device(host=fqdn, user=username, password=password, port='22',timeout=300).open()
    qfx_version = QFXVersion(dev)
    qfx_version.get()

    results=qfx_version[0].version
    return results



#this will get the version of code on an EX3400
def juniper_get_ex3400_version(fqdn, username, password):

    dev = Device(host=fqdn, user=username, password=password, port='22',timeout=300).open()
    ex_version = EX3400Version(dev)
    ex_version.get()

    results=ex_version[0].version
    return results



#this will get the version of code on an EX2200
def juniper_get_ex2200_version(ip_address,username,password):

    dev = Device(host=ip_address, user=username, password=password, port='22',timeout=300).open()
    ex_version = EX2200Version(dev)
    ex_version.get()

    results=ex_version[0].version
    #extract only the version
    only_version = results[results.find('[')+1:results.find(']')]
    return only_version
