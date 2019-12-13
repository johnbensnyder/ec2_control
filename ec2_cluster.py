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
    args = {'ImageId': self.ImageId,
    'InstanceType': self.InstanceType,
    'MinCount': self.MinCount if self.MinCount else self.MaxCount,
    'MaxCount': self.MaxCount,
    'KeyName': self.KeyName}

    # add name tag
    args['TagSpecifications'] = [{
        'ResourceType': 'instance',
        'Tags': [{
        'Key': 'Name',
        'Value': self.Name
        }]
      }]
    if 'BlockDeviceMappings' in self.__dict__:
      args['BlockDeviceMappings'] = self.BlockDeviceMappings
    if 'Efa' in self.__dict__:
      if self.Efa:
        assert self.InstanceType in ['p3dn.24xlarge', 'c5n.18xlarge', 'm5dn.24xlarge',
                                     'r5dn.24xlarge'], 'EFA not available on instance'
        args['NetworkInterfaces'] = [{'SubnetId': self.SubnetId,
                'DeviceIndex': 0,
                'DeleteOnTermination': True,
                'InterfaceType':'efa',
                'Groups': self.SecurityGroups}]
      else:
        args['SecurityGroupIds'] = self.SecurityGroups
    else:
      args['SecurityGroupIds'] = self.SecurityGroups

    return args

  def create_cluster(self):
    self.instances = self.ec2_session.create_instances(**self.args)
    return

  def start_cluster(self):
    self.ec2_client.start_instances(InstanceIds=self.instance_ids)

  def stop_cluster(self):
    self.ec2_client.stop_instances(InstanceIds=self.instance_ids)
    

  def terminate_cluster(self):
    self.ec2_client.terminate_instances(InstanceIds=self.instance_ids)

  @property
  def instance_info(self):
    return self.ec2_client.describe_instances(InstanceIds=self.instance_ids)
  
  @property
  def instance_ids(self):
    return [i.id for i in self.instances]

  @property
  def public_ips(self):
    instance_info = self.instance_info
    return [instance['PublicIpAddress'] for instance in [instance for sublist in [reservation['Instances'] \
             for reservation in self.instance_info['Reservations']] for instance in sublist]]

  @property
  def private_ips(self):
    instance_info = self.instance_info
    return [instance['PrivateIpAddress'] for instance in [instance for sublist in [reservation['Instances'] \
             for reservation in self.instance_info['Reservations']] for instance in sublist]]
  