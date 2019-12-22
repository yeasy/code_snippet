import datetime
import sys
import os

timestap_flag="========"
nic_name_flag= "mtu "


def main():
	"""
	main will parse the ifconfig file and store the data into
	ts=[1,2,3,...],

	nic_stat={
	'nic_name': {
		'RX packets': {'t1':xxx, ...},
		'RX bytes': {'t1':xxx, ...},
		'TX packets': {'t1':xxx, ...},
		'TX bytes': {'t1':xxx, ...},
		},
	...
	}
	"""
	filepath = sys.argv[1]

	if not os.path.isfile(filepath):
		print("File path {} does not exist. Exiting...".format(filepath))
		sys.exit()

	ts_list, nic_stat = [], {}

	with open(filepath) as f:
		cnt = 0
		for line in f:
			cnt += 1
			# print("{}:{}".format(cnt, line))
			line = line.lstrip(' ').rstrip(' ').strip('\n')
			if timestap_flag in line:  # Timestamp line
				ts = line[18:]  # TODO: we use fixed length here.
				# print("Timestamp={}\n".format(ts))
				ts = datetime.datetime.strptime(ts, '%a %b %d %H:%M:%S UTC %Y')
				ts = ts.strftime('%Y%m%d-%H:%M:%S')
				ts_list.append(ts)
			elif nic_name_flag in line:  # nic name line
				nic_name = line.split(":")[0]
				# print("Nic Name={}\n".format(nic_name))
				if nic_name not in nic_stat:
					nic_stat[nic_name] = {
						'RX-packets': {},
						'RX-bytes': {},
						'TX-packets': {},
						'TX-bytes': {}
					}
			elif line.startswith('RX packets') or line.startswith('TX packets'):
				prefix = line[:2]  # e.g., RX packets, or TX packets
				line_split = line[3:].split(' ')
				# print(line_split)
				pkts, bytes = line_split[1], line_split[4]  # No need int here
				nic_stat[nic_name][prefix+'-packets'][ts] = pkts
				nic_stat[nic_name][prefix+'-bytes'][ts] = bytes

	# print(nic_stat)
	nic_names = sorted(nic_stat.keys())
	metrics = ['RX-packets', 'RX-bytes', 'TX-packets', 'TX-bytes']
	labels, line = [], 'TimeStamp'
	for nic_name in nic_names:
		for metric in metrics:
			labels.append([nic_name, metric])
	for l in labels:
		line = '{} {}-{}'.format(line, l[0], l[1])
	print(line)  # TimeStamp eth0-RX-pkts ...
	for ts in ts_list:
		# ts nic_name+m  nic_name+m ...
		line = ts
		for l in labels:  # [eth0, Rx-pkts]
			values = nic_stat[l[0]][l[1]]
			if ts in values:
				value = values[ts]
			else:
				value = '0'  # sometimes, new created nic does not have complete ts
			line = line+' '+value
		print(line)
	return

	for nic_name in nic_stat:
		for k in nic_stat[nic_name]:  # RX packets/RX bytes/TX packets/TX bytes
			print(nic_name +' '+k)
			print(nic_stat[nic_name][k])


if __name__ == '__main__':
	main()