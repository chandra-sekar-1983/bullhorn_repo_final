#!/bin/bash
set -e
source ./devops/admin/constants.sh
source ./devops/admin/tools.sh

PROGNAME=$0
SKIP_ENABLE_SERVICES=0

usage() {
  cat << EOF >&2
Usage: $PROGNAME [-s] [-p <private_version_name>]

------------------------------------------
[-s] skips enabling required services:
   - artifactregistry.googleapis.com
   - compute.googleapis.com
   - cloudbuild.googleapis.com
   - run.googleapis.com
   - iam.googleapis.com

[-p <private_version_name>] runs for a private version

------------------------------------------
EOF
  exit 1
}
PRIVATE_VERSION_NAME=0
while getopts "sp:" opt; do
  case "${opt}" in
    s)
      SKIP_ENABLE_SERVICES=1
      ;;
    p)
      SKIP_ENABLE_SERVICES=1
      PRIVATE_VERSION_NAME=$OPTARG
      ;;
    *)
      usage
      ;;
  esac
done
shift "$((OPTIND - 1))"

welcome "Integration Framework Manual Deployment Script!" "
This script will enable google cloud platform services, build app's docker image,
push it to the artifact registry, initialize terraform, after verifying user's approval 
runs terraform apply.
Gcloud installation at $(which gcloud)
"

# TODO: Create function, take bash script argument and ask if it's not provided.
prints "Please enter environment name: (beta)"
read ENV
ENV=${ENV:-beta}
printe $ENV

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
REMOTE_STATE_BUCKET_NAME="$NAME-tfstate"
prints "Checking remote state bucket: $REMOTE_STATE_BUCKET_NAME. Please wait..."

