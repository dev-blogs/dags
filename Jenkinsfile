pipeline {
  agent {
    kubernetes {
      label 'custom-k8s-agent'
      yamlFile 'mvnBuildPod.yaml'
      defaultContainer 'jnlp'
    }
  }

  environment {
    WORKING_DIR='dags'
    CONFIG="/tmp/config"
    SERVICE_ACCOUNT='airflow-ca'
    DOCKER_HUB_LOGIN="devblogs1"
    SERVICE_NAME="dags-deploy"
    DOCKER_IMAGE="${DOCKER_HUB_LOGIN}/${SERVICE_NAME}"
    NAMESPACE="image-uploader"
    DOCKER_HUB_PASSWORD_SECRET="docker-hub-password"
    OS_HOST="https://ocp1.192.168.1.20.nip.io:8443"
    OS_USER="dev"
    OS_PASSWORD="dev"
  }

  stages {
		
    stage('Image build') {
      steps {
        container('java-container') {
		  sh "ls -la"
          build_image()
        }
      }
    }

    stage('Deploy') {
      steps {
        container('java-container') {
          dir ('{$WORKING_DIR}') {
            deploy_image()
          }
        }
      }
    }

    stage('Check') {
      steps {
        container('java-container') {
          dir ('{$WORKING_DIR}') {
            sh "ls -la"
          }
        }
      }
    }
  }
}

def build_image() {
  sh "docker build -t ${SERVICE_NAME} ."
}

def deploy_image() {
  sh '''
  export DOCKER_CONFIG=/tmp/docker-config
  
  /usr/bin/oc login --insecure-skip-tls-verify --config=${CONFIG} -u ${OS_USER} -p ${OS_PASSWORD} ${OS_HOST}
  /usr/bin/oc get secret ${DOCKER_HUB_PASSWORD_SECRET} --config=${CONFIG} -n ${NAMESPACE} -o go-template --template="{{.data.password}}" | base64 -d | docker login -u ${DOCKER_HUB_LOGIN} --password-stdin
  
  docker tag ${SERVICE_NAME} ${DOCKER_HUB_LOGIN}/${SERVICE_NAME}
  docker push ${DOCKER_HUB_LOGIN}/${SERVICE_NAME}
  
  # Check if the service exists
  if /usr/bin/oc get service --config=${CONFIG} ${SERVICE_NAME} -n ${NAMESPACE} > /dev/null 2>&1; then
      echo "Service ${SERVICE_NAME} exists. Replacing it with the new service."
      /usr/bin/oc delete service ${SERVICE_NAME} -n ${NAMESPACE} --config=${CONFIG}
  else
      echo "Service ${SERVICE_NAME} does not exist. New service will be created."
  fi
  
  # Check if the deployment exists
  if /usr/bin/oc get dc --config=${CONFIG} ${SERVICE_NAME} -n ${NAMESPACE} > /dev/null 2>&1; then
      echo "Deployment ${SERVICE_NAME} exists. Replacing it with the new deployment."
      /usr/bin/oc delete dc ${SERVICE_NAME} -n ${NAMESPACE} --config=${CONFIG}
  else
      echo "Deployment ${SERVICE_NAME} does not exist. New deployment will be created."
  fi
  
  # Check if the imagestream exists
  if /usr/bin/oc get imagestream --config=${CONFIG} ${SERVICE_NAME} -n ${NAMESPACE} > /dev/null 2>&1; then
      echo "Imagestream ${SERVICE_NAME} exists. Replacing it with the new imagestream."
      /usr/bin/oc delete imagestream ${SERVICE_NAME} -n ${NAMESPACE} --config=${CONFIG}
  else
      echo "Imagestream ${SERVICE_NAME} does not exist. New imagestream will be created."
  fi
  
  # Deploy the application
  /usr/bin/oc new-app --docker-image=${DOCKER_IMAGE} --name=${SERVICE_NAME} -n ${NAMESPACE} --config=${CONFIG}
  # Attach pv to container
  /usr/bin/oc login --token=$(/usr/bin/oc serviceaccounts get-token ${SERVICE_ACCOUNT} -n ${NAMESPACE})
  /usr/bin/oc set volume deployment/${SERVICE_NAME} --add --name=airflow-dags-volume --mount-path=/pvc/airflow/dags --claim-name=dag-pvc
  
  # Expose the service (if needed)
  if ! /usr/bin/oc get route ${SERVICE_NAME} -n ${NAMESPACE} --config=${CONFIG} > /dev/null 2>&1; then
      /usr/bin/oc expose service ${SERVICE_NAME} -n ${NAMESPACE} --config=${CONFIG}
  fi
  
  echo "Deployment complete"
  '''
}
