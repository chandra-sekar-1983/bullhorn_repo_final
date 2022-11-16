# IFRAME FEATURE

## Description
A feature to add capabilities to create iframes to be rendered in Dialpad.

## URL prefix
/iframe

## Configuration
| ENV VAR | DEFAULT |
| --- | --- |


## How to enable
Using environment variable; 
*development*
Add below line to .env
```bash
ENABLE_DIALPAD_IFRAME=1 # enable
ENABLE_DIALPAD_IFRAME=0 # disable
```
*google cloud*
Update ./devops/terraform/`ENV`.tfvars file
```
   env_vars = {
     ...,
     ENABLE_DIALPAD_IFRAME = 1,
   }
```
