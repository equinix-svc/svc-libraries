import ipaddress

from ..netbox import netbox
from ..juniper import juniper


# The purpose of this function is get all vlans from the Juniper QFX/MX, compare to the exisiting vlans in Netbox
# Then add/delete vlans in Netbox
def sync_mx_qfx_netbox_vlans(token, site, username, password):
    """Synchronize VLANs between Juniper QFX/MX devices and NetBox for a site.

    This function:
    - Queries the QFX for VLANs and the MX for subinterface VLANs.
    - Queries NetBox for VLANs keyed to the same site and device filters.
    - Creates NetBox VLAN objects for VLANs present on the devices but missing in NetBox.
    - Deletes NetBox VLAN objects that no longer exist on the devices.

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier (e.g. 'ch3', 'ny5').
    username : str
        Username for Juniper device authentication.
    password : str
        Password for Juniper device authentication.

    Returns
    -------
    None
    """
    # get qfx vlan information from Juniper QFX
    fqdn = netbox.netbox_get_fqdn(token, site, 'csw1')
    juniper_qfx_dictionary = juniper.juniper_get_qfx_vlans_dictionary(fqdn, username, password)

    # get mx subinterface information
    fqdn = netbox.netbox_get_fqdn(token, site, 'br1')
    juniper_mx_dictionary = juniper.juniper_get_mx_interface_vlans_dictionary(fqdn, username, password)

    # get qfx vlan information from Netbox
    netbox_qfx_vlans_dictionary = netbox.netbox_get_vlan_dictionary(token, site, 'qfx')

    # get mx vlan information from Netbox
    netbox_mx_vlans_dictionary = netbox.netbox_get_vlan_dictionary(token, site, 'mx')

    # add new qfx vlans to netbox
    for key, value in juniper_qfx_dictionary.items():
        if key not in netbox_qfx_vlans_dictionary:
            payload = {'site': {'name': site.upper()}, 'vid': key, 'name': value, 'description': 'qfx'}
            netbox.netbox_post_vlan(token, payload)

    # remove qfx netbox vlans that no longer appear on the qfx switch
    for key, value in netbox_qfx_vlans_dictionary.items():
        if key not in juniper_qfx_dictionary:
            netbox.netbox_delete_vlan(token, value)

    # add new mx vlans to netbox
    for key, value in juniper_mx_dictionary.items():
        if key not in netbox_mx_vlans_dictionary:
            payload = {'site': {'name': site.upper()}, 'vid': key, 'name': value, 'description': 'mx'}
            netbox.netbox_post_vlan(token, payload)

    # remove mx netbox vlans that no longer appear on the mx switch
    for key, value in netbox_mx_vlans_dictionary.items():
        if key not in juniper_mx_dictionary:
            netbox.netbox_delete_vlan(token, value)


# The purpose of this function is to synchronize Juniper QFX interfaces and Netbox.
# This function will add/delete interfaces from Netbox based on what is configured on the Juniper QFX
def sync_qfx_interfaces(token, site, username, password):
    """Synchronize QFX device interfaces with NetBox.

    This function:
    - Retrieves interface metadata from a Juniper QFX (description, speed, type).
    - Retrieves interfaces for the corresponding NetBox device.
    - Adds interfaces missing in NetBox.
    - Updates tags (speed/type) and descriptions when they differ.
    - Deletes NetBox interfaces that no longer exist on the device.

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier.
    username : str
        Juniper device username.
    password : str
        Juniper device password.

    Returns
    -------
    None
    """
    # get qfx interface information from Juniper QFX
    fqdn = netbox.netbox_get_fqdn(token, site, 'csw1')
    juniper_qfx_dictionary = juniper.juniper_get_qfx_interfaces(fqdn, username, password)

    # get qfx interface information from Netbox
    device_id = netbox.netbox_get_id(token, site, 'csw1')
    netbox_qfx_dictionary = netbox.netbox_get_interfaces(token, device_id)

    # add any missing qfx ports to the qfx device in Netbox
    # update any speed, type, description changes
    for key, value in juniper_qfx_dictionary.items():
        # add any missing qfx ports to the qfx device in Netbox
        if key not in netbox_qfx_dictionary:
            if 'em' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': '1000base-x-sfp', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
            elif 'xe' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': '10gbase-x-sfpp', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
            elif 'ge' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': '1000base-x-sfp', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
            elif 'ae' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': 'lag', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
        # update any speed, type, description changes
        elif (value['speed'] != netbox_qfx_dictionary[key]['speed'] or
              value['type'] != netbox_qfx_dictionary[key]['type']):
            payload = {'tags': [value['speed'], value['type']]}
            netbox.netbox_patch_interface(token, netbox_qfx_dictionary[key]['id'], payload)
        elif value['description'] != netbox_qfx_dictionary[key]['description']:
            payload = {'description': value['description']}
            netbox.netbox_patch_interface(token, netbox_qfx_dictionary[key]['id'], payload)

    # remove any qfx interfaces from Netbox that no longer exist on the qfx switch
    for key, value in netbox_qfx_dictionary.items():
        if key not in juniper_qfx_dictionary:
            netbox.netbox_delete_interface(token, value['id'])


