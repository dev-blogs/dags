pipeline {
  agent {
    kubernetes {
      label 'custom-k8s-agent'
      yamlFile 'mvnBuildPod.yaml'
      defaultContainer 'jnlp'
    }
  }

  environment {
    OS_USER="dev"
    OS_PASSWORD="dev"
    WORKING_DIR='dags'
    CONFIG="/tmp/config"
    NAMESPACE="image-uploader"
    SERVICE_NAME="dags-deployer-image"
    DOCKER_HUB_SECRET="docker-hub-password"
    OS_HOST="https://ocp1.192.168.1.20.nip.io:8443"
    DAGS_DEPLOYMENT_CONFIG="deployment/dags-deployment.yaml"
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
          deploy_image()
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
  sh '''
    export DOCKER_CONFIG=/tmp/docker-config

    /usr/bin/oc login --insecure-skip-tls-verify --config=${CONFIG} -u ${OS_USER} -p ${OS_PASSWORD} ${OS_HOST}
    /usr/bin/oc get secret ${DOCKER_HUB_SECRET} --config=${CONFIG} -n ${NAMESPACE} -o go-template --template="{{.data.password}}" |\
    base64 -d |\
    docker login -u ${DOCKER_HUB_LOGIN} --password-stdin

    docker build -t ${SERVICE_NAME} .
  '''
}

def deploy_image() {
  sh '''
    export DOCKER_CONFIG=/tmp/docker-config

    /usr/bin/oc login --insecure-skip-tls-verify --config=${CONFIG} -u ${OS_USER} -p ${OS_PASSWORD} ${OS_HOST}
    /usr/bin/oc get secret ${DOCKER_HUB_SECRET} --config=${CONFIG} -n ${NAMESPACE} -o go-template --template="{{.data.password}}" |\
    base64 -d |\
    docker login -u ${DOCKER_HUB_LOGIN} --password-stdin

    docker tag ${SERVICE_NAME} ${DOCKER_HUB_LOGIN}/${SERVICE_NAME}
    docker push ${DOCKER_HUB_LOGIN}/${SERVICE_NAME}

    # Check if the job exists
    if /usr/bin/oc get jobs --config=${CONFIG} ${SERVICE_NAME} -n ${NAMESPACE} > /dev/null 2>&1; then
      echo "Job ${SERVICE_NAME} exists. Replacing it with the new job."
      /usr/bin/oc delete job ${SERVICE_NAME} -n ${NAMESPACE} --config=${CONFIG}
    else
      echo "Job ${SERVICE_NAME} does not exist. New job will be created."
    fi

    # Deploy the application
    /usr/bin/oc apply -f ${DAGS_DEPLOYMENT_CONFIG}

    echo "Deployment complete"
  '''
}
