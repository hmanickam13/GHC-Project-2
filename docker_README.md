# What is in this directory?

## Contents
1. app.js
A simple nodejs app

2. Dockerfile
This is the file needed to create a docker image

3. nodes.md
Contains resources I used to learn docker

## Prerequisite
Docker must be installed on your macne/environment

## How do I create a docker image?
Follow the following commands:<br>
**Step 1**: Build docker image
```sh
docker build -t ghcp2 .
```
**Step 2**: Verify creation of docker image by listing all images on your system
```sh
docker image ls
```
**Step 3**: Run app
```sh
docker run ghcp2 .
```

## How do I delete a docker image?
List all active containers
```sh
docker ps
```
List all containers, including those that have stopped or exited
```sh
docker ps -a
```
Method 1:
Remove the image using it's repo name: docker rm <reponame>:<tag>
```sh
docker rm ghcp2:latest 
```
Method 2: 
Remove the image by using it's image_id
docker image rm <image_id>