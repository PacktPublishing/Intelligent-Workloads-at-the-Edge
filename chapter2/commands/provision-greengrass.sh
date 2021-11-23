#!/bin/bash

sudo -E java -Droot="/greengrass/v2" -Dlog.store=FILE \
  -jar ./greengrass/lib/Greengrass.jar \
  --aws-region us-west-2 \
  --thing-name hbshub001 \
  --thing-group-name hbshubprototypes \
  --tes-role-name GreengrassV2TokenExchangeRole \
  --tes-role-alias-name GreengrassCoreTokenExchangeRoleAlias \
  --component-default-user ggc_user:ggc_group \
  --provision true \
  --setup-system-service true \
  --deploy-dev-tools true