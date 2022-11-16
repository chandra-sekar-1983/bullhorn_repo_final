#!/bin/bash
set -e
source ./devops/admin/constants.sh
source ./devops/admin/tools.sh

set -e
source ./devops/admin/constants.sh
source ./devops/admin/tools.sh

welcome "Integration Framework Provision Script!" "
This script will add a new secret to referencing project secret manager 
Gcloud installation at $(which gcloud)
"

SECRET_FILE=$(mktemp)
echo $SECRET_FILE
while true
do
  prints "Please enter secret ID"
  read SECRET_ID
  printe $SECRET_ID

  gcloud secrets create $SECRET_ID
  prints "Please enter secret"
  read -s SECRET_VALUE

  echo $SECRET_VALUE > $SECRET_FILE
  gcloud secrets versions add $SECRET_ID --data-file=$SECRET_FILE &
  wait $!
  prints "Would you like to add another secret?"
  select yn in "Yes" "No"; do
    case $yn in
      Yes ) break;;
      No ) rm $SECRET_FILE; exit;;
    esac
  done
  printe
done
rm $SECRET_FILE
