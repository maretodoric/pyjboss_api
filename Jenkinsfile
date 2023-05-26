pipeline {
    agent {label 'node2'}

    stages {
        stage('Clone Repo') {
            steps {
                sh 'ls -la'
                git 'https://github.com/maretodoric/pyjboss_api.git'
            }
        }

        stage('Test') {
            steps {
                withCredentials([string(credentialsId: 'java8url', variable: 'JAVA_URL')]) {
                    withCredentials([string(credentialsId: 'wildfly10url', variable: 'WILDFLY_URL')]) {
                        sh '''
                            cd test

                            echo "Downloading Java 8"
                            wget ${JAVA_URL}

                            echo "Downloading Wildfly 10"
                            wget ${WILDFLY_URL}

                            echo "Running tests"
                            for python in 3.10 3.9 3.8 3.7 3.6; do
                                echo "Preparing Dockerfile for python version $python"
                                sed -i "s/^FROM python.*/FROM python:$python/g" Dockerfile

                                docker build . -t pyjboss_pipeline_test && docker run --rm --ulimit nofile=122880:122880 pyjboss_pipeline_test
                                docker image rm pyjboss_pipeline_test
                            done
                        '''
                    }
                }
            }
        }
    }
}
