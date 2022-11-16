#!/bin/bash
set -e
source ./devops/admin/constants.sh
source ./devops/admin/tools.sh

welcome "Integration Framework Create Framework IaC Service Account script!" "
Gcloud installation at $(which gcloud)
Gcloud config: \n $(gcloud config list)
"

prints "Please enter project ID"
read PROJECT_ID

prints "Please confirm included permissions"
echo "$(cat $OSCWD/devops/admin/service-role.yml)"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done
printe

prints "Please enter impersonator group email: (integrations-eng@dialpad.com)"
read GROUP_EMAIL
GROUP_EMAIL=${GROUP_EMAIL:-integrations-eng@dialpad.com}
printe $GROUP_EMAIL

prints "Creating iac_service_role"
gcloud iam roles create iac_service_role --project=$PROJECT_ID --file=$OSCWD/devops/admin/service-role.yml 
printe "Created"

prints "Creating service account: iac-service-account"
gcloud iam service-accounts create iac-service-account \
    --description="Service account for framework IaC" \
    --display-name="Framework IaC Service Account"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:iac-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="projects/$PROJECT_ID/roles/iac_service_role"

gcloud iam service-accounts add-iam-policy-binding \
    iac-service-account@$PROJECT_ID.iam.gserviceaccount.com \
    --member="group:$GROUP_EMAIL" \
    --role="roles/iam.serviceAccountUser"
printe
