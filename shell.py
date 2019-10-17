import boto3
import paramiko

class Cluster_Shell:
  def __init__(self, cluster, user_name = 'ec2-user'):
    self.cluster = cluster
    self.ssh = self.create_connection()
    self.user_name = user_name
  
  def create_connection(self):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return ssh

  def node_bash(self, hostname, command):
    self.ssh.connect(hostname=hostname, username=self.user_name,
                     key_filename="/Users/jbsnyder/.aws/jbsnyder.pem")
    stdin, stdout, stderr = self.ssh.exec_command(command)
    self.ssh.close()
    for line in stdout.read().splitlines():
      print(line)
    return stdin, stdout, stderr
