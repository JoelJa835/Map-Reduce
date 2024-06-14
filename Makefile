# Variables
SERVICE_NAME := ui-service
UI_DEPLOYMENT_FILE := kubernetes/deployments/ui-service-deployment.yaml
UI_SERVICE_FILE := kubernetes/services/ui-service.yaml
AUTH_DEPLOYMENT_FILE := kubernetes/deployments/auth-service-statefull-set.yaml
AUTH_SERVICE_FILE := kubernetes/services/auth-service.yaml
CASSANDRA_DEPLOYMENT_FILE := kubernetes/dds/cassandra.yaml
CASSANDRA_SERVICE_FILE := kubernetes/services/cassandra-service.yaml
CASSANDRA_PV_FILE := kubernetes/dds/cassandra-pv.yaml
MINIO_STORAGE_FILE := kubernetes/storage/minio-storage-class.yaml
MINIO_PVC_FILE := kubernetes/storage/minio-pvc.yaml
MINIO_PV_FILE := kubernetes/storage/minio-pv.yaml
MINIO_DEPLOYMENT_FILE := kubernetes/storage/minio-deployment.yaml
MINIO_SERVICE_FILE := kubernetes/services/minio-service.yaml

# Targets
.PHONY: deploy

deploy:
	kubectl create -f $(UI_DEPLOYMENT_FILE)
	kubectl create -f $(UI_SERVICE_FILE)
	kubectl create -f $(AUTH_DEPLOYMENT_FILE)
	kubectl create -f $(AUTH_SERVICE_FILE)
	kubectl create -f $(CASSANDRA_PV_FILE)
	kubectl create -f $(CASSANDRA_DEPLOYMENT_FILE)
	kubectl create -f $(CASSANDRA_SERVICE_FILE)
	kubectl create -f $(MINIO_STORAGE_FILE)
	kubectl create -f $(MINIO_PV_FILE)
	kubectl create -f $(MINIO_PVC_FILE)
	kubectl create -f $(MINIO_DEPLOYMENT_FILE)
	kubectl create -f $(MINIO_SERVICE_FILE)


.PHONY: clean

clean:
	kubectl delete -f $(UI_DEPLOYMENT_FILE)
	kubectl delete -f $(UI_SERVICE_FILE)
	kubectl delete -f $(AUTH_DEPLOYMENT_FILE)
	kubectl delete -f $(AUTH_SERVICE_FILE)
	kubectl delete -f $(CASSANDRA_DEPLOYMENT_FILE)
	kubectl delete -f $(CASSANDRA_SERVICE_FILE)
	kubectl delete -f $(CASSANDRA_PV_FILE)
	kubectl delete -f $(MINIO_DEPLOYMENT_FILE)
	kubectl delete -f $(MINIO_PVC_FILE)
	kubectl delete -f $(MINIO_PV_FILE)
	kubectl delete -f $(MINIO_STORAGE_FILE)
	kubectl delete -f $(MINIO_SERVICE_FILE)