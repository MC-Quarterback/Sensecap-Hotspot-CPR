# SenseCAP Hotspot CPR

A script to mitigate ongoing issues with Helium hotspots getting behind the blockchain and seeming to hang
rather than catch up.

This script will periodically check (currently every 7 minutes) the current blockchain height against
that of the hotspot.  If the hotspot is behind by 6 (configurable) or more blocks, then the script
will automatically instruct the hotspot to do a Reset Blocks, and optionally a Reboot.

## Usage from source code
* This script is intended to be run on the sam LAN that your hotspot is on. 
  You can of course run it remotely if you have set up a VPN which has access to your hotspot.
  I __do not__ recommend setting up port forwarding to make the API accessible externally outside of a VPN.  
* Ensure you have the prerequisites installed on your computer which are:
   * Python 3
   * Pipenv
    
* From the root of the source directory, install dependent packages with:
`pipenv install`
  
* Switch to the virtualenv created by Pipenv with:
`pipenv shell`
  
* Edit the configuration file and list your hotspots (see _Configuration_ section)
* Run the code with `python3 monitor-hotspots.py`

## Configuration

This is driven from the settings.ini file

### Global system settings

| Property      | Description           | Default  |
| ------------- |-------------| -----:|
| max_delta     | The maximum number of blocks your hotspot can be behind the blockchain before a reset blocks occurs | 6 |
| reboot_before_reset | If set to 'yes', before performing a reset blocks, your hotspot will be rebooted.  A reset blocks will be scheduled to start 3 minutes after the reboot. | no |
| reboot_after_reset | If set to 'yes', 35 minutes after performing a reset blocks, your hotspot will be rebooted | yes |

### Hotspot configuration sections
Each hotspot is configured in its own section in the file with its name as the section title.
The name is for your reference only and doesn't have to exactly match the name of your hotspot.

The following properties must be configured for each hotspot:

| Property      | Description           | Example  |
| ------------- |-------------| -----|
| address     | This is the address of your hotspot, which you can get from explorer.helium.com or your Sensecap Dashboard | 11239zQFLCU9s85t7Hnsi5yjFrBTwLNQZqC7x1ybi99aNBbUWDQq |
| token | This is the API token you can copy/paste by logging on locally to your hotspot's IP, it's displayed near the top of the page | 6556fde778ee5656aab66b6b6a7735624435da66826498274b6c55f00378bab7 |
| ip | This is the LAN IP address of your hotspot, which must be accessible from the host you run the script from | 192.168.1.34 |

### Full Example

Say I had a hotspot called Antagonising Slow Doorstop, after noting the address and token my settings.ini might look something like this:

```
[System]
max_delta = 6
reboot_before_reset = no
reboot_after_reset = yes

[Antagonising Slow Doorstop]
address = 11239zQFLCU9s85t7Hnsi5yjFrBTwLNQZqC7x1ybi99aNBbUWDQq
token = 6556fde778ee5656aab66b6b6a7735624435da66826498274b6c55f00378bab7
ip = 192.168.1.34
```

If you own additional hotspots, and have set up VPNs in such a way you can access them all from the same host - you can add additional sections per hotspot and the script will monitor them all.

I'm not sure how practical such a VPN setup is though, so please contact me if it isn't practical - as multiple hotspots on the same LAN would clearly indicate gaming the system...


