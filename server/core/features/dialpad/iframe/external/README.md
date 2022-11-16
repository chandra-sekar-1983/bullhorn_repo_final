# EXTERNAL FEATURE

## Description
A feature to add capabilities to handle all type of interaction with an external platform

## URL prefix
/external

## Configuration
|  ENV VAR | DEFAULT | DESCRIPTION |
| --- | --- | --- |


## How to enable
*development*
Add below line to .env
```bash
DPI_ENABLE_EXTERNAL=1 # enable
DPI_ENABLE_EXTERNAL=0 # disable
```
*google cloud*
Update ./devops/terraform/<ENV>.tfvars file
```
   env_vars = {
     ...,
     DPI_ENABLE_EXTERNAL = 1,
   }
```   
   
## Dependencies
Requires implementation of Integration Client.
- *dpi/external/integration/client.py*
- *dpi/external/integration/config.py*

IntegrationClient is a subclass of IntegrationClientBase. Please see *dpi/external/base.py* for the minimum interface required.
