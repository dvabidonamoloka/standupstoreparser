Parser for standupstore.ru

### Run the app in docker
Running prod version
```sh
docker-compose up -d
```
Running dev version, which has port forwarding
```sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### How to run jupyter notebook in docker
1. Copy repo and go to repo folder. Also you need to install docker, if you didn't yet.
2. Run docker container with mounted directory. Dont't worry, if you don't have an image, it'll be downloaded automatically.
    ```sh
    docker run -dit -v ${PWD}:/home/jovyan/ -p 8888:8888 jupyter/base-notebook
    ```
    As you can see, we got container id as an output.
    ```sh
    bb56438780fa6c8ffd9b26927259b246b30be54673bf678228c94af
    ```
3. We need token to get access for jupyter server. We can get logs to see token by simply run 'docker logs' command with specifying containder id. First few letter of the container id will be enought. Remember to replace "bb56" with first letter of your container.
    ```sh
    docker logs bb56
    ```
4. Open http://localhost:8888/ in your browser and enter a token.
5. Ready! Now all of your notebooks will be saved in repo folder.
