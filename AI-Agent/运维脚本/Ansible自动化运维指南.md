---
title: Ansible自动化运维指南
aliases: [Ansible教程, 自动化工具, 配置管理]
tags: [ansible, 自动化, 运维]
type: reference
status: published
created: 2026-06-27
updated: 2026-06-27
source: 实践经验
difficulty: intermediate
project: 运维
---
# Ansible 自动化运维指南

## 概述

本指南提供Ansible自动化运维的配置方法和最佳实践。

## 1. 基础配置

### 安装Ansible

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ansible

# CentOS/RHEL
sudo yum install epel-release
sudo yum install ansible

# pip安装
pip install ansible
```

### 配置文件

```yaml
# ansible.cfg
[defaults]
inventory = ./hosts
remote_user = ansible
private_key_file = ~/.ssh/id_rsa
host_key_checking = False

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False
```

### 主机清单

```yaml
# hosts
[webservers]
web1 ansible_host=192.168.1.101
web2 ansible_host=192.168.1.102

[dbservers]
db1 ansible_host=192.168.1.201
db2 ansible_host=192.168.1.202

[all:vars]
ansible_user=ansible
ansible_ssh_private_key_file=~/.ssh/id_rsa
```

## 2. 常用命令

### Ad-hoc命令

```bash
# 测试连接
ansible all -m ping

# 执行命令
ansible all -m shell -a "uptime"

# 复制文件
ansible all -m copy -a "src=/local/file dest=/remote/file"

# 安装软件
ansible all -m apt -a "name=nginx state=present"

# 重启服务
ansible all -m service -a "name=nginx state=restarted"
```

### Playbook执行

```bash
# 执行playbook
ansible-playbook playbook.yml

# 检查语法
ansible-playbook playbook.yml --syntax-check

# 试运行
ansible-playbook playbook.yml --check

# 指定主机
ansible-playbook playbook.yml --limit webservers
```

## 3. Playbook编写

### 基础Playbook

```yaml
# playbook.yml
---
- name: Install and configure Nginx
  hosts: webservers
  become: yes
  
  tasks:
    - name: Install Nginx
      apt:
        name: nginx
        state: present
        update_cache: yes
    
    - name: Copy Nginx configuration
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
      notify: Restart Nginx
    
    - name: Start Nginx
      service:
        name: nginx
        state: started
        enabled: yes
  
  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
```

### 变量使用

```yaml
# playbook.yml
---
- name: Configure servers
  hosts: all
  become: yes
  
  vars:
    http_port: 80
    max_clients: 200
  
  tasks:
    - name: Set HTTP port
      lineinfile:
        path: /etc/nginx/nginx.conf
        regexp: "listen"
        line: "listen {{ http_port }};"
```

### 条件判断

```yaml
# playbook.yml
---
- name: Install packages
  hosts: all
  become: yes
  
  tasks:
    - name: Install Apache (Debian)
      apt:
        name: apache2
        state: present
      when: ansible_os_family == "Debian"
    
    - name: Install Apache (RedHat)
      yum:
        name: httpd
        state: present
      when: ansible_os_family == "RedHat"
```

### 循环

```yaml
# playbook.yml
---
- name: Create users
  hosts: all
  become: yes
  
  vars:
    users:
      - name: user1
        groups: sudo
      - name: user2
        groups: sudo
  
  tasks:
    - name: Create users
      user:
        name: "{{ item.name }}"
        groups: "{{ item.groups }}"
        state: present
      loop: "{{ users }}"
```

## 4. Roles

### 目录结构

```
roles/
  nginx/
    tasks/
      main.yml
    handlers/
      main.yml
    templates/
      nginx.conf.j2
    files/
      index.html
    vars/
      main.yml
    defaults/
      main.yml
```

### Role示例

```yaml
# roles/nginx/tasks/main.yml
---
- name: Install Nginx
  apt:
    name: nginx
    state: present
    update_cache: yes

- name: Copy configuration
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify: Restart Nginx

- name: Start Nginx
  service:
    name: nginx
    state: started
    enabled: yes
```

### 使用Role

```yaml
# playbook.yml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  
  roles:
    - nginx
    - php
    - mysql
```

## 5. 常用模块

### 文件模块

```yaml
# 复制文件
- name: Copy file
  copy:
    src: /local/file
    dest: /remote/file
    owner: root
    group: root
    mode: '0644'

# 创建目录
- name: Create directory
  file:
    path: /remote/dir
    state: directory
    owner: root
    group: root
    mode: '0755'

# 模板文件
- name: Template file
  template:
    src: template.j2
    dest: /remote/file
```

### 系统模块

```yaml
# 用户管理
- name: Create user
  user:
    name: username
    groups: sudo
    state: present

# 服务管理
- name: Start service
  service:
    name: nginx
    state: started
    enabled: yes

# 包管理
- name: Install package
  apt:
    name: nginx
    state: present
    update_cache: yes
```

### 网络模块

```yaml
# 防火墙规则
- name: Allow HTTP
  ufw:
    rule: allow
    port: '80'
    proto: tcp

# DNS记录
- name: Add DNS record
  nsupdate:
    key_name: "mykey"
    key_secret: "mysecret"
    server: "dns.example.com"
    zone: "example.com"
    record: "www"
    value: "192.168.1.100"
```

## 6. 最佳实践

### 代码组织

```
ansible/
  inventories/
    production/
      hosts
      group_vars/
    staging/
      hosts
      group_vars/
  roles/
    common/
    nginx/
    php/
  playbooks/
    site.yml
    webservers.yml
    dbservers.yml
```

### 变量管理

```yaml
# group_vars/all.yml
---
http_port: 80
max_clients: 200

# group_vars/webservers.yml
---
nginx_worker_processes: 4
nginx_worker_connections: 1024

# host_vars/web1.yml
---
ansible_host: 192.168.1.101
http_port: 8080
```

### 安全实践

```yaml
# 使用vault加密敏感数据
ansible-vault create secrets.yml
ansible-vault edit secrets.yml
ansible-vault encrypt secrets.yml
ansible-vault decrypt secrets.yml

# 执行时输入密码
ansible-playbook playbook.yml --ask-vault-pass
```

## 7. 调试技巧

### 调试命令

```bash
# 详细输出
ansible-playbook playbook.yml -v
ansible-playbook playbook.yml -vvv

# 试运行
ansible-playbook playbook.yml --check

# 逐步执行
ansible-playbook playbook.yml --step
```

### 调试任务

```yaml
# 调试输出
- name: Debug variable
  debug:
    var: my_variable
    verbosity: 1

# 调试消息
- name: Debug message
  debug:
    msg: "The value of my_variable is {{ my_variable }}"
```

## 相关页面

- [[Linux运维常用命令]]
- [[Docker容器化指南]]
- [[Kubernetes容器编排指南]]