# The purpose of this function is to synchronize Juniper MX interfaces and Netbox.
# This function will add/delete interfaces from Netbox based on what is configured on the Juniper MX
def sync_mx_interfaces(token, site, username, password):
    """Synchronize MX device interfaces with NetBox.

    This function:
    - Retrieves MX interface and SFP data from the device.
    - Retrieves NetBox interfaces for the MX device.
    - Adds missing interfaces to NetBox.
    - Updates tags (speed/type) and descriptions when they differ.
    - Deletes NetBox interfaces that no longer exist on the MX (except management).

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier.
    username : str
        Juniper device username.
    password : str
        Juniper device password.

    Returns
    -------
    None
    """
    # determine MX ip address and device id
    fqdn = netbox.netbox_get_fqdn(token, site, 'br1')
    device_id = netbox.netbox_get_id(token, site, 'br1')

    # get mx interface information from Juniper MX
    juniper_mx_dictionary = juniper.juniper_get_mx_interfaces(fqdn, username, password)

    # get mx interface information from Netbox
    netbox_mx_dictionary = netbox.netbox_get_interfaces(token, device_id)

    # add any missing mx ports to the mx device in Netbox
    # update any speed, type, description changes
    for key, value in juniper_mx_dictionary.items():
        # add any missing mx ports to the mx device in Netbox
        if key not in netbox_mx_dictionary:
            if 'xe' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': '10gbase-x-sfpp', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
            elif 'ge' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': '1000base-x-sfp', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
            elif 'ae' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': 'lag', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
        # update any speed, type, description changes
        elif value['speed'] != netbox_mx_dictionary[key]['speed'] or value['type'] != netbox_mx_dictionary[key]['type']:
            payload = {'tags': [value['speed'], value['type']]}
            netbox.netbox_patch_interface(token, netbox_mx_dictionary[key]['id'], payload)
        elif value['description'] != netbox_mx_dictionary[key]['description']:
            payload = {'description': value['description']}
            netbox.netbox_patch_interface(token, netbox_mx_dictionary[key]['id'], payload)

    # remove any mx interfaces from Netbox that no longer exist on the mx router
    for key, value in netbox_mx_dictionary.items():
        if key != 'MGMT':
            if key not in juniper_mx_dictionary:
                netbox.netbox_delete_interface(token, value['id'])


