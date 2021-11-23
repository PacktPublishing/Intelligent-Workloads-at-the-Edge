The resources here for chapter 3 are as follows:

Components
* com.hbs.hub.ReadSenseHAT
* com.hbs.hub.WriteSenseHAT
* com.hbs.hub.ReadSenseHATSimulated
* com.hbs.hub.WriteSenseHATSimulated

If you are working through the book examples with a Raspberry Pi and a SenseHAT expansion board, you will deploy the components `com.hbs.hub.ReadSenseHAT` and `com.hbs.hub.WriteSenseHAT` just as they are indicated in the chapter's instructions. If you are working on any other configuration, it is recommended to use `com.hbs.hub.ReadSenseHATSimulated` and `com.hbs.hub.WriteSenseHATSimulated` which do not try to read or write any serial interface. To use these alternate components, simply modify the command that creates the local deployment to update the component name. For example:

`sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir recipes/ --artifactDir artifacts/ --merge "com.hbs.hub.ReadSenseHAT=1.0.0"` 

becomes

`sudo /greengrass/v2/bin/greengrass-cli deployment create --recipeDir recipes/ --artifactDir artifacts/ --merge "com.hbs.hub.ReadSenseHATSimulated=1.0.0"` 

For verifying that these simulators are correctly deployed, you will need to inspect the local log files for each. 

