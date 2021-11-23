#!/bin/bash

#replace the path of the artifacts below before running this script. 

sudo /greengrass/v2/bin/greengrass-cli deployment create \
  --recipeDir ~/Documents/hbshub/recipes \
  --artifactDir ~/Documents/hbshub/artifacts \
  --merge "com.hbs.hub.Publisher=1.0.0"

sleep 2

sudo /greengrass/v2/bin/greengrass-cli deployment create \
  --recipeDir ~/Documents/hbshub/recipes \
  --artifactDir ~/Documents/hbshub/artifacts \
  --merge "com.hbs.hub.Subscriber=1.0.0"

sleep 2

sudo /greengrass/v2/bin/greengrass-cli deployment create \
  --recipeDir ~/Documents/hbshub/recipes \
  --artifactDir ~/Documents/hbshub/artifacts \
  --merge "com.hbs.hub.Aggregator=1.0.0"

sleep 2
