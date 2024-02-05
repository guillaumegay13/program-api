# program-api
Tailor-made sports program generation API using LLM, FastAPI and deployed on GCP

# HOWTO
- docker build -t fastapi-app .
- docker run -p 8080:8080 fastapi-app

# Deploy on GCP (https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling?hl=fr)
- gcloud auth configure-docker europ-west9-docker.pkg.dev
- cat program-api-413117-cda9396404e9.json | docker login -u _json_key --password-stdin https://europe-west9-docker.pkg.dev
- docker tag fastapi-app:latest europe-west9-docker.pkg.dev/program-api-413117/program/fastapi-app:lates
t
- docker push europe-west9-docker.pkg.dev/program-api-413117/program/fastapi-app:latest

# Google Cloud Run (GCR)
- Deploy : gcloud run deploy program-api-service --image europe-west9-docker.pkg.dev/program-api-413117/program/fastapi-app --region europe-west1 --allow-unauthenticated
- https://program-api-service-qqoaabgxbq-ew.a.run.app
- Get logs : gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=program-api-service" --project=program-api-413117 --limit=100 --format="value(textPayload)"

# Google Kubernetes Engine (GKE)
- Create a Kubernetes Cluster : gcloud container clusters create CLUSTER-NAME --region europe-west1
- Get Credentials for the Cluster : gcloud container clusters get-credentials CLUSTER-NAME --region europe-west1
- Create deployment.yaml
- Deploy : kubectl apply -f deployment.yaml
- Expose deployment : kubectl expose deployment fastapi-app-deployment --type=LoadBalancer --port=80 --target-port=80
- Access the API : kubectl get services
- Secure the API