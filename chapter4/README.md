The resources here for chapter 4 are as follows:

## Components

* com.hbs.hub.HelloWithConfig
* com.hbs.hub.ScrollMessage
* com.hbs.hub.ScrollMessageSimulated

If you are working through the book examples with a Raspberry Pi and a SenseHAT expansion board, you will deploy the component `com.hbs.hub.ScrollMessage` just as it is indicated in the chapter's instructions. If you are working on any other configuration, it is recommended to use `com.hbs.hub.ScrollMessageSimulated` which does not try to read or write any serial interface. To use these alternate components, simply modify the command that creates the local deployment to update the component name. For example:

`sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir recipes/ --artifactDir artifacts/ --merge "com.hbs.hub.ScrollMessage=1.0.0"` 

becomes

`sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir recipes/ --artifactDir artifacts/ --merge "com.hbs.hub.ScrollMessageSimulated=1.0.0"` 

For verifying that these simulators are correctly deployed, you will need to inspect the local log files for each. 

## Deployment templates

* deployment-hellowithconfig.json
* deployment-logmanager.json
* deployment-ml.json
* deployment-syncstate.json

In deployment-ml.json, you are deploying the component com.hbs.hub.ScrollMessage to act on the results of the ML inference solution. For readers working through the book examples without a Raspberry Pi and SenseHAT expansion board, you will update the deployment file to deploy com.hbs.hub.ScrollMessageSimulated instead. You will need to register the com.hbs.hub.ScrollMessageSimulated component instead of com.hbs.hub.ScrollMessage in your account before this edited deployment will work.