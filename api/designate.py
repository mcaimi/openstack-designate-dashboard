# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Python Wrapper for openstack designate. Used in the DNS as a service plugin
# v.0.1 - Initial Implementation - Marco Caimi <marco.caimi@fastweb.it>

import logging
from keystoneauth1.identity import v2 as v2_plugin
from keystoneauth1.identity import v3 as v3_plugin
from keystoneauth1 import session as keystone_session
from django.conf import settings

# import base api library from openstack dashboard codebase
from openstack_dashboard.api import base as api_base
from openstack_dashboard.api import keystone
from horizon.utils import functions as utils
from horizon.utils.memoized import memoized

# import designate SDK libraries
from designateclient.v2 import client as designate_client

LOG = logging.getLogger(__name__)

KS_VERSION = api_base.APIVersionManager("identity", preferred_version=3)
VERSION = api_base.APIVersionManager("dns", preferred_version=2)
try:
    VERSION.load_supported_version(2, {"client": designate_client, "version": 2})
except ImportError:
    LOG.error("VERSION.load_supported_versions FAILED.")

DEBUGLOG=True
def logwrap_info(message):
    if DEBUGLOG:
        LOG.info("DESIGNATE API WRAPPER: %s" % message)

# wrapper around designate DNS as a service API set
@memoized
def designateclient(request):
    token = request.user.token.id

    if keystone.get_version() < 3:
        tenant_id = request.user.tenant_id
        logwrap_info("using keystone v2.")
        # keystone auth object
        auth = v2_plugin.Token(auth_url="https://%s:5000/v2.0" % settings.OPENSTACK_HOST, 
                                tenant_id=tenant_id, 
                                token=token)
    else:
        project_id = request.user.project_id
        project_domain_id = request.session.get('domain_context')
        logwrap_info("using keystone v3.")
        auth = v3_plugin.Token(auth_url="https://%s:5000/v3" % settings.OPENSTACK_HOST,
                                token=token,
                                project_id=project_id,
                                project_domain_id=project_domain_id)

    # create a session
    ks_session = keystone_session.Session(auth=auth)

    # spawn designate client object
    dns_client = designate_client.Client(session=ks_session)

    logwrap_info("Created a new DNSaaS API Client Object.")
    return dns_client

def get_zones(request):
    logwrap_info("Querying API service for a list of zones.")
    return designateclient(request).zones.list()

def get_zone(request, zone=None):
    if zone==None:
        raise ValueError

    logwrap_info("Querying API service for info on zone %s" % zone)
    return designateclient(request).zones.get(zone)

def create_zone(request, name, email=None, ttl=None, description=None):
    try:
        logwrap_info("Creating zone %s." % name)
        designateclient(request).zones.create(name=name, email=email, ttl=ttl, description=description)
    except Exception as e:
        raise e

def update_zone(request, zone, data):
    try:
        logwrap_info("Updating zone %s." % zone)
        designateclient(request).zones.update(zone=zone, values=data)
    except Exception as e:
        raise e

def delete_zone(request, zone):
    try:
        logwrap_info("Deleting zone %s." % zone)
        designateclient(request).zones.delete(zone=zone)
    except Exception as e:
        raise e

def get_recordsets(request, zone):
    logwrap_info("Querying API for a list of recordsets in zone %s." % zone)
    return designateclient(request).recordsets.list(zone=zone)

def get_record(request, zone, record):
    logwrap_info("Querying API for a info on recordset %s in zone %s." % (record, zone))
    return designateclient(request).recordsets.get(zone, record)

def create_recordset(request, zone, name, type_, records, description=None, ttl=None):
    try:
        logwrap_info("Creating recordset %s in zone %s." % (name, zone))
        designateclient(request).recordsets.create(zone=zone, name=name, type_=type_, records=records, description=description, ttl=ttl)
    except Exception as e:
        raise e

def update_recordset(request, zone, recordset, values):
    try:
        logwrap_info("Updating recordset %s in zone %s." % (recordset, zone))
        designateclient(request).recordsets.update(zone=zone, recordset=recordset, values=values)
    except Exception as e:
        raise e

def delete_recordset(request, zone, recordset):
    try:
        logwrap_info("Deleting recordset %s in zone %s." % (recordset, zone))
        designateclient(request).recordsets.delete(zone=zone, recordset=recordset)
    except Exception as e:
        raise e

