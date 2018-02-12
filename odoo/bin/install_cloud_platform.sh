#!/bin/bash
# Install modules for c2c Odoo Cloud platform
# by default platform is disabled
set -e

if [ "$C2C_PLATFORM" == "True" ]; then
    echo "Installing C2C platform modules..."
    # camptocamp/cloud-platform
    odoo -i cloud_platform_exoscale --stop-after-init --workers=0
    # platform is on AWS not on exoscale but it is mostly the same config
    # we will use exoscale one as we don't know yet if it will be the final config
    anthem openerp.addons.cloud_platform.songs::install_exoscale
fi
