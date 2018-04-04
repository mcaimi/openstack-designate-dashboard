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
import re

from horizon.utils.validators import ValidationError
from django.utils.translation import ugettext_lazy as _
from oslo_utils import netutils

LOG = logging.getLogger(__name__)

# global validation helpers.
# this one validates a string against a regex
def string_validate_by_regex(string_to_validate, regex):
    if not (isinstance(string_to_validate, str) or isinstance(regex, str)):
        return False

    # compile regex
    rp = re.compile(regex, re.IGNORECASE)

    # match
    if rp.match(string_to_validate) is not None:
        return True
    else:
        return False

# validate a domain name
def validate_domain_name(domain_name=""):
    if not string_validate_by_regex(domain_name, r'^(\D+\.){2,5}$'):
        raise ValidationError(_("Invalid Domain Name Format."))

# validate a record name
def validate_record_name(record_name=""):
    if not string_validate_by_regex(record_name, r'^(\w+\.){0,5}(\w+)$'):
        raise ValidationError(_("Invalid Record Name Format."))

# validate an email address
def validate_email_address(email_address=""):
    if not string_validate_by_regex(email_address, r'^(\w+.)+\@(\w+\.){1,5}(\w+)$'):
        raise ValidationError(_("Invalid E-Mail Format."))

# validate an ip address
def validate_ip_address(ip_address=""):
    if not netutils.is_valid_ipv4(ip_address):
        raise ValidationError(_("Invalid IP Address Format."))

#
