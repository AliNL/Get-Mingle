# Get-Mingle

## How to use
1. Create a yaml file called `config.yml`
1. Copy the content in `config_template.yml` to `config.yml`
1. Change it to your project info
1. You can get your secret key from Mingle at: Settings -> HMAC Auth Key -> GENERATE
1. The status doesn't need to be all of the status of your project, but the name should be exactly same with the status on Mingle

## How it works
1. The requester calls Mingle API to get all kinds of data
1. The formatter puts the data into page templates
