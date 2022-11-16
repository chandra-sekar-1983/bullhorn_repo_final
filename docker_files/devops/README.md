## Google Cloud Platform
Integration framework has a built-in terraform support to automate provisioning and deployment. You can find IaC under terraform folder.


![Integration Framework (12)](https://user-images.githubusercontent.com/6083754/164491063-a5491439-7dab-4457-a21c-bd423a074b58.png)


If you are planning to host your solution in GCP, follow below steps only *ONCE* to provision CI/CD using terraform;
1. Create a GCP project
2. Create a group of engineers who would have access to deploy private versions.
3. Run create service account script
```bash
./devops/admin/create_service_account.sh
```
4. Create required secrets (dialpad-client-id, dialpad-client-secret, etc.) using add_secret script
```bash
./devops/admin/add_secret.sh
```
5. Run manual_run.sh script (Apart from this first run; only run this if a secret has been updated)
```bash
./devops/admin/manual_run.sh
```

After this point, you could just let automated CI/CD do its job. A push to configured <BRANCH> will trigger a deployment. 
