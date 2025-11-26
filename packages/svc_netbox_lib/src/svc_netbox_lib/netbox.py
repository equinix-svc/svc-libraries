import requests


def netbox_get_sites():
    """Return the list of supported SVC site identifiers.

    Returns
    -------
    list[str]
        A list of site codes (e.g. 'ld5', 'da6', 'ny5', ...).
    """
    svc_locations = ['ld5', 'dx1', 'da6', 'dc6', 'la3', 'mi1', 'ny5', 'se3', 'sv5', 'am3', 'ch3', 'fr4', 'at1', 'hk2',
                     'os1', 'sg2', 'sy4', 'ty4', 'tr2']
    return svc_locations


def netbox_get_fqdn(token, site, device):
    """Query NetBox for a device and return its FQDN/name.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    site : str
        Site identifier to filter devices by.
    device : str
        Search string for the device (e.g. 'br1', 'csw1').

    Returns
    -------
    str
        Device FQDN/name if found, otherwise the string 'none'.
    """
    myheaders = {'Authorization': 'Token ' + token}
    parameters = {'site': site, 'q': device}
    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/devices/', headers=myheaders, params=parameters)
    data = data.json()
    try:
        fqdn = data['results'][0]['name']
    except:
        fqdn = 'none'
    return fqdn


def netbox_get_vlan_dictionary(token, site, device):
    """Return a mapping of VLAN tag to NetBox VLAN ID for a site and device filter.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    site : str
        Site identifier to filter VLANs by.
    device : str
        Search/filter term for VLANs (passed as 'q' to the API).

    Returns
    -------
    dict[int, int] or dict
        Mapping of VLAN VID (int) -> NetBox VLAN object id (int). If the request fails or no data is present,
        returns {'none': 'none'}.
    """
    myheaders = {'Authorization' : 'Token '+ token}
    parameters = {'q' : device, 'site': site, 'limit' : 100000}
    data = requests.get('http://netbox.solutionvalidation.center/api/ipam/vlans/', headers=myheaders, params=parameters)
    data = data.json()
    results = {}
    try:
        for i in range(len(data['results'])):
            results.update({data['results'][i]['vid'] : data['results'][i]['id']})
    except:
        results = {'none': 'none'}
    return results


def netbox_delete_vlan(token, id):
    """Delete a VLAN object from NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    id : int
        NetBox VLAN object id to delete.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization' : 'Token '+ token, 'Content-Type': 'application/json'}
    data = requests.delete('http://netbox.solutionvalidation.center/api/ipam/vlans/'+ str(id)+ '/', headers=myheaders)
    return data.status_code


def netbox_post_vlan(token, payload):
    """Create a VLAN in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    payload : dict
        JSON payload for VLAN creation following NetBox API schema.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization' : 'Token '+ token, 'Content-Type': 'application/json'}
    data = requests.post('http://netbox.solutionvalidation.center/api/ipam/vlans/', headers=myheaders, json=payload)
    return data.status_code


def netbox_get_id(token, location, device):
    """Return the NetBox device id for a device matching location and name.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    location : str
        Site/location code to filter devices by.
    device : str
        Search string for the device.

    Returns
    -------
    int
        NetBox device id (raises if no results are found).
    """
    myheaders = {'Authorization': 'Token ' + token}
    parameters = {'q': device, 'site': location, 'tenant' : 'svc'}
    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/devices/', headers=myheaders, params=parameters)
    data = data.json()
    results = data['results'][0]['id']
    return results


def netbox_get_interfaces(token, id):
    """Fetch interfaces for a NetBox device and return a structured mapping.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    id : int
        NetBox device id to list interfaces for.

    Returns
    -------
    dict[str, dict]
        Mapping of interface name -> dict containing:
        - 'id' (int): NetBox interface id
        - 'description' (str)
        - 'type' (str): one of 'SMF', 'MMF', 'copper', 'lag', 'No SFP', etc.
        - 'speed' (str): human-readable speed tag
    """
    myheaders = {'Authorization' : 'Token '+ token}
    parameters = {'q' : '', 'device_id' : id, 'limit' : 100000}
    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/interfaces/', headers=myheaders, params=parameters)
    data = data.json()
    results = {}
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


