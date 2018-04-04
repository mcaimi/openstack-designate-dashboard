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

import logging

from django.template import defaultfilters
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
from django.core.urlresolvers import reverse,reverse_lazy, NoReverseMatch

from horizon import tables,exceptions,messages
from openstack_dashboard.api import designate as designate_bridge
from openstack_dashboard import policy

# policy engine support
# make sure a "domain_admin" role is created in openstack keystone
DESIGNATE_POLICY_ATOMS = {
            'dns_get_quota': ("dns", "get_quota"),
            'dns_get_quotas': ("dns", "get_quotas"),
            'get_zone': ("dns", "get_zone"),
            'get_zones': ("dns", "get_zones"),
            'find_zone': ("dns", "find_zone"),
            'find_zones': ("dns", "find_zones"),
            'zone_create': ("dns", "create_zone"),
            'zone_update': ("dns", "update_zone"),
            'zone_delete': ("dns", "delete_zone"),
            'recordset_create': ("dns", "create_recordset"),
            'recordset_update': ("dns", "update_recordset"),
            'recordset_delete': ("dns", "delete_recordset"),
            'get_recordset': ("dns", "get_recordset"),
            'get_recordsets': ("dns", "get_recordsets"),
            'find_recordset': ("dns", "find_recordsets"),
            'find_recordsets': ("dns", "find_recordsets"),
        }

DNS_POLICIES = {
            'zone_create': (DESIGNATE_POLICY_ATOMS['zone_create'], DESIGNATE_POLICY_ATOMS['get_zones'], DESIGNATE_POLICY_ATOMS['find_zones'],),
            'zone_update': (DESIGNATE_POLICY_ATOMS['get_zone'], DESIGNATE_POLICY_ATOMS['find_zone'], DESIGNATE_POLICY_ATOMS['zone_update'],),
            'zone_delete': (DESIGNATE_POLICY_ATOMS['get_zone'], DESIGNATE_POLICY_ATOMS['find_zone'], DESIGNATE_POLICY_ATOMS['zone_delete'],),
            'recordset_create': (DESIGNATE_POLICY_ATOMS['get_recordsets'], DESIGNATE_POLICY_ATOMS['find_recordsets'], DESIGNATE_POLICY_ATOMS['recordset_create']),
            'recordset_update': (DESIGNATE_POLICY_ATOMS['get_recordset'], DESIGNATE_POLICY_ATOMS['find_recordset'], DESIGNATE_POLICY_ATOMS['recordset_update']),
            'recordset_delete': (DESIGNATE_POLICY_ATOMS['get_recordsets'], DESIGNATE_POLICY_ATOMS['find_recordsets'], DESIGNATE_POLICY_ATOMS['recordset_delete']),
        }

LOG = logging.getLogger(__name__)
ALLOWED_RECORD_TYPES = ['A', 'AAAA', 'PTR', 'CNAME', 'MX', 'SRV', 'TXT', 'SPF']

class DnsData(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for k in kwargs:
            setattr(self, k, kwargs.get(k))

        self.record_data = None
        if getattr(self, 'records', None) is not None:
            self.record_data = ", ".join(self.records)

# create zone button link handler
class ZoneCreateLink(tables.LinkAction):
    name = "zonecreate"
    verbose_name = _("Add a DNS Zone")
    url = "horizon:project:dns:zonecreate"
    classes = ("ajax-modal",)
    icon = "plus"

    def allowed(self, request, datum):
        outcome = policy.check(DNS_POLICIES['zone_create'], request)
        LOG.info("POLICY %s (type %s) CHECK ZONE CREATE %s" % (DNS_POLICIES['zone_create'], type(DNS_POLICIES['zone_create']), outcome))
        return outcome

# zone update link handler
class ZoneUpdateLink(tables.LinkAction):
    name = "zoneupdate"
    verbose_name = _("Update DNS Zone")
    url = "horizon:project:dns:zoneupdate"
    classes = ("ajax-modal",)
    icon = "pencil"

    def allowed(self, request, datum):
        outcome = policy.check(DNS_POLICIES['zone_update'], request)
        LOG.info("POLICY %s (type %s) CHECK ZONE UPDATE %s" % (DNS_POLICIES['zone_update'], type(DNS_POLICIES['zone_update']), outcome))
        return outcome


# zone delete button link handler
class ZoneDeleteLink(tables.DeleteAction):
    name = "zonedelete"
    success_url = reverse_lazy("horizon:project:dns:index")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete DNS Zone",
            u"Delete DNS Zone",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"DNS Zone Delete Accepted",
            u"DNS Zone Delete Accepted",
            count
        )

    def allowed(self, request, datum):
       outcome = policy.check(DNS_POLICIES['zone_delete'], request)
       LOG.info("POLICY CHECK ZONE DELETE %s" % outcome)
       return outcome

    def delete(self, request, obj_id):
        designate_bridge.delete_zone(request, obj_id)

class UpdateZoneRow(tables.Row):
    ajax = True
    table = 'dns'

    def get_data(self, request, zone_id):
        try:
            zone_instance = designate_bridge.get_zone(request, zone_id)
        except Exception:
            zone_instance = None
            exceptions.handle(request,
                              _('Error getting information from API '
                                'for dns zone "%s".') % zone_id,
                              ignore=True)

        if zone_instance is not None:
            zone_object = DnsData(**zone_instance)
        else:
            zone_object = DnsData(**{'id': None, 'name': None, 'email': None, 'status': "deleted", 'action': None, 'ttl': None, 'serial': None, 'description': None})

        return zone_object

