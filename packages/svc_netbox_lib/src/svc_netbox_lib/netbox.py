import requests


def netbox_get_sites():
    """
    Get all sites from SVC
    """

    svc_locations = ['ld5', 'dx1', 'da6', 'dc6', 'la3', 'mi1', 'ny5', 'se3', 'sv5', 'am3', 'ch3', 'fr4', 'at1', 'hk2',
                     'os1', 'sg2', 'sy4', 'ty4', 'tr2']
    return svc_locations


# The purpose of this function is to return the fqdn of an internal network device (Juniper QFX,Juniper MX)
# all Equinix mx routers contain 'br1' in the fqdn.
# all Equinix qfx switches contain 'csw1' in the fqdn
# all Equinix ex switches contain 'ls1' in the fqdn
# Example: br1-svc.ch3.corp.equinix.com
def netbox_get_fqdn(token, site, device):

    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token}

    # filter for site, device role and tenant
    parameters = {'site': site, 'q': device}

    # API get for devices
    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/devices/', headers=myheaders, params=parameters)
    # convert response to python dictionary
    data = data.json()
    try:
        fqdn = data['results'][0]['name']
    except:
        fqdn = 'none'
    return fqdn


# The purpose of this function is to return a dictionary of vlans (key) and netbox id's (value) configured at a site
# EXAMPLE: {2000: 326, 2001: 327, 2002: 328, 2003: 329, 3000: 636, 3061: 337, 3062: 338, 3063: 339, 3064: 340}
def netbox_get_vlan_dictionary(token, site, device):

    # Netbox API key
    myheaders = {'Authorization' : 'Token '+ token}

    # filter for site, device_type_id
    parameters = {'q' : device, 'site': site, 'limit' : 100000}

    # API get for devices
    data = requests.get('http://netbox.solutionvalidation.center/api/ipam/vlans/', headers=myheaders, params=parameters)
    # convert response to python dictionary
    data = data.json()

   # create a dictionary of vlan names (key) pointing to another dictionary with Netbox id, vlan name
    results = {}
    try:
        for i in range(len(data['results'])):
            results.update({data['results'][i]['vid'] : data['results'][i]['id']})
    except:
        results = {'none': 'none'}
    return results


#This function will delete vlans from Netbox
def netbox_delete_vlan(token,id):

    # Netbox API key
    myheaders = {'Authorization' : 'Token '+ token, 'Content-Type': 'application/json'}

    data = requests.delete('http://netbox.solutionvalidation.center/api/ipam/vlans/'+ str(id)+ '/', headers=myheaders)

    return data.status_code


#This function will add a vlan to Netbox
def netbox_post_vlan(token,payload):

    # Netbox API key
    myheaders = {'Authorization' : 'Token '+ token, 'Content-Type': 'application/json'}

    data = requests.post('http://netbox.solutionvalidation.center/api/ipam/vlans/', headers=myheaders, json=payload)

    return data.status_code


# The purpose of this function is to return the device id from Netbox (EX,QFX,MX)
# EXAMPLE: 166
def netbox_get_id(token, location, device):

    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token}

    # filter for site, device role and tenant
    parameters = {'q': device, 'site': location, 'tenant' : 'svc'}

    # API get for devices
    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/devices/', headers=myheaders, params=parameters)
    # convert response to python dictionary
    data = data.json()
    # return device id
    results = data['results'][0]['id']

    return results


# The purpose of this function is to return a dictionary with the device name (key) pointing to another dictionary (value) containing
# the interface description, type of SFP and the SFP speed)
#EXAMPLE: {'ge-0/0/0': {'id': 3207, 'description': 'POC: LS5.SV5 0/1/1', 'type': 'SMF', 'speed': '1Gbps'}
def netbox_get_interfaces(token, id):
    # Netbox API key
    myheaders = {'Authorization' : 'Token '+ token}

    # filter for site, device role and tenant
    parameters = {'q' : '', 'device_id' : id, 'limit' : 100000}

    # API get for devices
    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/interfaces/', headers=myheaders, params=parameters)
    # convert response to python dictionary
    data = data.json()
    # create a dictionary of device names with another dictionary with Netbox id, port description, sfp type and speed
    results={}
    for i in range(len(data['results'])):
        if 'vcp' not in data['results'][i]['name'] and 'member' not in data['results'][i]['name'] and 'vlan' not in data['results'][i]['name']:
            results.update({data['results'][i]['name']:{'id':data['results'][i]['id'],'description':data['results'][i]['description'], 'type':'', 'speed':''}})

        for x in data['results'][i]['tags']:
            if x == 'SMF':
                results[data['results'][i]['name']]['type']='SMF'
            elif x == 'MMF':
                results[data['results'][i]['name']]['type'] = 'MMF'
            elif x == 'copper':
                results[data['results'][i]['name']]['type'] = 'copper'
            elif x == 'lag':
                results[data['results'][i]['name']]['type'] = 'lag'
            elif x == 'No SFP':
                results[data['results'][i]['name']]['type'] = 'No SFP'
            elif x == '100mbps':
                results[data['results'][i]['name']]['speed'] = '100mbps'
            elif x == '100 Mbps':
                results[data['results'][i]['name']]['speed'] = '100 Mbps'
            elif x == '1Gbps':
                results[data['results'][i]['name']]['speed'] = '1Gbps'
            elif x == '10Gbps':
                results[data['results'][i]['name']]['speed'] = '10Gbps'
            elif x == '20Gbps':
                results[data['results'][i]['name']]['speed'] = '20Gbps'
            elif x == '30Gbps':
                results[data['results'][i]['name']]['speed'] = '30Gbps'
            elif x == '40Gbps':
                results[data['results'][i]['name']]['speed'] = '40Gbps'
            elif x == 'Unspecified':
                results[data['results'][i]['name']]['speed'] = 'Unspecified'
            elif x == 'None':
                results[data['results'][i]['name']]['speed'] = 'None'

    return results


