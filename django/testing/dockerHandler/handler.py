import docker

class DockerHandler:
    def __init__(self) -> None:
        self.client = docker.from_env()
    
    def get_container_list(self) -> list:
        return self.client.containers.list()
    
    # def start_container(self):
        

cli = DockerHandler()
print(cli.get_container_list())

