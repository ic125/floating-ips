# floating-ips
Files required for floating IPs

Find KB article about installation and more here: https://kb.heficed.com/en/articles/3692410-heficed-floating-ip

For CentOS 8 use the following instructions:

1) Get your API Key
You MUST enable KronosCloud, IpSwitch and ProtoCompute even if you don't use KronosCloud or ProtoCompute instances

2) Enable the Repo for PCS / Pacemaker

dnf config-manager --set-enabled ha

3) Run Yum Update

yum update -y && yum upgrade -y

4) Install PCS

yum install pacemaker pcs

5) Enable Python2 and install requests module

dnf install python2
pip2 install requests

6) Set Password for hacluster account:

passwd hacluster

7) Enable Cluster Software on Boot and Start PCS Daemon

systemctl enable pcsd.service
systemctl start pcsd.service

8) Build the Cluster - Node1, Node2 etc being the IP addresses of your instances

pcs host auth node1 node2

9) Continue Building the Cluster - Clustername can be changed to a name of your choice. Node1, Node2 etc being the IP addresses of your instances

pcs cluster setup clustername node1 node2

10) Start the Clkuster on Primary Node:

pcs cluster start --all

11) Check Status

pcs status corosync

12) Enable Corosync and Pacemaker to start on Boot:

systemctl enable corosync.service
systemctl enable pacemaker.service

13) Disable Shoot the other node in the head

pcs property set stonith-enabled=false

14) Create some Directories

mkdir /usr/lib/ocf/resource.d/heficed

15) Place floatip script in the following location:

/usr/lib/ocf/resource.d/heficed

16) Make the script executable

chmod +x /usr/lib/ocf/resource.d/heficed/floatip

17) Register the script with PCS

pcs resource create FloatIP ocf:heficed:floatip

18) Test
pcs status
