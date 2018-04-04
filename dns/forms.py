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

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.api import designate as designate_bridge
from openstack_dashboard.dashboards.project.dns.field_validators import validate_ip_address, validate_email_address, validate_domain_name, validate_record_name

LOG = logging.getLogger(__name__)

# Recordset create Django form
class RecordSetCreateForm(forms.SelfHandlingForm):
    RECORDSET_TYPES = (
            ('A', '[A] IPv4 Address Alias'),
            ('CNAME', '[CNAME] Common Name'),
            ('PTR', '[PTR] Pointer'),
            ('MX', '[MX] Mail Exchange'),
            ('SRV', '[SRV] Service'),
            ('TXT', '[TXT] Text'),
            )

    recordname = forms.CharField(max_length=255, label=_("Record Name"), required=True, validators=[validate_record_name])
    ttl = forms.IntegerField(label=_("Record TTL"), required=False)
    record_value = forms.CharField(label=_("Record Value"), required=True)
    recordtype = forms.ChoiceField(choices=RECORDSET_TYPES, required=True)
    description = forms.CharField(label=_("Description"), required=False)
    zone_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, request, *args, **kwargs):
        super(RecordSetCreateForm, self).__init__(request, *args, **kwargs)

        self.fields['zone_id'].initial = kwargs.get('initial', {}).get('zone_id')
        self.fields['recordname'].initial = ""
        self.fields['record_value'].initial = ""
        self.fields['ttl'].initial = 86400
        self.fields['recordtype'].initial = 'A'
        self.fields['description'].initial = ""

    def handle(self, request, data):
        LOG.info("dns::forms::RecordSetCreateForm: RUNNING POST HOOK")
        zone_id = data.get('zone_id')
        recordname = data.get('recordname')
        record_value = data.get('record_value')
        ttl = data.get('ttl')
        recordtype = data.get('recordtype')
        description = data.get('description')

        try:
            designate_bridge.create_recordset(request, zone=zone_id, name=recordname, type_=recordtype, records=[record_value,], description=description, ttl=ttl)
            messages.success(request, _('[DNS]: Record Create Request queued for execution.'))
        except:
            exceptions.handle(request, _('[DNS]: Error while submitting Record Create Request.'))

        return True

# Recordset create Django form
class RecordSetUpdateForm(forms.SelfHandlingForm):
    RECORDSET_TYPES = (
            ('A', '[A] IPv4 Address Alias'),
            ('CNAME', '[CNAME] Common Name'),
            ('PTR', '[PTR] Pointer'),
            ('MX', '[MX] Mail Exchange'),
            ('SRV', '[SRV] Service'),
            ('TXT', '[TXT] Text'),
            )

    recordset_id = forms.CharField(widget=forms.HiddenInput())
    recordname = forms.CharField(widget=forms.HiddenInput())
    ttl = forms.IntegerField(label=_("Record TTL"), required=False)
    record_value = forms.CharField(label=_("Record Value"), required=True)
    recordtype = forms.ChoiceField(choices=RECORDSET_TYPES, widget=forms.HiddenInput())
    description = forms.CharField(label=_("Description"), required=False)
    zone_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, request, *args, **kwargs):
        super(RecordSetUpdateForm, self).__init__(request, *args, **kwargs)

        self.fields['zone_id'].initial = kwargs.get('initial', {}).get('zone_id')
        self.fields['recordset_id'].initial = kwargs.get('initial', {}).get('recordset_id')
        try:
            current_record = designate_bridge.get_record(request, self.fields['zone_id'].initial, self.fields['recordset_id'].initial)
        except Exception as e:
            LOG.error("Update API Call: %s " % e)
            raise e
        self.fields['recordname'].initial = current_record.get('name').split()[0]
        self.fields['record_value'].initial = current_record.get('records')[0]
        self.fields['ttl'].initial = int(current_record.get('ttl'))
        self.fields['recordtype'].initial = current_record.get('type')
        self.fields['description'].initial = current_record.get('description')
        
    def handle(self, request, data):
        LOG.info("dns::forms::RecordSetUpdateForm: RUNNING POST HOOK")
        recordset_id = data.get('recordset_id')
        zone_id = data.get('zone_id')
        recordname = data.get('recordname')
        record_value = data.get('record_value')
        ttl = data.get('ttl')
        recordtype = data.get('recordtype')
        description = data.get('description')
        
        # pack record data
        args = {'records': [record_value, ], 'ttl': ttl, 'description': description}

        # Make an update_record API call to the backend engine
        try:
            designate_bridge.update_recordset(request, zone=zone_id, recordset=recordset_id, values=args)
            messages.success(request, _('[DNS]: Record Update Request queued for execution.'))
            return True
        except:
            exceptions.handle(request, _('[DNS]: Error while submitting Record Update Request.'))
            return False