class UpdateRecordRow(tables.Row):
    ajax = True
    table = 'recordsets'

    def __init__(self, table, datum=None):
        super(UpdateRecordRow, self).__init__(table, datum)
        self.datum = datum

    def get_data(self, request, obj_id):
        try:
            record_instance = designate_bridge.get_recordsets(request, obj_id)
        except Exception:
            record_instance = None
            exceptions.handle(request,
                              _('Error getting information from API '
                                'for dns record "%s".') % obj_id, ignore=True)

        if record_instance is not None:
            record_object = DnsData(**record_instance)
        else:
            record_object = DnsData(**{'id': None, 'zone_id': 'PENDING', 'name': None, 'email': None, 'status': "deleted", 'action': None, 'ttl': None, 'serial': None, 'description': None, 'type': 'A'})

        return record_object

# create recordset button link handler
class RecordSetCreateLink(tables.LinkAction):
    name = "recordsetcreate"
    verbose_name = _("Add a Record to the Zone")
    url = "horizon:project:dns:recordsetcreate"
    classes = ("ajax-modal",)
    icon = "plus"

    def allowed(self, request, datum):
       outcome = policy.check(DNS_POLICIES['recordset_create'], request)
       LOG.info("POLICY CHECK RECORDSET CREATE %s" % outcome)
       return outcome

# zone update link handler
class RecordSetUpdateLink(tables.LinkAction):
    name = "recordsetupdate"
    verbose_name = _("Update this Record")
    url = "horizon:project:dns:recordsetupdate"
    cancel_url = "horizon:project:dns:recordsets"
    classes = ("ajax-modal",)
    icon = "pencil"
    policy_rules = DNS_POLICIES['recordset_update']

    def get_link_url(self, datum=None):
        if not self.url:
            raise NotImplementedError('A LinkAction class must have a '
                                      'url attribute or define its own '
                                      'get_link_url method.')

        if callable(self.url):
            return self.url(datum, **self.kwargs)
        try:
            if datum:
                obj_id = self.table.get_object_id(datum)
                return reverse(self.url, args=(datum.zone_id, obj_id,))
            else:
                return reverse(self.url)

        except NoReverseMatch as ex:
            LOG.error('No reverse found for "%(url)s": %(exception)s', {'url': self.url, 'exception': ex})
            return reverse_lazy(self.cancel_url)

    def allowed(self, request, datum):
        if (datum is not None) and (datum.type in ALLOWED_RECORD_TYPES):
            self.datum = datum
            return True
        else:
            LOG.info("RecordSetUpdateLink: Update call is not permitted by API")
            return False

# record delete button link handler
class RecordSetDeleteLink(tables.DeleteAction):
    name = "recordsetdelete"
    policy_rules = DNS_POLICIES['recordset_delete']

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Selected Record",
            u"Delete Selected Record",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Recordset Delete Accepted",
            u"Recordset Delete Accepted",
            count
        )

    def allowed(self, request, datum):
        if (datum is not None) and (datum.type in ALLOWED_RECORD_TYPES):
            self.datum=datum
            return True
        else:
            LOG.info("RecordSetDeleteLink: Delete call is not permitted by API")
            return False

    def delete(self, request, obj_id):
        designate_bridge.delete_recordset(request, zone=self.datum.zone_id, recordset=obj_id)

class DNSRecordSetTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("pending", None),
        ("error", False),
        ("deleted", True),
    )
    ACTION_CHOICES = (
        ("create", None),
        ("update", None),
        ("delete", None),
        ("none", True),
        ("error", False),
    )
    id = tables.Column('id', verbose_name=_('ID'), hidden=True)
    name = tables.Column('name', verbose_name=_('FQDN'))
    description = tables.Column('description', verbose_name=_('Description'))
    status = tables.Column('status', verbose_name=_('Health'), status=True, status_choices=STATUS_CHOICES)
    action = tables.Column('action', verbose_name=_('Current Action'), status=True, status_choices=ACTION_CHOICES)
    ttl = tables.Column('ttl', verbose_name=_('TTL'))
    type = tables.Column('type', verbose_name=_('Record Type'))
    zone_id = tables.Column('zone_id', verbose_name=_('Zone ID'))

    class Meta(object):
        name = 'recordsets'
        verbose_name = 'Records in zone'
        row_class = UpdateRecordRow
        status_columns = ['status', 'action']
        row_class = UpdateRecordRow
        row_actions = (RecordSetUpdateLink, RecordSetDeleteLink, )

class DNSZonesTable(tables.DataTable):
    STATUS_CHOICES = (
        ("active", True),
        ("pending", None),
        ("error", False),
        ("deleted", True),
    )
    ACTION_CHOICES = (
        ("create", None),
        ("update", None),
        ("delete", None),
        ("none", True),
        ("error", False),
    )
    id = tables.Column('id', verbose_name=_('ID'), hidden=True)
    name = tables.Column('name', link='horizon:project:dns:recordsets', verbose_name=_('DNS Zone Name'))
    email = tables.Column('email', verbose_name=_('Registrar E-Mail Address'))
    status = tables.Column('status', verbose_name=_('Zone Health'), status=True, status_choices=STATUS_CHOICES)
    action = tables.Column('action', verbose_name=_('Current Action'), status=True, status_choices=ACTION_CHOICES)
    ttl = tables.Column('ttl', verbose_name=_('Zone TTL'))
    type = tables.Column('type', verbose_name=_('Zone Type'))
    serial = tables.Column('serial', verbose_name=_('Zone Serial'))
    description = tables.Column('description', verbose_name=_('Description'))

    class Meta(object):
        name = "dns"
        verbose_name = _("DNS as a Service: Zones")
        status_columns = ["status", "action"]
        row_class = UpdateZoneRow
        table_actions = (ZoneCreateLink, ZoneDeleteLink, )
        row_actions = (ZoneUpdateLink, RecordSetCreateLink, ZoneDeleteLink,)
