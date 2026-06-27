---
title: Jenkins持续集成指南
aliases: [Jenkins教程, CI/CD, 持续集成]
tags: [jenkins, ci/cd, 自动化]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 运维
---
# Jenkins 持续集成指南

## 概述

本指南提供Jenkins持续集成的配置方法和最佳实践。

## 1. 基础配置

### 安装Jenkins

```bash
# Ubuntu/Debian
wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt update
sudo apt install jenkins

# CentOS/RHEL
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat/jenkins.io.key
sudo yum install jenkins

# Docker
docker run -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts
```

### 初始配置

```bash
# 获取初始密码
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# 访问Web界面
http://localhost:8080
```

## 2. Pipeline配置

### 基础Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        JAVA_HOME = '/usr/lib/jvm/java-11'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/user/repo.git'
            }
        }
        
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        
        stage('Test') {
            steps {
                sh 'mvn test'
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'cp target/*.jar /opt/app/'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            echo 'Build successful!'
        }
        failure {
            echo 'Build failed!'
        }
    }
}
```

### 多分支Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Test') {
                    steps {
                        sh 'make test-unit'
                    }
                }
                stage('Integration Test') {
                    steps {
                        sh 'make test-integration'
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'make deploy'
            }
        }
    }
}
```

## 3. 常用插件

### 必装插件

```bash
# Git插件
Git plugin

# Pipeline插件
Pipeline: Stage View
Pipeline: Declarative

# 构建工具插件
Maven Integration
NodeJS Plugin

# 部署插件
Deploy to container
Publish Over SSH

# 通知插件
Email Extension
Slack Notification
```

### 插件配置

```yaml
# Maven配置
Manage Jenkins -> Global Tool Configuration -> Maven
Name: Maven 3.8
Install automatically: true

# Node.js配置
Manage Jenkins -> Global Tool Configuration -> NodeJS
Name: NodeJS 16
Install automatically: true
```

## 4. 构建触发器

### 触发器类型

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    triggers {
        // 定时构建
        cron('H 2 * * *')
        
        // SCM变更触发
        pollSCM('H/5 * * * *')
        
        // GitHub webhook触发
        githubPush()
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
    }
}
```

### Webhook配置

```bash
# GitHub Webhook
Payload URL: http://jenkins.example.com/github-webhook/
Content type: application/json
Events: Push events
```

## 5. 构建环境

### 环境变量

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        JAVA_HOME = '/usr/lib/jvm/java-11'
        PATH = "${JAVA_HOME}/bin:${env.PATH}"
        APP_VERSION = '1.0.0'
    }
    
    stages {
        stage('Build') {
            steps {
                sh 'echo $JAVA_HOME'
                sh 'echo $APP_VERSION'
            }
        }
    }
}
```

### 凭据管理

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        DOCKER_CREDENTIALS = credentials('docker-cred')
        AWS_CREDENTIALS = credentials('aws-cred')
    }
    
    stages {
        stage('Push') {
            steps {
                sh 'echo $DOCKER_CREDENTIALS_PSW | docker login -u $DOCKER_CREDENTIALS_USR --password-stdin'
                sh 'docker push myapp:latest'
            }
        }
    }
}
```

## 6. 构建步骤

### 构建工具

```groovy
// Maven构建
stage('Build') {
    steps {
        sh 'mvn clean package -DskipTests'
    }
}

// Gradle构建
stage('Build') {
    steps {
        sh './gradlew build'
    }
}

// npm构建
stage('Build') {
    steps {
        sh 'npm install'
        sh 'npm run build'
    }
}
```

### 测试

```groovy
// 单元测试
stage('Test') {
    steps {
        sh 'mvn test'
    }
    post {
        always {
            junit 'target/surefire-reports/*.xml'
        }
    }
}

// 代码覆盖率
stage('Coverage') {
    steps {
        sh 'mvn jacoco:report'
    }
    post {
        always {
            jacoco()
        }
    }
}
```

## 7. 部署配置

### SSH部署

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Deploy') {
            steps {
                sshagent(['ssh-cred']) {
                    sh 'scp target/*.jar user@server:/opt/app/'
                    sh 'ssh user@server "sudo systemctl restart myapp"'
                }
            }
        }
    }
}
```

### Docker部署

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build Docker') {
            steps {
                sh 'docker build -t myapp:latest .'
            }
        }
        
        stage('Push Docker') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-cred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    sh 'docker push myapp:latest'
                }
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'docker-compose down'
                sh 'docker-compose up -d'
            }
        }
    }
}
```

## 8. 通知配置

### 邮件通知

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    post {
        failure {
            emailext (
                subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build failed. Check: ${env.BUILD_URL}",
                to: 'team@example.com'
            )
        }
        success {
            emailext (
                subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build successful. Check: ${env.BUILD_URL}",
                to: 'team@example.com'
            )
        }
    }
}
```

### Slack通知

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    post {
        failure {
            slackSend (
                color: 'danger',
                message: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }
        success {
            slackSend (
                color: 'good',
                message: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }
    }
}
```

## 9. 最佳实践

### 代码组织

```
project/
  Jenkinsfile
  docker-compose.yml
  src/
  tests/
  scripts/
    deploy.sh
    test.sh
```

### 安全实践

```groovy
// 使用凭据
withCredentials([usernamePassword(credentialsId: 'cred', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
    sh 'echo $PASS | docker login -u $USER --password-stdin'
}

// 使用vault
withVault([vaultSecrets: [[path: 'secret/myapp', secretValues: [[envVar: 'DB_PASS', vaultKey: 'password']]]]]) {
    sh 'echo $DB_PASS'
}
```

## 相关页面

- [[Docker容器化指南]]
- [[Git版本控制指南]]
- [[Kubernetes容器编排指南]]
