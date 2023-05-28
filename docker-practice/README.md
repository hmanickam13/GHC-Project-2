# What is in this directory?

## Contents
1. app.js
Simple nodejs app

2. Dockerfile
File needed to create a docker image

3. nodes.md
Resources I used to learn docker

## Prerequisite
Docker must be installed on your macne/environment

## How do I create a docker image?
Follow the following commands:<br>
**Step 1**: Build docker image
```sh
docker build -t hello-docker .
```
**Step 2**: Verify creation of docker image
```sh
docker image ls
```
**Step 3**: Run app
```sh
docker run hello-docker .
```