# The purpose of this function is to synchronize Juniper EX interfaces and Netbox.
# This function will add/delete interfaces from Netbox based on what is configured on the Juniper EX
def sync_ex_interfaces(token, site, username, password):
    """Synchronize EX device interfaces with NetBox.

    This function:
    - Retrieves EX interface and SFP data from the device.
    - Retrieves NetBox interfaces for the EX device.
    - Adds missing interfaces to NetBox.
    - Updates tags (speed/type) and descriptions when they differ.
    - Deletes NetBox interfaces that no longer exist on the EX.

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier.
    username : str
        Juniper device username.
    password : str
        Juniper device password.

    Returns
    -------
    None
    """
    # get ex interface information from Juniper EX
    fqdn = netbox.netbox_get_fqdn(token, site, 'ls1')
    juniper_ex_dictionary = juniper.juniper_get_ex_interfaces(fqdn, username, password)

    # get ex interface information from Netbox
    device_id = netbox.netbox_get_id(token, site, 'ls1')
    netbox_ex_dictionary = netbox.netbox_get_interfaces(token, device_id)

    for key, value in juniper_ex_dictionary.items():
        # check for interfaces found on Juniper but not in Netbox
        if key not in netbox_ex_dictionary:
            if 'xe' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': '10gbase-x-sfpp', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
            elif 'ge' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': '1000base-x-sfp', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)
            elif 'ae' in key:
                payload = {'device': {'id': device_id}, 'name': key, 'description': value['description'],
                           'type': 'lag', 'tags': [value['speed'], value['type']]}
                netbox.netbox_post_interface(token, payload)

        # update any speed, type, description changes
        elif (value['speed'] != netbox_ex_dictionary[key]['speed'] or
              value['type'] != netbox_ex_dictionary[key]['type']):
            payload = {'tags': [value['speed'], value['type']]}
            netbox.netbox_patch_interface(token, netbox_ex_dictionary[key]['id'], payload)
        elif value['description'] != netbox_ex_dictionary[key]['description']:
            payload = {'description': value['description']}
            netbox.netbox_patch_interface(token, netbox_ex_dictionary[key]['id'], payload)

    # remove any ex interfaces from Netbox that no longer exist on the ex switch
    for key, value in netbox_ex_dictionary.items():
        if key not in juniper_ex_dictionary:
            netbox.netbox_delete_interface(token, value['id'])


# The purpose of this function is to get all public ipv4 networks from the Juniper MX and compare to what is configured in Netbox
# Then add/delete individual ipv4 entries in Netbox
def sync_mx_netbox_public_ipv4_routes(token, site, username, password):
    """Synchronize public IPv4 routes between an MX device and NetBox for a site.

    This function:
    - Retrieves public route prefixes configured on the MX (site-specific YML models).
    - Expands each network into individual addresses and maps them to interface descriptions.
    - Patches NetBox IP objects where descriptions changed.
    - Creates NetBox IP objects that are present on the device but missing in NetBox.
    - Deletes NetBox IP objects that are no longer present on the device.

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier.
    username : str
        Juniper device username.
    password : str
        Juniper device password.

    Returns
    -------
    None
    """
    # get public ipv4 routes from juniper
    fqdn = netbox.netbox_get_fqdn(token, site, 'br1')
    juniper_routes = juniper.juniper_get_mx_ipv4_public_routes(fqdn, site, username, password)

    # get public ipv4 routes from Netbox
    netbox_routes = netbox.netbox_get_ipv4_public_routes(token, site)

    # create a dictionary of all ips in use with descriptions
    # EXAMPLE: {'64.191.201.2/31': 'SVC: THOUSANDEYES AWS IPV4', '64.191.201.3/31': 'SVC: THOUSANDEYES AWS IPV4'}
    juniper_routes_expanded = {}
    for key, value in juniper_routes.items():
        mask = key[-3:]
        for addr in ipaddress.ip_network(key):
            juniper_routes_expanded.update({str(addr) + mask: value})

    # Patch routes that need to be updated
    # add new routes
    for key, value in juniper_routes_expanded.items():
        if key in netbox_routes and value != netbox_routes[key]['description'] and value is not None:
            payload = {'address': key, 'description': value}
            netbox.netbox_patch_ip_address(token, key, payload)
        elif key not in netbox_routes:
            if value is None:
                payload = {'address': key, 'description': '', 'vrf': {'name': site.upper() + ' RI-VRF-Internet-2'}}
                netbox.netbox_post_ip_address(token, payload)
            else:
                payload = {'address': key, 'description': value, 'vrf': {'name': site.upper() + ' RI-VRF-Internet-2'}}
                netbox.netbox_post_ip_address(token, payload)

    # delete routes that are no longer in the mx
    for key, value in netbox_routes.items():
        if key not in juniper_routes_expanded:
            netbox.netbox_delete_ip_address(token, value['id'])


