# Variables
SERVICE_NAME := ui-service
DEPLOYMENT_FILE := kubernetes/deployments/ui-service-deployment.yaml
SERVICE_FILE := kubernetes/services/ui-service.yaml

# Targets
.PHONY: deploy

deploy:
	kubectl create -f $(DEPLOYMENT_FILE)
	kubectl create -f $(SERVICE_FILE)

.PHONY: clean

clean:
	kubectl delete -f $(DEPLOYMENT_FILE)
	kubectl delete -f $(SERVICE_FILE)
