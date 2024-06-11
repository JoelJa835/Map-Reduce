# Variables
SERVICE_NAME := ui-service
UI_DEPLOYMENT_FILE := kubernetes/deployments/ui-service-deployment.yaml
UI_SERVICE_FILE := kubernetes/services/ui-service.yaml
AUTH_DEPLOYMENT_FILE := kubernetes/deployment/auth-statefulset.yaml
AUTH_SERVICE_FILE := kubernetes/services/auth-service.yaml


# Targets
.PHONY: deploy

deploy:
	kubectl create -f $(UI_DEPLOYMENT_FILE)
	kubectl create -f $(UI_SERVICE_FILE)
	kubectl create -f $(AUTH_DEPLOYMENT_FILE)
	kubectl create -f $(AUTH_SERVICE_FILE)



.PHONY: clean

clean:
	kubectl delete -f $(UI_DEPLOYMENT_FILE)
	kubectl delete -f $(UI_SERVICE_FILE)
	kubectl delete -f $(AUTH_DEPLOYMENT_FILE)
	kubectl delete -f $(AUTH_SERVICE_FILE)
