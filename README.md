
**Openstack Designate Dashboard for Horizon**
-
A work-in-progress dashboard that runs inside Openstack Horizon.
This project started as a personal project at work, in order to give a simple Designate dashboard to the users of our Openstack Platform.

This dashboard was developed on RedHat Openstack Platform starting with the Mitaka release (9.0) and should work even in Newton (10.0). 
Also, it is still (mostly off-working-time) in development.

Feature currently implemented:
  * Designate api v1 integration layer
  * Create/update/delete zones
  * Create/update/delete recordsets
  * Zone multitenancy
  * "Master" dns zone that hosts all automatic floatingip/instancename associations
  * DNSaaS API policy enforcement.

TODO:
  - Graphical overhaul of most django forms.

**INSTALLATION**
-

At this time an automated/pretty way to install this component is not available, luckily an ugly script is shipped with the code :)
Just run the installation script specifying the hostname or the IP address of your horizon server. Deployment inside a docker container is also a common shortcut.

Two environment variables are needed to be set before running the script:

  * SSHKEY: path to the ssh key that you have to use in order to perform passwordless root login in the target server
  * DNSMASTER: hostname/IP address of the designate-api host

This script is mostly geared towards Openstack Installations based on Redhat's own distribution but since this is basically a django dashboard, it should be almost the same on all horizon installations.
