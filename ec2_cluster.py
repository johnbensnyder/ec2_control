import boto3
import yaml

class EC2_Cluster:

  def __init__(self, config=None, **kwargs):
    self.instances = None
    if config:
      with open(config) as infile:
        params = yaml.safe_load(infile)
      for i,j in params.items():
        kwargs[i]=j
    for param, value in kwargs.items():
      self.__dict__[param] = value
    self.args = self.create_config()
    self.ec2_session = boto3.Session().resource('ec2')
    self.ec2_client=boto3.client('ec2')

  def create_config(self):
    args = {'ImageId': self.image_id,
    'InstanceType': self.instance_type,
    'MinCount': self.min_nodes if self.min_nodes else self.node_count,
    'MaxCount': self.node_count,
    'KeyName': self.keypair}

    # add name tag
    args['TagSpecifications'] = [{
        'ResourceType': 'instance',
        'Tags': [{
        'Key': 'Name',
        'Value': self.name
        }]
      }]
    if self.efa:
      assert self.instance_type in ['p3dn.24xlarge', 'c5n.18xlarge', 'm5dn.24xlarge',
                                    'r5dn.24xlarge'] print('EFA not available on instance') 
      args['NetworkInterfaces'] = [{'SubnetId': self.subnet,
              'DeviceIndex': 0,
              'DeleteOnTermination': True,
              'InterfaceType':'efa',
              'Groups': self.security_groups}]
    return args

  def create_cluster(self):
    return self.instances = self.ec2_session.create_instances(**self.args)

  def start_cluster(self):
    return self.ec2_client.start_instances(InstanceIds=self.instance_ids)

  def stop_cluster(self):
    return self.ec2_client.stop_instances(InstanceIds=self.instance_ids)
    

  def terminate_cluster(self):
    return self.ec2_client.terminate_instances(InstanceIds=self.instance_ids)

  @property
  def instance_info(self):
    return self.ec2_client.describe_instances(InstanceIds=self.instance_ids)
  
  @property
  def instance_ids(self):
    return [i.id for i in self.instances]

  @property
  def public_ips(self):
    instance_info = self.instance_info
    return [info['PublicIpAddress'] for info in reservation['Instances'] \
                                    for reservation in instance_info['Reservations']]

  @property
  def private_ips(self):
    instance_info = self.instance_info
    return [info['PrivateIpAddress'] for info in reservation['Instances'] \
                                    for reservation in instance_info['Reservations']]
  