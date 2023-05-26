pipeline {
    agent {label 'node2'}

    stages {
        stage('Clone Repo') {
            steps {
                script {
                    // Get branch name
                    GIT_BRANCH_LOCAL = sh (
                        script: 'echo ${GIT_BRANCH#*/}',
                        returnStdout: true
                    ).trim()
                    
                    echo "Cloning Git Branch: ${GIT_BRANCH_LOCAL}"
                    git credentialsId: 'mtodoric_ssh', url: 'git@github.com:maretodoric/pyjboss_api.git', branch: GIT_BRANCH_LOCAL
                }
            }
        }

        stage('Test') {
            steps {
                echo "Downloading Java 8"
                withCredentials([string(credentialsId: 'java8url', variable: 'DL_URL')]) {
                    sh 'cd test; wget ${DL_URL} > /dev/null 2>&1'

                }

                echo "Downloading Wildfly 10"
                withCredentials([string(credentialsId: 'wildfly10url', variable: 'DL_URL')]) {
                    sh 'cd test; wget ${DL_URL} > /dev/null 2>&1'
                }

                echo "Running tests"
                sh '''
                    cd test

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