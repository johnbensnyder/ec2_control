import boto3

class EC2_Cluster:
	subnets = {'us-east-1a': 'subnet-d7b30f9d',
								'us-east-1b': 'subnet-58b35b04',
								'us-east-1c': 'subnet-b440b9d3',
								'us-east-1d': 'subnet-2ef71d00',
								'us-east-1e': 'subnet-7e9b9341',
								'us-east-1f': 'subnet-21ac2f2e'}

	def __init__(self, name, image_id, node_count, keypair, pemfile, security_groups, 
		zone='us-east-1c', instance_type='p3dn.24xlarge', min_nodes=None, efa=True):
		self.keypair=keypair
		self.name=name
		self.image_id=image_id
		self.node_count=node_count
		self.min_nodes=node_count
		self.pemfile=pemfile
		self.zone=zone
		self.subnet=self.subnets[self.zone]
		self.instance_type=instance_type
		self.efa=efa
		if min_nodes:
			self.min_nodes=min_nodes
		self.security_groups = security_groups
		self.args = self.create_config()
		self.instances = None
		self.ec2_session = boto3.Session().resource('ec2')
		self.ec2_client=boto3.client('ec2')


	def create_config(self):
		args = {'ImageId': self.image_id,
		'InstanceType': self.instance_type,
		'MinCount': self.min_nodes,
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
				args['NetworkInterfaces'] = [{'SubnetId': self.subnet,
								'DeviceIndex': 0,
								'DeleteOnTermination': True,
								'InterfaceType':'efa',
								'Groups': self.security_groups}]
		return args

	def create_cluster(self):
		self.instances = self.ec2_session.create_instances(**self.args)
		return

	@property
	def instance_ids(self):
		return [i.id for i in self.instances]

	@property
	def public_ips(self):
		instance_info = self.ec2_client.describe_instances(InstanceIds=self.instance_ids)
		return [info['PublicIpAddress'] for info in instance_info['Reservations'][0]['Instances']]

	@property
	def private_ips(self):
		instance_info = self.ec2_client.describe_instances(InstanceIds=self.instance_ids)
		return [info['PrivateIpAddress'] for info in instance_info['Reservations'][0]['Instances']]
	


