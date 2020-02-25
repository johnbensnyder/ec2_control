from time import time
import os

def launch_docker(cluster_shell, image, container_name):
    if cluster_shell.cluster.Efa:
        docker_start_jupyter_lab = "docker run --gpus all -it --rm -d --net=host --name {0} " \
                                   "--uts=host --ipc=host " \
                                   "--ulimit stack=67108864 --ulimit memlock=-1 " \
                                   "--security-opt seccomp=unconfined " \
                                   "-v /opt/amazon/efa:/efa " \
                                   "-v /home/ubuntu/aws-ofi-nccl:/ofi " \
                                   "-v /home/ubuntu/ssh_container/:/root/.ssh/ " \
                                   "-v ~/shared_workspace/:/workspace/shared_workspace " \
                                   "-v ~/src/:/src " \
                                   "{1}".format(container_name, image)
    else:
        docker_start_jupyter_lab = "docker run --gpus all -it --rm -d --net=host --name {0} " \
                                   "--uts=host --ipc=host " \
                                   "--ulimit stack=67108864 --ulimit memlock=-1 " \
                                   "--security-opt seccomp=unconfined " \
                                   "-v /home/ubuntu/ssh_container/:/root/.ssh/ " \
                                   "-v ~/shared_workspace/:/workspace/shared_workspace " \
                                   "-v ~/src/:/src " \
                                   "{1}".format(container_name, image)
    return cluster_shell.bash(docker_start_jupyter_lab)

def forward_port(cluster_shell, notebook_port="8890", tensorboard_port="6006"):
    host = cluster_shell.cluster.public_ips[0]
    socket = "tf-socket-{}".format(int(time() * 10000))
    start_port_forwarding = "ssh -i ~/.aws/jbsnyder.pem -o StrictHostKeyChecking=no " \
                            "-M -S {0} -fNT -L {2}:localhost:8888 -L {3}:localhost:6006 ubuntu@{1}".format(socket,
                                                                            host, notebook_port, tensorboard_port)
    os.system(start_port_forwarding)
    print(os.system("ssh -S {} -O check ubuntu@{}".format(socket, host)))

def get_token(cluster_shell, container_name, port="8890"):
    token = cluster_shell.master_bash("docker exec {} bash -c \"jupyter notebook list\"".format(container_name))[0][1].split('token=')[1].split()[0]
    return "http://localhost:{}/?token={}".format(port, token)