# This function will synchronize Juniper routing instances with Netbox VRFs
def sync_netbox_mx_vrfs(token, site, username, password):
    """Synchronize Juniper MX routing-instances with NetBox VRFs for a site.

    This function:
    - Retrieves routing-instances from the MX and VRFs from NetBox.
    - Creates missing VRFs in NetBox based on MX routing-instances.
    - Updates VRF attributes (RD, type, tags/instance interfaces, site) when they differ.
    - Deletes VRFs from NetBox that no longer exist on the MX.

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier.
    username : str
        Juniper device username.
    password : str
        Juniper device password.

    Returns
    -------
    None
    """
    # get routing-instances from Juniper MX
    fqdn = netbox.netbox_get_fqdn(token, site, 'br1')
    juniper_instances = juniper.juniper_get_instance(fqdn, site, username, password)

    # get vrfs from Netbox
    netbox_vrfs = netbox.netbox_get_vrfs(token, site)

    # identify missing vrfs and vrfs that need corrections
    for key, value in juniper_instances.items():
        interface_list = []
        if value['instance_interface'] == None:
            pass
        elif isinstance(value['instance_interface'], list):
            interface_list = value['instance_interface']
        else:
            interface_list = [value['instance_interface']]

        if key not in netbox_vrfs:
            payload = {'name': key, 'rd': value['route_distinguisher'], 'tags': interface_list,
                       'custom_fields': {'Site': site, 'type': value['instance_type']}}
            netbox.netbox_post_vrf(token, payload)

        try:
            if value['route_distinguisher'] != netbox_vrfs[key]['route_distinguisher']:
                payload = {'name': key, 'rd': value['route_distinguisher']}
                netbox.netbox_patch_vrf(token, netbox_vrfs[key]['id'], payload)
        except:
            pass
        try:
            if value['instance_type'] != netbox_vrfs[key]['instance_type']:
                payload = {'name': key, 'custom_fields': {'type': value['instance_type']}}
                netbox.netbox_patch_vrf(token, netbox_vrfs[key]['id'], payload)
        except:
            pass
        try:
            for i in interface_list:
                if i not in netbox_vrfs[key]['instance_interface']:
                    payload = {'name': key, 'tags': interface_list}
                    netbox.netbox_patch_vrf(token, netbox_vrfs[key]['id'], payload)
            for i in netbox_vrfs[key]['instance_interface']:
                if i not in interface_list:
                    payload = {'name': key, 'tags': interface_list}
                    netbox.netbox_patch_vrf(token, netbox_vrfs[key]['id'], payload)
        except:
            pass
        try:
            if site != netbox_vrfs[key]['site']:
                payload = {'name': key, 'custom_fields': {'Site': site}}
                netbox.netbox_patch_vrf(token, netbox_vrfs[key]['id'], payload)
        except:
            pass

    # find all vrfs that should be removed from Netbox
    for key, value in netbox_vrfs.items():
        if key not in juniper_instances:
            netbox.netbox_delete_vrf(token, value['id'])


# The purpose of this function is to synchronize software version between Juniper Networking devices and Netbox
def sync_mx_platform_version(token, site, username, password):
    """Ensure the NetBox platform entry and device platform match the Juniper MX software version.

    This function:
    - Reads the software version from the MX.
    - Ensures the version exists in NetBox platforms (creates it if missing).
    - Updates the device platform in NetBox if it does not match the MX.
    - Clears any 'upgrade' custom field if the versions already match.

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier.
    username : str
        Juniper device username.
    password : str
        Juniper device password.

    Returns
    -------
    None
    """
    # get mx corp ip address from Netbox
    fqdn = netbox.netbox_get_fqdn(token, site, 'br1')

    # get netbox device id
    device_id = netbox.netbox_get_id(token, site, 'br1')

    # get version from MX
    mx_version = juniper.juniper_get_mx_version(fqdn, username, password)

    # Get the current platform (software version) of the device according to Netbox
    mx_platform_netbox, mx_platform_upgrade = netbox.netbox_get_device_platform(token, device_id)

    # get all platform versions from Netbox
    all_platforms = netbox.netbox_get_platforms(token)

    # add version to Netbox if not in Netbox
    if mx_version not in all_platforms:
        slug_version = mx_version.replace('.', '-')
        new_platform = {'name': mx_version, 'slug': slug_version}
        netbox.netbox_post_platform(token, new_platform)

    # change version in Netbox to match MX
    if mx_version != mx_platform_netbox:
        if mx_platform_upgrade == None:
            payload = {'platform': {'name': mx_version}}
            netbox.netbox_patch_device_platform(token, device_id, payload)

    # remove upgrade status since versions match
    elif mx_version == mx_platform_netbox:
        if mx_platform_upgrade != None:
            payload = {'custom_fields': {'upgrade': None}}
            netbox.netbox_patch_device_platform(token, device_id, payload)


