'''
For mulitnode docker communication with mpi, we need to set up ssh connections that will redirect
to the containers and create a hostfile for mpi
'''

import os
from pathlib import Path

def create_hostfiles(cluster_shell, file_location='~/shared_workspace/hosts', gpus=8):
    '''

    Parameters
    ----------
    cluster_shell: an instance of a cluster shell connected to an active cluster

    Returns
    -------
    None: creates host files on each node
    '''
    host_text = '\n'.join(["{} slots={}".format(node, gpus) for node in cluster_shell.cluster.private_ips])
    cluster_shell.bash("echo \"{}\" >> {}".format(host_text, file_location))
    return

def create_config(cluster_shell, file_location='~/.ssh/config'):
    config = "Host *\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null" \
             "\n\tLogLevel=ERROR\n\tServerAliveInterval=30\nUser ubuntu"
    cluster_shell.bash("echo \"{}\" >> {}".format(config, file_location))
    return

def create_ssh_key(cluster_shell, key_name='id_rsa', file_location='~/.ssh'):
    keyfile = os.path.join(file_location, key_name)
    pub_file = os.path.join(file_location, key_name + ".pub")
    local_key = os.path.join(os.getcwd(), key_name)
    local_pub = os.path.join(os.getcwd(), key_name + ".pub")
    cluster_shell.master_bash("ssh-keygen -f {} -q -N \"\"".format(keyfile))
    cluster_shell.scp_master_to_local(keyfile)
    cluster_shell.scp_master_to_local(pub_file)
    cluster_shell.scp_local_to_workers(local_key, keyfile)
    cluster_shell.scp_local_to_workers(local_pub, pub_file)
    Path(local_key).unlink()
    Path(local_pub).unlink()
    cluster_shell.bash("echo `cat {0}/{1}.pub` >> {0}/authorized_keys".format(file_location, key_name))

def create_instance_keys(cluster_shell):
    create_config(cluster_shell)
    create_ssh_key(cluster_shell)

def create_container_keys(cluster_shell):
    cluster_shell.bash('mkdir ssh_container')
    create_config(cluster_shell, file_location='~/ssh_container/config')
    cluster_shell.bash("sudo chown root:root {}".format('~/ssh_container/config'))
    create_ssh_key(cluster_shell, file_location="~/ssh_container")

def create_container_communicator(cluster_shell, container_name='mpicont'):
    cluster_shell.bash("touch ~/.ssh/{}.sh".format(container_name))
    com_script = "#!/bin/bash\necho \"entering container\"\n\n" \
                 "docker exec {} /bin/bash -c \\\"\$SSH_ORIGINAL_COMMAND\\\"".format(container_name)
    cluster_shell.bash("echo \"{0}\" >> ~/.ssh/{1}.sh".format(com_script, container_name))
    cluster_shell.bash("chmod +x /home/ubuntu/.ssh/{}.sh".format(container_name))
    key_command = "command=\\\"bash $HOME/.ssh/{}.sh\\\"" \
                  ",no-port-forwarding,no-agent-forwarding" \
                  ",no-X11-forwarding {}".format(container_name,
                   cluster_shell.master_bash('cat /home/ubuntu/ssh_container/id_rsa.pub')[0][0])
    cluster_shell.bash("echo \"{0}\" >> ~/.ssh/authorized_keys".format(key_command))

def connect_nodes(cluster_shell, container_name='mpicont', gpu_count=8):
    create_hostfiles(cluster_shell, gpus=gpu_count)
    create_instance_keys(cluster_shell)
    create_container_keys(cluster_shell)
    create_container_communicator(cluster_shell, container_name)


