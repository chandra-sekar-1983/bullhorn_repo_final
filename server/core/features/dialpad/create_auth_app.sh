#!/usr/bin/env bash
set -e
set -o history -o histexpand
source ./devops/admin/constants.sh
source ./devops/admin/tools.sh

welcome "Integration Framework - Dialpad OAuth App Creation Script!" "

This script will help you to create OAuth App on Dialpad using your API Token.
Please make sure that you have your Dialpad Public API key ready. API Key has to be company level.
"

DIALPAD_BETA_API_URL=https://dialpadbeta.com/api/v2/oauth_apps 
DIALPAD_PROD_API_URL=https://dialpad.com/api/v2/oauth_apps 
DIALPAD_API_URL=''
declare -A CREATE_PARAMS

function make_array() {
  echo "[\"$(echo "$1" | sed "s/,/\",\"/g")\"]"
}

function assign_to_params() {
  if [[ ! -z $2 ]]
  then
    TYPE="${3:-'literal'}"
    if [[ $TYPE = 'array' ]]
    then
      VALUE=$(make_array $2)
    else
      VALUE=$2
    fi
    CREATE_PARAMS[$1]=$VALUE
    printe "{$1:$VALUE}"
  fi
  unset VALUE
}

prints "Please choose the environment:"
select yn in Production Beta
do
  case $yn in
    Production ) DIALPAD_API_URL="$DIALPAD_PROD_API_URL"; break;;
    Beta ) DIALPAD_API_URL="$DIALPAD_BETA_API_URL"; break;;
  esac
done

prints "Please enter the Dialpad API key:"
read -s API_KEY
API_KEY=${API_KEY}
printe

prints "Please enter the name of your OAuth App:"
read NAME
assign_to_params 'name' $NAME

prints "Please enter the description of your OAuth App:"
read DESCRIPTION
assign_to_params 'description' $DESCRIPTION


prints "Would you like to publish your OAuth App to Marketplace?"
select yn in Yes No
do
  case $yn in
    Yes ) IS_PUBLISHED=true; break;;
    No ) IS_PUBLISHED=false; break;;
  esac
done
assign_to_params 'is_published' $IS_PUBLISHED

prints "Please choose the required company account type of the OAuth App:"
select res in "Free" "Standard" "Pro" "Enterprise"
do
  case $res in
    Free ) REQUIRED_SKU="Free"; break;;
    Standard ) REQUIRED_SKU="Standard"; break;;
    Pro ) REQUIRED_SKU="Pro"; break;;
    Enterprise ) REQUIRED_SKU="Enterprise"; break;;
  esac
done
assign_to_params 'required_sku' $REQUIRED_SKU

prints "Please enter the redirect URIs for the OAuth app. (Comma seperated if many):"
read REDIRECT_URIS
assign_to_params 'redirect_uris' "$REDIRECT_URIS" 'array'

prints "Please enter the all possible scopes an ApiKey associated with this OAuth App can have:" "
(Comma seperated if many)"
read ALLOWED_SCOPES
assign_to_params 'allowed_scopes' "$ALLOWED_SCOPES" 'array'

prints "Please enter the allowed origins of the OAuth App:"
read ALLOWED_ORIGINS
assign_to_params 'allowed_origins' "$ALLOWED_ORIGINS" 'array'

prints "Please enter the additional headers of the OAuth App:"
read ADDITIONAL_HEADERS
assign_to_params 'additional_headers' "$ADDITIONAL_HEADERS"

prints "Please enter the URIs that will be used to render iframe for the OAuth App:" "
(Comma seperated if many)"
read IFRAME_URIS
assign_to_params 'iframe_uris' "$IFRAME_URIS" 'array'

prints "Please enter the schema of supported custom settings for the OAuth App:"
read CUSTOM_SETTINGS_SCHEMA
assign_to_params 'custom_settings_schema' "$CUSTOM_SETTINGS_SCHEMA"

prints "Please enter the email of support of the OAuth App:"
read SUPPORT_EMAIL
assign_to_params 'support_email' "$SUPPORT_EMAIL"

prints "Please enter the email of developer of the OAuth App:"
read DEVELOPER_EMAIL
assign_to_params 'developer_email' $DEVELOPER_EMAIL

prints "Please enter the first name of the developer of the OAuth App:"
read DEVELOPER_FIRST_NAME
assign_to_params 'developer_first_name' $DEVELOPER_FIRST_NAME

prints "Please enter the last name of the developer of the OAuth App:"
read DEVELOPER_LAST_NAME
assign_to_params 'developer_last_name' $DEVELOPER_LAST_NAME

prints "Please confirm."
printf "$DIALPAD_API_URL\n"

FINAL_PARAMS=$(for key in "${!CREATE_PARAMS[@]}"; do
    printf '%s\0%s\0' "$key" "${CREATE_PARAMS[$key]}"
done |
jq -Rs '
  split("\u0000")
  | . as $a
  | reduce range(0; length/2) as $i
  ({}; . + {($a[2*$i]): ($a[2*$i + 1]|fromjson? // .)})')

echo $FINAL_PARAMS

function make_create_request() {
  echo $(curl -X POST $DIALPAD_API_URL \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "$FINAL_PARAMS")
}

function make_enable_request() {
  echo $(curl -X PATCH "$DIALPAD_API_URL/$CLIENT_ID/toggle" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "{\"enable\": true}")
}

CLIENT_ID=''
function create_and_enable_oauth_app() {
  CLIENT_ID=$(make_create_request | awk 'BEGIN { FS="\""; RS="," }; { if ($2 == "client_id") {print $4} }')
  make_enable_request
}

select yn in Yes No
do
  case $yn in
    Yes ) create_and_enable_oauth_app; break;; 
    No ) exit;;
  esac
done
