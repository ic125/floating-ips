#!/usr/bin/python

import os
import sys
import requests
import json
import time
import sys

command = sys.argv[1]

######################### Variables from the config #########################

with open('/opt/floatingIP/api.conf') as f:
    for line in f.readlines():
        if 'tenantId' in line:
            tenantId = line.split('=')[1].strip()
        if 'client_id' in line:
            client_id = line.split('=')[1].strip()
        if 'client_secret' in line:
            client_secret = line.split('=')[1].strip()
        if 'ip' in line:
            ip = line.split('=')[1].strip()
        if 'cidr' in line:
            cidr = int(line.split('=')[1].strip())
        if 'local_hostname' in line:
            vm_hostname = line.split('=')[1].strip()
        if 'local_product' in line:
            local_product = line.split('=')[1].strip()
        if 'remote_product' in line:
            remote_product = line.split('=')[1].strip()
##############################################################################

def IP2Int(ip):     ## Simple IP string to integer conversion
    o = map(int, ip.split('.'))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res

def get_token():    ## Getting token for further step on all required scopes
    url = 'https://iam-proxy.heficed.com/oauth2/token'
    data = {'grant_type': 'client_credentials', 'scope': 'kronoscloud ipswitch protocompute'}
    r = requests.post(url, data=data, auth=(client_id, client_secret))
    resp = r.json()
    return resp['access_token']

def subnet_to_id(): ## Recursive subnet search. Heficed API (at the time script is writen) doesn't support recursive search.
    ip_found = False
    parentUID = ""
    while ip_found == False:
        url = 'https://api.heficed.com/' + tenantId + '/ipswitch/v4/subnets?parentUuid=' + parentUID
        r = requests.get(url, headers=auth_header)
        resp = r.json()
        for x in range(len(resp['data'])):
            if resp['data'][x]['address'] <= IP2Int(ip) <= resp['data'][x]['lastAddress']:
                if resp['data'][x]['cidr'] == cidr:
                    ip_found = True
                    subnet_id = resp['data'][x]['id']
                    if "instanceId" in resp['data'][x]['metadata']['switch']:
                        current_vm = resp['data'][x]['metadata']['switch']['instanceId']
                        print("Subnet is assigned to some machine")
                    else:
                        print("Subnet is not assigned")
                        current_vm = "none"
                    break
                else:
                    parentUID = resp['data'][x]['id']
    return subnet_id, current_vm;

def vm_to_id():     ## Converting machine hostname to service id)
    vm_id = ""
    if local_product == "kronoscloud":
        url = 'https://api.heficed.com/' + tenantId + '/kronoscloud/instances'
    elif  local_product == "protocompute":
        url = 'https://api.heficed.com/' + tenantId + '/protocompute/instances/premium'
    r = requests.get(url, headers=auth_header)
    resp = r.json()
    for x in range(len(resp['data'])):
        if resp['data'][x]['hostname'] == vm_hostname:
            vm_id = resp['data'][x]['id']
    return vm_id

def reassign_subnet():## Definition that reassigns subnet
    url_u = 'https://api.heficed.com/' + tenantId + '/ipswitch/v4/subnets/release/' + remote_product + '/' + str(current_vm)
    url_a = 'https://api.heficed.com/' + tenantId + '/ipswitch/v4/subnets/route/' + local_product + '/' + str(vm_id)
    data = [subnet_id]
    print('Current machine is ' + str(current_vm) + ' and to be machine is ' + str(vm_id))
    if current_vm != "none":
        r = requests.post(url_u, headers=auth_header, data=json.dumps(data))
        print r
        time.sleep(4) ## After subnet unassign request is done, next request must be done after a delay, otherwise errors occur.
    r = requests.post(url_a, headers=auth_header, data=json.dumps(data))
    print r
    sys.exit(0)

def vm_subnet_check(bad_exit):
    if vm_id == current_vm:
        print("subnet is on the VM")
        sys.exit(0)
    else:
        print("subnet is not on the VM")
        if bad_exit == "status":
            sys.exit(1)
        if bad_exit == "monitor":
            sys.exit(7)

##################################### MAIN #####################################
## Mandatory requests
if command == "monitor": ## Delay to fix monitor error right after assignment
    time.sleep(7)
auth_header = {'Authorization': get_token()}
subnet_id, current_vm = subnet_to_id()
vm_id = vm_to_id()

## Script options
if command == "status":
    vm_subnet_check(command)
elif command == "monitor":
    vm_subnet_check(command)
elif command == "start":
    reassign_subnet()
