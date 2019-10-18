import boto3
import paramiko
import multiprocessing
import asyncio

class Cluster_Shell:
  def __init__(self, cluster, user_name = 'ec2-user'):
    self.cluster = cluster
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
                     key_filename=self.cluster.pemfile)
    stdin, stdout, stderr = ssh.exec_command(command)
    ssh.close()
    return stdin, stdout, stderr

  def master_bash(self, command):
  	return self.node_bash(self.master_public_ip, command)

  def worker_bash(self, command):
  	"""
		asynchronous execution of command on all worker nodes
  	"""
  	async def async_node_bash(hostname, command):
  		return self.node_bash(hostname, command)
  	tasks = {worker:  asyncio.ensure_future(async_node_bash(worker, command)) \
  						 for worker in self.workers_public_ip}
  	await asyncio.wait(tasks)
  	result = {worker: task.result() for worker, task in tasks.items()}
  	return result




