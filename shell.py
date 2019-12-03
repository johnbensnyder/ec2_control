import paramiko
from concurrent.futures import ThreadPoolExecutor

class Cluster_Shell(object):
  def __init__(self, cluster, user_name = 'ubuntu', async_threads=None):
    self.cluster = cluster
    self.thread_pool = ThreadPoolExecutor(max_workers=async_threads \
                                          if async_threads \
                                          else len(self.cluster.public_ips))
    self.ssh = self.create_connection()
    self.user_name = user_name
    self.master_public_ip = self.cluster.public_ips[0]
    self.workers_public_ip = self.cluster.public_ips[1:]
    self.master_private_ip = self.cluster.private_ips[0]
    self.workers_private_ip = self.cluster.private_ips[1:]
  
  def create_connection(self):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return ssh

  def node_bash(self, hostname, command):
    ssh = self.create_connection()
    ssh.connect(hostname=hostname, username=self.user_name,
                     key_filename=self.cluster.KeyFile)
    results = ssh.exec_command(command)
    results = [i.readlines() for i in results[1:]]
    ssh.close()
    return results

  def master_bash(self, command):
    return self.node_bash(self.master_public_ip, command)

  def worker_bash(self, command, wait=True):
    """
    asynchronous execution of command on all worker nodes
    """
    tasks = {worker:  self.thread_pool.submit(self.node_bash, worker, command) \
               for worker in self.workers_public_ip}
    return tasks

  def bash(self, command, wait=True):
    """
    async execution on all nodes
    Parameters
    ----------
    command
    wait

    Returns
    -------

    """
    tasks = {node: self.thread_pool.submit(self.node_bash, node, command) \
             for node in self.cluster.public_ips}
    return tasks



