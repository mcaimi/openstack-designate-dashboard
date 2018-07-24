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

from django.core.urlresolvers import reverse,reverse_lazy, NoReverseMatch
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables

from openstack_dashboard import settings
from openstack_dashboard.api import designate
from openstack_dashboard.dashboards.project.dns import tables as dns_tables
from openstack_dashboard.dashboards.project.dns import forms as dns_forms

LOG = logging.getLogger(__name__)

class DnsData(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for k in kwargs:
            setattr(self, k, kwargs.get(k))

        self.record_data = None
        if getattr(self, 'records', None) is not None:
            self.record_data = ", ".join(self.records)

class RecordSetsIndexView(tables.DataTableView):
    table_class = dns_tables.DNSRecordSetTable
    template_name = 'project/dns/recordset_index.html'
    page_title = _('Zone Record Set Overview')

    def get_context_data(self, **kwargs):
        context = super(RecordSetsIndexView, self).get_context_data(**kwargs)
        context['zone_id'] = self.kwargs.get('zone_id')
        return context

    def get_data(self):
        objects = []
        try:
            for recordset in designate.get_recordsets(self.request, zone=self.kwargs.get('zone_id')):
                objects.append(DnsData(**recordset))
        except Exception as e:
            objects = []

        return objects

class IndexView(tables.DataTableView):
    table_class = dns_tables.DNSZonesTable
    template_name = 'project/dns/index.html'
    page_title = _("DNSaaS")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context

    def get_data(self):
        objects = []
        try:
            for zone_object in designate.get_zones(self.request):
                objects.append(DnsData(**zone_object))
        except:
            objects = []

        return objects

class ZoneCreateView(forms.ModalFormView):
    template_name = 'project/dns/zonecreate.html'
    modal_header = _("Create a new DNS Zone")
    form_id = "dns_zone_create_form"
    form_class = dns_forms.ZoneCreateForm
    submit_label = _("Create Zone")
    submit_url = reverse_lazy("horizon:project:dns:zonecreate")
    success_url = reverse_lazy('horizon:project:dns:index')
    page_title = _("Create a new DNS Zone")

class RecordSetCreateView(forms.ModalFormView):
    template_name = 'project/dns/recordsetcreate.html'
    modal_header = _("Create a new Record in this Zone")
    form_id = "dns_recordset_create_form"
    form_class = dns_forms.RecordSetCreateForm
    submit_label = _("Create Record")
    submit_url = 'horizon:project:dns:recordsetcreate'
    success_url = reverse_lazy('horizon:project:dns:index')
    cancel_url = reverse_lazy('horizon:project:dns:index')
    page_title = _("Create a new Record in this Zone")

    def get_context_data(self, **kwargs):
        context = super(RecordSetCreateView, self).get_context_data(**kwargs)
        context['zone_id'] = self.kwargs.get('zone_id')
        args = (self.kwargs.get('zone_id'),)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {'zone_id': self.kwargs['zone_id']}

class RecordSetUpdateView(forms.ModalFormView):
    template_name = 'project/dns/recordsetupdate.html'
    modal_header = _("Update This Record")
    form_id = "dns_recordset_update_form"
    form_class = dns_forms.RecordSetUpdateForm
    submit_label = _("Update Record")
    submit_url = 'horizon:project:dns:recordsetupdate'
    success_url = reverse_lazy('horizon:project:dns:index')
    cancel_url = reverse_lazy('horizon:project:dns:index')
    page_title = _("Update Record")

    def get_context_data(self, **kwargs):
        context = super(RecordSetUpdateView, self).get_context_data(**kwargs)
        context['recordset_id'] = self.kwargs.get('recordset_id')
        context['zone_id'] = self.kwargs.get('zone_id')
        submit_args = (self.kwargs.get('zone_id'), self.kwargs.get('recordset_id'),)
        #success_args = (self.kwargs.get('zone_id'),)
        context['submit_url'] = reverse(self.submit_url, args=submit_args)
        #context['success_url'] = reverse(self.success_url, args=success_args)
        LOG.info("RUPDATE: updated context %s" % context)
        return context

    def get_initial(self):
        return {'recordset_id': self.kwargs['recordset_id'], 'zone_id': self.kwargs['zone_id']}

class ZoneUpdateView(forms.ModalFormView):
    template_name = 'project/dns/zoneupdate.html'
    modal_header = _("Update DNS Zone")
    form_id = "dns_zone_update_form"
    form_class = dns_forms.ZoneUpdateForm
    submit_label = _("Update Zone")
    submit_url = "horizon:project:dns:zoneupdate"
    success_url = reverse_lazy('horizon:project:dns:index')
    page_title = _("Update DNS Zone")

    def get_context_data(self, **kwargs):
        context = super(ZoneUpdateView, self).get_context_data(**kwargs)
        context['zone_id'] = self.kwargs.get('zone_id')
        args = (self.kwargs.get('zone_id'),)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {'zone_id': self.kwargs['zone_id']}