def netbox_post_interface(token, payload):
    """Create one or more interfaces in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    payload : dict
        JSON payload for interface creation per NetBox API.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.post('http://netbox.solutionvalidation.center/api/dcim/interfaces/', headers=myheaders, json=payload)
    return data.status_code


def netbox_delete_interface(token, id):
    """Delete an interface from NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    id : int
        NetBox interface id to delete.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.delete('http://netbox.solutionvalidation.center/api/dcim/interfaces/'+ str(id)+ '/', headers=myheaders)
    return data.status_code


def netbox_patch_interface(token, interface_id, payload):
    """Patch/update an interface object in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    interface_id : int
        NetBox interface id to update.
    payload : dict
        JSON payload with fields to update.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.patch('http://netbox.solutionvalidation.center/api/dcim/interfaces/'+ str(interface_id)+'/', headers=myheaders, json=payload)
    return data.status_code


def netbox_get_ipv4_public_prefix(token, site):
    """Return the IPv4 public prefix role entry for a given site.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    site : str
        Site identifier (used to construct the role filter: '<site>-ipv4-public-ip-space').

    Returns
    -------
    str
        The prefix string (e.g. '64.191.201.0/24'), or an empty string if none found.
    """
    myheaders = {'Authorization' : 'Token '+ token}
    parameters = {'q' : '', 'role': site+'-ipv4-public-ip-space'}
    data = requests.get('http://netbox.solutionvalidation.center/api/ipam/prefixes/', headers=myheaders, params=parameters)
    data = data.json()
    results = ''
    for i in range(len(data['results'])):
        results = data['results'][i]['prefix']
    return results


def netbox_get_ipv4_public_routes(token, site):
    """Return IPv4 public addresses (children of the site's public prefix) from NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    site : str
        Site identifier to locate the parent public prefix.

    Returns
    -------
    dict[str, dict]
        Mapping of address (CIDR string) -> dict with keys 'id' and 'description'.
    """
    myheaders = {'Authorization' : 'Token '+ token}
    parent_prefix = netbox_get_ipv4_public_prefix(token, site)
    if parent_prefix == '':
        parent_prefix = '1.1.1.0/30'
    parameters = {'q' : '', 'parent': parent_prefix, 'limit' : 100000}
    data = requests.get('http://netbox.solutionvalidation.center/api/ipam/ip-addresses/', headers=myheaders, params=parameters)
    data = data.json()
    results={}
    for i in range(len(data['results'])):
        results.update({data['results'][i]['address']:{'id':data['results'][i]['id'], 'description': data['results'][i]['description']}})
    return results


def netbox_patch_ip_address(token, ip_id, payload):
    """Patch/update an IP address object in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    ip_id : int
        NetBox IP address object id to update.
    payload : dict
        JSON payload with fields to update (e.g. {'description': '...'}).

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.patch('http://netbox.solutionvalidation.center/api/ipam/ip-addresses/'+ str(ip_id)+'/', headers=myheaders, json=payload)
    return data.status_code


def netbox_post_ip_address(token, payload):
    """Create a new IP address in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    payload : dict
        JSON payload for IP creation (e.g. {'address': 'x.x.x.x/yy', 'description': '...', 'vrf': {...}}).

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.post('http://netbox.solutionvalidation.center/api/ipam/ip-addresses/', headers=myheaders, json=payload)
    return data.status_code


def netbox_delete_ip_address(token, ip_id):
    """Delete an IP address from NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    ip_id : int
        NetBox IP address object id to delete.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.delete('http://netbox.solutionvalidation.center/api/ipam/ip-addresses/'+ str(ip_id)+ '/', headers=myheaders)
    return data.status_code


def netbox_get_vrfs(token, site):
    """Return VRFs for a given site from NetBox with selected metadata.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    site : str
        Site identifier to filter VRFs by (custom field 'Site').

    Returns
    -------
    dict[str, dict]
        Mapping of VRF name -> dict with keys:
        - 'id' : NetBox VRF id
        - 'instance_type' : custom field 'type'
        - 'route_distinguisher' : rd (string)
        - 'instance_interface' : tags list
        - 'site' : custom field 'Site'
    """
    myheaders = {'Authorization' : 'Token '+ token, 'Content-Type': 'application/json'}
    parameters = {'q':'', 'cf_Site':site, 'limit' : 100000}
    data = requests.get('http://netbox.solutionvalidation.center/api/ipam/vrfs/',headers=myheaders, params=parameters)
    data = data.json()
    results={}
    for i in range(len(data['results'])):
        results.update({data['results'][i]['name']:{'id':data['results'][i]['id'],'instance_type':data['results'][i]['custom_fields']['type'],
                                                    'route_distinguisher':data['results'][i]['rd'],'instance_interface':data['results'][i]['tags'],
                                                    'site':data['results'][i]['custom_fields']['Site']}})
    return results


def netbox_post_vrf(token, payload):
    """Create a new VRF in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    payload : dict
        JSON payload for VRF creation per NetBox API.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.post('http://netbox.solutionvalidation.center/api/ipam/vrfs/', headers=myheaders, json=payload)
    return data.status_code


def netbox_patch_vrf(token, vrf_id, payload):
    """Patch/update a VRF object in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    vrf_id : int
        NetBox VRF object id to update.
    payload : dict
        JSON payload with fields to update.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.patch('http://netbox.solutionvalidation.center/api/ipam/vrfs/'+ str(vrf_id)+'/', headers=myheaders, json=payload)
    return data.status_code


def netbox_delete_vrf(token, vrf_id):
    """Delete a VRF from NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    vrf_id : int
        NetBox VRF object id to delete.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.delete('http://netbox.solutionvalidation.center/api/ipam/vrfs/'+ str(vrf_id)+ '/', headers=myheaders)
    return data.status_code


def netbox_get_platforms(token):
    """Return a list of platform names (software versions) from NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.

    Returns
    -------
    list[str]
        List of platform names as strings.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/platforms/', headers=myheaders)
    data = data.json()
    results = []
    for i in range(len(data['results'])):
        results.append(data['results'][i]['name'])
    return results


def netbox_post_platform(token, payload):
    """Create a new platform (software version) in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    payload : dict
        JSON payload for platform creation (e.g. {'name': ..., 'slug': ...}).

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.post('http://netbox.solutionvalidation.center/api/dcim/platforms/', headers=myheaders, json=payload)
    return data.status_code


def netbox_get_device_platform(token, device_id):
    """Get the current platform name and upgrade flag for a device in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    device_id : int
        NetBox device id.

    Returns
    -------
    tuple[str, Any]
        (platform_name, upgrade_flag) where platform_name is the platform name string or 'none'
        and upgrade_flag is the device's custom_fields['upgrade'] value or None.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.get('http://netbox.solutionvalidation.center/api/dcim/devices/'+ str(device_id)+'/', headers=myheaders)
    data = data.json()
    if data['platform'] is not None:
        platform = data['platform']['name']
        upgrade = data['custom_fields']['upgrade']
    else:
        platform = 'none'
        upgrade = None
    return platform, upgrade


def netbox_patch_device_platform(token, device_id, payload):
    """Patch/update the platform (software version) of a device in NetBox.

    Parameters
    ----------
    token : str
        NetBox API token for authentication.
    device_id : int
        NetBox device id.
    payload : dict
        JSON payload with platform update fields.

    Returns
    -------
    int
        HTTP status code returned by the NetBox API.
    """
    myheaders = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    data = requests.patch('http://netbox.solutionvalidation.center/api/dcim/devices/'+ str(device_id)+'/', headers=myheaders, json=payload)
    return data.status_code