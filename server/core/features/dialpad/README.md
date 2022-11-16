# DIALPAD FEATURE

## Description
A feature to add capabilities to handle all type of interaction with Dialpad Platform API

## Auth flow
![Integration Framework - Auth Flow ](https://user-images.githubusercontent.com/6083754/164580523-6794a100-963a-4407-895f-3c1367358fac.png)

## URL prefix
/dialpad

## Configuration
| ENV VAR | DEFAULT |
| --- | --- |
| DIALPAD_CLIENT_ID | None |
| DIALPAD_CLIENT_SECRET | None |
| DIALPAD_URL | http://devbox:8085 |


## How to enable

*development*
Add below line to .env
```
DPI_ENABLE_DIALPAD=1 # enable
DPI_ENABLE_DIALPAD=0 # disable
```
*google cloud*
Update ./devops/terraform/<ENV>.tfvars file
```
   env_vars = {
     ...,
     DPI_ENABLE_DIALPAD = 1,
   }
```