#This function will add interfaces to a Netbox device
#EXAMPLE PAYLOAD: {'ae4': {'device': {'id': 274}, 'name': 'None', 'type': 'lag'}}
def netbox_post_interface(token,payload):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.post('http://netbox.solutionvalidation.center/api/dcim/interfaces/', headers=myheaders, json=payload)

    return data.status_code


#This function will delete an interface from Netbox
def netbox_delete_interface(token,id):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.delete('http://netbox.solutionvalidation.center/api/dcim/interfaces/'+ str(id)+ '/', headers=myheaders)

    return data.status_code


# This function will patch interface configuration within Netbox
def netbox_patch_interface(token,interface_id,payload):

    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    # filter for site, device role and tenant
    parameters = {'id': interface_id}

    # API patch for interfaces
    data = requests.patch('http://netbox.solutionvalidation.center/api/dcim/interfaces/'+ str(interface_id)+'/', headers=myheaders, json=payload)

    return data.status_code


#the purpose of this function is to return the ipv4 public prefix for a particular location
def netbox_get_ipv4_public_prefix(token,site):
    # Netbox API key
    myheaders = {'Authorization' : 'Token '+ token}

    # filter for site, device_type_id
    parameters = {'q' : '', 'role': site+'-ipv4-public-ip-space'}

    # API get for devices
    data = requests.get('http://netbox.solutionvalidation.center/api/ipam/prefixes/', headers=myheaders, params=parameters)
    # convert response to python dictionary
    data = data.json()

    results = ''
    for i in range(len(data['results'])):
        results = data['results'][i]['prefix']

    return results


#This purpose of this function is to return a dictionary of routes (key)
#EXAMPLE: {'64.191.201.1/32': {'id': 67, 'description': ''}, '64.191.201.2/31': {'id': 68, 'description': ''}}
#NOTE: PUBLIC NETWORKS ARE ADDED MANUALLY BELOW
def netbox_get_ipv4_public_routes(token, site):
    # Netbox API key
    myheaders = {'Authorization' : 'Token '+ token}

    parent_prefix = netbox_get_ipv4_public_prefix(token, site)

    #dummy prefix if nothing is returned
    if parent_prefix == '':
        parent_prefix = '1.1.1.0/30'

     # filter for site, device_type_id
    parameters = {'q' : '', 'parent': parent_prefix, 'limit' : 100000}

    # API get for devices
    data = requests.get('http://netbox.solutionvalidation.center/api/ipam/ip-addresses/', headers=myheaders, params=parameters)
    #print(data.url)
    # convert response to python dictionary
    data = data.json()
    #print(data)

    results={}
    for i in range(len(data['results'])):
        results.update({data['results'][i]['address']:{'id':data['results'][i]['id'], 'description': data['results'][i]['description']}})
    return results


#This function will patch an netbox ipaddress
#EXAMPLE: {'address': '64.191.201.2/31', 'description': 'SVC: THOUSANDEYES AWS IPV4'}
def netbox_patch_ip_address(token,ip_id,payload):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.patch('http://netbox.solutionvalidation.center/api/ipam/ip-addresses/'+ str(ip_id)+'/', headers=myheaders, json=payload)

    return data.status_code



