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

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^index$', views.IndexView.as_view(), name='index'),
    url(r'^zones/create$', views.ZoneCreateView.as_view(), name='zonecreate'),
    url(r'^zones/(?P<zone_id>[^/]+)/update$', views.ZoneUpdateView.as_view(), name='zoneupdate'),
    url(r'^zones/(?P<zone_id>[^/]+)/index$', views.RecordSetsIndexView.as_view(), name='recordsets'),
    url(r'^zones/(?P<zone_id>[^/]+)/create$', views.RecordSetCreateView.as_view(), name='recordsetcreate'),
    url(r'^zones/(?P<zone_id>[^/]+)/recordset/(?P<recordset_id>[^/]+)/update$', views.RecordSetUpdateView.as_view(), name='recordsetupdate'),
]
