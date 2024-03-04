# program-api
Tailor-made sports program generation API using LLM, FastAPI and deployed on GCP

Live on : https://train-programs.ai/

# HOWTO
- docker build -t <image_name> .
- docker run -p 8080:8080 <image_name>

# Deploy on GCP 
- gcloud auth configure-docker <pkg_name>
- cat <config_file.json> | docker login -u _json_key --password-stdin https://<pkg_name>
- docker tag <image_name>:<tag> <pkg_name>/<project_id>/<repository>/<image_name>:<tag>
- docker push <region>-docker.pkg.dev/<project_id>/<repository>/<image_name>:<tag>
- [Documentation](https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling?hl=fr)

# Google Cloud Run (GCR)
- Deploy : gcloud run deploy <service_name> --image <pkg_name>/<project_id>/<repository>/<image>:<tag> --region <region> --allow-unauthenticated --timeout <timeout> --set-env-vars <env_var_name>=<env_var_value>
- Get logs : gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=<service_name>" --project=<project_id> --limit=100 --format="value(textPayload)"

# Google Kubernetes Engine (GKE)
- Create a Kubernetes Cluster : gcloud container clusters create CLUSTER-NAME --region <region>
- Get Credentials for the Cluster : gcloud container clusters get-credentials CLUSTER-NAME --region <region>
- Create deployment.yaml
- Deploy : kubectl apply -f deployment.yaml
- Expose deployment : kubectl expose deployment <deployment_name> --type=LoadBalancer --port=80 --target-port=80
- Access the API : kubectl get services
- Secure the API
