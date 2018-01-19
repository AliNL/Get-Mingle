# Get-Mingle

## How to use
1. Create a json file called `config.json`
1. Copy the content in `config_template.json` to `config.json`
1. Change it to your project info
1. You can get your secret key from Mingle at: Settings -> HMAC Auth Key -> GENERATE
1. The status don't need to be all of the status of your project, but the name should be exactly same with the status on Mingle

## How it works
1. The requester calls Mingle API to get all kinds of data
1. The formatter puts the data into page templates

## Set up
1. brew install python3
1. pip3 install -r requirements.txt