if output=$(gsutil ls -L -b gs://$REMOTE_STATE_BUCKET_NAME 2>&1 > /dev/null); then
  echo "Bucket exists skipping creation"
else
  if [[ $output == *"BucketNotFoundException"* ]]
  then
    echo "Bucket does not exist. Creating..."
    gsutil mb gs://$REMOTE_STATE_BUCKET_NAME
  else
    echo "Cannot access bucket. Backing off."
    echo $output
    exit;
  fi
fi

printe "Done"

prints "Initializing terraform"
terraform -chdir=./devops/terraform init -reconfigure -backend-config="bucket=$REMOTE_STATE_BUCKET_NAME" &
wait $!

prints "Please enter the image tag: ($COMMIT_SHA)"
read IMAGE_TAG
IMAGE_TAG=${IMAGE_TAG:-${COMMIT_SHA}}
printe $IMAGE_TAG
export COMMIT_SHA=$COMMIT_SHA

prints "Acquiring variables from given terraform variable file. Please wait..."
console_name='superrandomname'
try_count=0
while [[ $NAME != $console_name && $try_count < 5 ]]
do
  plain_vars="$(echo '"${var.name},${var.env},${var.debug},${local.base_url},${local.image_base},${var.project_region},${var.cloud_run_service_account},${var.project_id},${local.registry},${local.registry_repo},@@@@@@@${join("+++++++" ,[for key, value in local.env_vars: "${key}=${value}"])}-------"' | terraform -chdir=./devops/terraform console -var "image_tag=$IMAGE_TAG" -var-file=./vars/$TFVAR_NAME.tfvars)"
  prints "$plain_vars"
  vars=$(echo $plain_vars | sed 's/\"//g')
  var_array=($(echo $vars | tr ',' '\n'))
  console_name="${var_array[0]}"
  ((try_count++))
done

if [[ $try_count -ge 5 ]]
then
  prints "Backing off. Cannot acquire terraform variables"
  exit
fi

ENV="${var_array[1]}"
DEBUG="${var_array[2]}"
BASE_URL="${var_array[3]}"
IMAGE_BASE="${var_array[4]}"
IMAGE="${IMAGE_BASE}:${IMAGE_TAG}"
REGION="${var_array[5]}"
GCP_RUN_SERVICE_ACCOUNT="${var_array[6]}"
PROJECT_ID="${var_array[7]}"
REGISTRY="${var_array[8]}"
REGISTRY_REPO="${var_array[9]}"
printe """Acquired...\n
  $> Please confirm the variables\n\n
  $> PROJECT_ID=$PROJECT_ID\n
  $> NAME=$NAME\n
  $> ENV=$ENV\n
  $> DEBUG=$DEBUG\n
  $> BASE_URL=$BASE_URL\n
  $> IMAGE=$IMAGE\n
  $> REGION=$REGION\n
  $> GCP_RUN_SERVICE_ACCOUNT=$GCP_RUN_SERVICE_ACCOUNT\n
  $> REGISTRY=$REGISTRY\n
  $> REGISTRY_REPO=$REGISTRY_REPO\n
"""
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done

env_vars="${vars##*@@@@@@@}"
env_vars="${env_vars%%-------*}"
export NAME=$NAME
export ENV=$ENV
export DEBUG=$DEBUG
export BASE_URL=$BASE_URL
export $(echo $env_vars | tr '+++++++' '\n' | cat)

prints "Please enter service account email to impersonate: (iac-service-account@$PROJECT_ID.iam.gserviceaccount.com)"
read SERVICE_ACCOUNT
SERVICE_ACCOUNT=${SERVICE_ACCOUNT:-"iac-service-account@$PROJECT_ID.iam.gserviceaccount.com"}
printe $SERVICE_ACCOUNT

if [[ $SKIP_ENABLE_SERVICES -eq 0 ]]
then
  prints "Enabling artifactregistry.googleapis.com"
  gcloud services enable artifactregistry.googleapis.com
  printe "Done"

  prints "Enabling compute.googleapis.com"
  gcloud services enable compute.googleapis.com
  printe "Done"

  prints "Enabling run.googleapis.com"
  gcloud services enable run.googleapis.com

  prints "Enabling cloudbuild.googleapis.com"
  gcloud services enable cloudbuild.googleapis.com
  printe "Done"

  prints "Enabling iam.googleapis.com"
  gcloud services enable iam.googleapis.com
  printe "Done"

  prints "Enabling dns.googleapis.com"
  gcloud services enable dns.googleapis.com
  printe "Done"
fi

prints "Checking artifact registry repo: $REGISTRY/$PROJECT_ID/$REGISTRY_REPO. Please wait..."
if output=$(gcloud artifacts repositories describe $REGISTRY_REPO --location=$REGION 2>&1 > /dev/null); then
  echo "Artifact registry found."
else
  if [[ $output == *"NOT_FOUND"* ]]
  then
    echo "Artifact registry $NAME in $REGION not found. Creating..."
    gcloud artifacts repositories create $REGISTRY_REPO --location=$REGION --repository-format=docker
  else
    echo $output
    echo "Cannot access artifact registry. Backing off"
    exit;
  fi
fi
printe "Done"

prints "Impersonating service account and docker login to registry"
gcloud auth print-access-token \
  --impersonate-service-account $SERVICE_ACCOUNT | docker login \
  -u oauth2accesstoken \
  --password-stdin $REGISTRY &
wait $!
printe "Done"


prints "Building static files"
cd ./client
npm install && npm run $ENV
cd ../
cp $OSCWD/client/static/index.html $OSCWD/server/templates/index.html
printe "Done"

prints "Building docker image"
docker build \
  -t "$IMAGE" \
  -f "./docker_files/$ENV.Dockerfile" \
  --platform=linux/amd64 \
  .
rm -rf ./templates
printe "Built image: $IMAGE"

prints "Pushing docker image"
docker push "$IMAGE"
printe "Done"

prints "Running 'terraform plan'..."
terraform -chdir=./devops/terraform plan -var="image_tag=$IMAGE_TAG" -var-file="./vars/$TFVAR_NAME.tfvars" -out=tf.plan &
wait $!
printe "Done"


function apply() {
  terraform -chdir=./devops/terraform apply -auto-approve tf.plan &
  wait $!
  rm ./devops/terraform/tf.plan
}

# TODO: Nice to have rollback after this point. Though terraform plan should be correct before
# reaching this point.
prints "Enter 1 to apply this plan, OR 2 to exit (Won't rollback anychange)"

select yn in "Yes" "No"; do
    case $yn in
        Yes ) apply; break;;
        No ) exit;;
    esac
done
printe "Done"

prints "Deploying static files"
gsutil -m rsync -r $OSCWD/client/static "gs://$NAME-static-bucket/static"
printe "Done"
