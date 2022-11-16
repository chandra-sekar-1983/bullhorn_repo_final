# api feature

## Description
A feature to add capabilities to handle all type of interaction with frontend DPI Client

## URL prefix
/api

## Configuration
| ENV VAR | DEFAULT | DESCRIPTION |
| --- | --- | --- |

## How to enable
*development*
Add below line to .env
```bash
DPI_ENABLE_API=1 # enable
DPI_ENABLE_API=0 # disable
```
*google cloud*
Update ./devops/terraform/<ENV>.tfvars file
```
   env_vars = {
     ...,
     DPI_ENABLE_API = 1,
   }
```