# Zone create Django form
class ZoneCreateForm(forms.SelfHandlingForm):
    zonename = forms.CharField(max_length=255, label=_("DNS Zone Name"), required=True, validators=[validate_domain_name])
    email_address = forms.CharField(label=_("Registrar E-Mail"), required=True, validators=[validate_email_address])
    ttl = forms.IntegerField(label=_("Zone TTL"), required=False)
    description = forms.CharField(max_length=255, label=_("Zone Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(ZoneCreateForm, self).__init__(request, *args, **kwargs)

        self.fields['zonename'].initial = ""
        self.fields['email_address'].initial = ""
        self.fields['ttl'].initial = 3600
        self.fields['description'].initial = "DNS Zone"

    def handle(self, request, data):
        LOG.info("dns::forms::ZoneCreateForm: RUNNING POST HOOK")
        user = self.request.user
        zonename = data.get('zonename')
        email_address = data.get('email_address')
        ttl = data.get('ttl')
        description = data.get('description')

        try:
            designate_bridge.create_zone(request, name=zonename, email=email_address, ttl=ttl, description=description)
            messages.success(request, _('[DNS]: Zone Create Request queued for execution.'))
        except:
            exceptions.handle(request, _('[DNS]: Error while submitting Zone Create Request.'))

        return True

# Zone update Django form
class ZoneUpdateForm(forms.SelfHandlingForm):
    zone_id = forms.CharField(widget=forms.HiddenInput())
    zonename = forms.CharField(widget=forms.HiddenInput())
    email_address = forms.CharField(label=_("Registrar E-Mail"), required=True, validators=[validate_email_address])
    ttl = forms.IntegerField(label=_("Zone TTL"), required=False)
    description = forms.CharField(max_length=255, label=_("Zone Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(ZoneUpdateForm, self).__init__(request, *args, **kwargs)

        # get initial info
        self.fields['zone_id'].initial = kwargs.get('initial', {}).get('zone_id')
        try:
            zone_info = designate_bridge.get_zone(self.request, zone=self.fields.get('zone_id').initial)
        except Exception as e:
            raise e

        self.fields['zonename'].initial = zone_info.get('name')
        self.fields['email_address'].initial = zone_info.get('email')
        self.fields['ttl'].initial = zone_info.get('ttl')
        self.fields['description'].initial = zone_info.get('description')

    def handle(self, request, data):
        LOG.info("dns::forms::ZoneUpdateForm: RUNNING POST HOOK")
        user = self.request.user
        zone_id = data.get('zone_id')
        zonename = data.get('zonename')
        email_address = data.get('email_address')
        ttl = data.get('ttl')
        description = data.get('description')
        update_data = {'name': zonename, 'email': email_address, 'ttl': ttl, 'description': description}

        try:
            designate_bridge.update_zone(request, zone=zone_id, data=update_data)
            messages.success(request, _('[DNS]: Zone Update Request queued for execution.'))
        except:
            exceptions.handle(request, _('[DNS]: Error while submitting Zone Update Request.'))

        return True

