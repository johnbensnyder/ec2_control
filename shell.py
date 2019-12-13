import paramiko
from scp import SCPClient
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

  def create_scp_client(self, hostname):
    ssh = self.create_connection()
    ssh.connect(hostname=hostname, username=self.user_name,
                key_filename=self.cluster.KeyFile)
    return SCPClient(ssh.get_transport())

  def node_scp_put(self, hostname, src, dest, recursive=False):
    scp = self.create_scp_client(hostname)
    return scp.put(src, remote_path=dest, recursive=recursive)

  def node_scp_get(self, hostname, src, dest="", recursive=False):
    scp = self.create_scp_client(hostname)
    return scp.get(src, dest, recursive)

  def scp_local_to_master(self, src, dest, recursive=False, wait=True):
    task = self.thread_pool.submit(self.node_scp_put, self.master_public_ip, src, dest, recursive)
    if wait:
      while not task.done():
        continue
      return task.result()
    return task

  def scp_master_to_local(self, src, dest="", recursive=False, wait=True):
    task = self.thread_pool.submit(self.node_scp_get, self.master_public_ip, src, dest, recursive)
    if wait:
      while not task.done():
        continue
      return task.result()
    return task

  def scp_local_to_workers(self, src, dest, recursive=False, wait=True):
    tasks = [self.thread_pool.submit(self.node_scp_put, i, src, dest, recursive) for i in self.workers_public_ip]
    if wait:
      while not all([i.done() for i in tasks]):
        continue
      return [i.result() for i in tasks]
    return tasks

  def scp_workers_to_local(self, src, dest, recursive=False, wait=True):
    tasks = [self.thread_pool.submit(self.node_scp_get, i, src, dest+str(j), recursive) for j, i in enumerate(self.workers_public_ip)]
    if wait:
      while not all([i.done() for i in tasks]):
        continue
      return [i.result() for i in tasks]
    return tasks

  def master_bash(self, command, wait=True):
    task = self.thread_pool.submit(self.node_bash, self.master_public_ip, command)
    if wait:
      while not task.done():
        continue
      return task.result()
    return task

  def worker_bash(self, command, wait=True):
    """
    asynchronous execution of command on all worker nodes
    """
    tasks = [self.thread_pool.submit(self.node_bash, worker, command) \
               for worker in self.workers_public_ip]
    if wait:
      while not all([i.done() for i in tasks]):
        continue
      return [i.result() for i in tasks]
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
    tasks = [self.thread_pool.submit(self.node_bash, node, command) \
             for node in self.cluster.public_ips]
    if wait:
      while not all([i.done() for i in tasks]):
        continue
      return [i.result() for i in tasks]
    return tasks





