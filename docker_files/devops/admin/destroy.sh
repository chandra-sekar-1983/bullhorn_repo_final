#!/bin/bash
set -e
source ./devops/admin/constants.sh
source ./devops/admin/tools.sh

PROGNAME=$0
SKIP_ENABLE_SERVICES=0

usage() {
  cat << EOF >&2
Usage: $PROGNAME [-p <private_version_name>]

------------------------------------------

[-p <private_version_name>] runs for a private version

------------------------------------------
EOF
  exit 1
}
PRIVATE_VERSION_NAME=0
while getopts "p:" opt; do
  case "${opt}" in
    p)
      PRIVATE_VERSION_NAME=$OPTARG
      ;;
    *)
      usage
      ;;
  esac
done
shift "$((OPTIND - 1))"

welcome "Integration Framework Destroy Script!" "
This script will destroy resources created by terraform. 
Gcloud installation at $(which gcloud)
"

prints "Please enter environment name: (beta)"
read ENV
ENV=${ENV:-beta}
printe

TFVAR_NAME=$ENV
if [[ $PRIVATE_VERSION_NAME != 0 ]]
then
  TFVAR_NAME=$PRIVATE_VERSION_NAME
  FILE="./devops/terraform/vars/$TFVAR_NAME.tfvars"
  if [[ ! -f $FILE ]]; then
    echo "Terraform variable file does not exists: $FILE"
    return
  fi
fi

NAME="$(./devops/get_env_var.sh $TFVAR_NAME name)"
DEFAULT_REMOTE_STATE_BUCKET_NAME="$NAME-tfstate"
prints "Please enter terraform state GCP Storage bucket ($DEFAULT_REMOTE_STATE_BUCKET_NAME)"
read REMOTE_STATE_BUCKET_NAME
REMOTE_STATE_BUCKET_NAME=${REMOTE_STATE_BUCKET_NAME:-${DEFAULT_REMOTE_STATE_BUCKET_NAME}}
printe $REMOTE_STATE_BUCKET_NAME

prints "Initializing terraform"
terraform -chdir=./devops/terraform init -reconfigure -backend-config="bucket=$REMOTE_STATE_BUCKET_NAME" &
wait $!

NAME="$(./devops/get_env_var.sh $TFVAR_NAME name)"
prints "
Please confirm if you are sure to destroy all Google Cloud Platform resources created for $TFVAR_NAME
"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done

terraform \
  -chdir=./devops/terraform destroy \
  -var-file="./vars/$TFVAR_NAME.tfvars"
