#!/bin/bash

SWPATH="/usr/share/openstack-dashboard/openstack_dashboard"
APIPATH="$SWPATH/api"
DASHPATH="$SWPATH/dashboards/project"

for host in "$@"; do
  # install api integration python file
  ssh -i $SSHKEY root@$host mkdir -p $APIPATH
  scp -i $SSHKEY api/designate.py root@$host:$APIPATH/

  # install dashboard
  scp -ri $SSHKEY dns root@$host:$DASHPATH/

  # enable dashboard
  scp -i $SSHKEY enabled/_3032_network_dns_panel.py root@$host:$SWPATH/enabled/

  # install policy file
  scp -i $SSHKEY dns_policy.json root@$host:/etc/openstack-dashboard/dns_policy.json

  # fix selinux
  ssh -i $SSHKEY root@$host restorecon -Rv $SWPATH
  ssh -i $SSHKEY root@$host restorecon -Rv /etc/openstack-dashboard
  ssh -i $SSHKEY root@$host chown root:apache /etc/openstack-dashboard/dns_policy.json

  # restart apache
  ssh -i $SSHKEY root@$host systemctl restart httpd
done

# Now upload the new policy file to the server that hosts the designate-api service.
scp -i $SSHKEY dns_policy.json root@$DNSMASTER:/etc/designate/policy.json

