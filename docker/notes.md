# docker-practice

- restAPI - https://youtu.be/lsMQRaeKNDk 
    - caching
    - resource
    - building blocks of restAPI: request & response
        - REQUEST: operation, end pt, parameters/body, headers
        - CRUD = POST, GET, PUT, DELETE
        - RESPONSE: typically in json


## Commands to delete a docker image
List all active containers
```sh
docker ps
```
List all containers, including those that have stopped or exited
```sh
docker ps -a
```
Remove the image: docker rm <reponame>:<tag>
```sh
docker rm hello-repo:latest 
```