#This function will add ip addresses to a Netbox device
#EXAMPLE PAYLOAD: {'address': '64.191.201.254/31', 'description': 'SVC: SCIENCELOGIC INTERNET CONNECTION', 'vrf': {'name': 'CH3 RI-VRF-Internet-2'}
def netbox_post_ip_address(token,payload):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.post('http://netbox.solutionvalidation.center/api/ipam/ip-addresses/', headers=myheaders, json=payload)

    return data.status_code



#This function will delete ip addresses not needed in Netbox
def netbox_delete_ip_address(token,ip_id):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.delete('http://netbox.solutionvalidation.center/api/ipam/ip-addresses/'+ str(ip_id)+ '/', headers=myheaders)

    return data.status_code


#The purpose of this function is to get a dictionary of VRFs
#NOTE: Netbox Tags will be populated with associated Juniper routing-instances
#EXAMPLE: {'AM3 RI-AZURE-MARKETPLACE': {'id': 118,'instance_type': None, 'route_distinguisher': None, 'instance_interface': []}}
def netbox_get_vrfs(token,site):

    # Netbox API key
    myheaders = {'Authorization' : 'Token '+ token, 'Content-Type': 'application/json'}

    # filter for site, device role and tenant
    parameters = {'q':'', 'cf_Site':site, 'limit' : 100000}

    # API patch for interfaces
    data = requests.get('http://netbox.solutionvalidation.center/api/ipam/vrfs/',headers=myheaders, params=parameters)
    data = data.json()

    results={}
    for i in range(len(data['results'])):
        results.update({data['results'][i]['name']:{'id':data['results'][i]['id'],'instance_type':data['results'][i]['custom_fields']['type'],
                                                    'route_distinguisher':data['results'][i]['rd'],'instance_interface':data['results'][i]['tags'],
                                                    'site':data['results'][i]['custom_fields']['Site']}})
    return results


#This function will post a new vrf to Netbox
#EXAMPLE PAYLOAD: {'RI-BBVA': {'name': 'RI-BBVA', 'rd': '0:0', 'tags': ['xe-2/0/1.3031', 'ae0.3031', 'xe-2/0/1.3030', 'ae0.3030'],
#                   'custom_fields': {'Site': 'dc6', 'type': 'vpls'}}
def netbox_post_vrf(token,payload):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.post('http://netbox.solutionvalidation.center/api/ipam/vrfs/', headers=myheaders, json=payload)

    return data.status_code


#This function will patch the circuit information in Netbox
#EXAMPLE PAYLOAD: {'name': 'DC6 RI-VRF-Internet-2', 'custom_fields': {'Type': 'vrf'}}
def netbox_patch_vrf(token,vrf_id,payload):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.patch('http://netbox.solutionvalidation.center/api/ipam/vrfs/'+ str(vrf_id)+'/', headers=myheaders, json=payload)

    return data.status_code


#This function will delete an existing vrf in Netbox
#Example vrf_id: 14
def netbox_delete_vrf(token,vrf_id):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.delete('http://netbox.solutionvalidation.center/api/ipam/vrfs/'+ str(vrf_id)+ '/', headers=myheaders)

    return data.status_code


#This function is designed to get a list of software versions (platforms) in Netbox
#EXAMPLE: ['14.1X53-D44.3', '14.1X53-D46.7', '5.3.9', 'ESXi 5.5.0', 'ESXi 6.5', 'JUNOS 16.1R6.7', 'JUNOS 17.3R3.10', 'KVM/QEMU']
def netbox_get_platforms(token):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/platforms/', headers=myheaders)
    data=data.json()
    results=[]
    for i in range(len(data['results'])):
        results.append(data['results'][i]['name'])
    return results



#This function will add a new platform (software version) to Netbox
#EXAMPLE Payload: {'name': '17.3R3.10', 'slug': '17-3R3-10'}
def netbox_post_platform(token,payload):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.post('http://netbox.solutionvalidation.center/api/dcim/platforms/', headers=myheaders, json=payload)

    return data.status_code



#This function will get the current platform (software version) of a device in Netbox
#EXAMPLE {'id': 19, 'url': 'http://netbox.solutionvalidation.center/api/dcim/platforms/19/', 'name': '17.3R3.10', 'slug': '17-3R3-10'}
def netbox_get_device_platform(token, device_id):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/devices/'+ str(device_id)+'/', headers=myheaders)
    data=data.json()
    if data['platform'] is not None:
        platform = data['platform']['name']
        upgrade = data['custom_fields']['upgrade']
    else:
        platform = 'none'
        upgrade = None
    return platform,upgrade


#This function will update the platform (software version) of a device in netbox
def netbox_patch_device_platform(token, device_id, payload):
    # Netbox API key
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}

    data = requests.patch('http://netbox.solutionvalidation.center/api/dcim/devices/'+ str(device_id)+'/', headers=myheaders, json=payload)
    return data.status_code