# The purpose of this function is to synchronize software version between Juniper Networking devices and Netbox
def sync_qfx_platform_version(token, site, username, password):
    """Ensure the NetBox platform entry and device platform match the Juniper QFX software version.

    Behavior and parameters mirror sync_mx_platform_version but operate on the QFX device ('csw1').

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier.
    username : str
        Juniper device username.
    password : str
        Juniper device password.

    Returns
    -------
    None
    """
    # get qfx corp ip address from Netbox
    fqdn = netbox.netbox_get_fqdn(token, site, "csw1")

    # get netbox device id
    device_id = netbox.netbox_get_id(token, site, "csw1")

    # get version from MX
    qfx_version = juniper.juniper_get_qfx_version(fqdn, username, password)

    # Get the current platform (software version) of the device according to Netbox
    qfx_platform_netbox, qfx_platform_upgrade = netbox.netbox_get_device_platform(token, device_id)

    # get all platform versions from Netbox
    all_platforms = netbox.netbox_get_platforms(token)

    # add any missing versions to Netbox
    if qfx_version not in all_platforms:
        slug_version = qfx_version.replace('.', '-')
        new_platform = {'name': qfx_version, 'slug': slug_version}
        netbox.netbox_post_platform(token, new_platform)

    # find version mismatch
    if qfx_version != qfx_platform_netbox:
        if qfx_platform_upgrade == None:
            payload = {'platform': {'name': qfx_version}}
            netbox.netbox_patch_device_platform(token, device_id, payload)

    elif qfx_version == qfx_platform_netbox:
        if qfx_platform_upgrade != None:
            payload = {'custom_fields': {'upgrade': None}}
            netbox.netbox_patch_device_platform(token, device_id, payload)


# The purpose of this function is to synchronize software version between Juniper Networking devices and Netbox
def sync_ex_platform_version(token, site, username, password):
    """Ensure the NetBox platform entry and device platform match the Juniper EX software version.

    This function:
    - Detects EX model (EX3400 vs EX2200) and reads version accordingly.
    - Ensures the version exists in NetBox platforms (creates if missing).
    - Updates the device platform in NetBox if it does not match the device.
    - Clears any 'upgrade' custom field when versions match.

    Parameters
    ----------
    token : str
        NetBox API token.
    site : str
        Site identifier.
    username : str
        Juniper device username.
    password : str
        Juniper device password.

    Returns
    -------
    None
    """
    # get ex corp ip address from Netbox
    fqdn = netbox.netbox_get_fqdn(token, site, "ls1")

    # get netbox device id
    device_id = netbox.netbox_get_id(token, site, "ls1")

    # get version from EX
    # switch in TR2 is a ex3400
    if 'tr2' in fqdn:
        ex_version = juniper.juniper_get_ex3400_version(fqdn, username, password)
    else:
        ex_version = juniper.juniper_get_ex2200_version(fqdn, username, password)

    # Get the current platform (software version) of the device according to Netbox
    ex_platform_netbox, ex_platform_upgrade = netbox.netbox_get_device_platform(token, device_id)

    # get all platform versions from Netbox
    all_platforms = netbox.netbox_get_platforms(token)

    # if version on ex switch not in Netbox, add it to Netbox platform table
    if ex_version not in all_platforms:
        slug_version = ex_version.replace('.', '-')
        new_platform = {'name': ex_version, 'slug': slug_version}
        netbox.netbox_post_platform(token, new_platform)

    # update Netbox device with version currently on the juniper ex
    if ex_version != ex_platform_netbox:
        if ex_platform_upgrade == None:
            payload = {'platform': {'name': ex_version}}
            netbox.netbox_patch_device_platform(token, device_id, payload)

    # remove upgrade flag if versions match
    elif ex_version == ex_platform_netbox:
        if ex_platform_upgrade != None:
            payload = {'custom_fields': {'upgrade': None}}
            netbox.netbox_patch_device_platform(token, device_id, payload)