#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Point
from sensor_msgs.msg import PointCloud
import std_msgs.msg
import math

# switch to change the mode. True is by cycle, False is by time.
split_by_cycle = True

if __name__ == '__main__':
	rospy.init_node('pub_pcl')
	cloud_pub = rospy.Publisher(
		'pcl_output',
		PointCloud,
		queue_size=1
	)

	#rate = rospy.Rate(10)
	rate = rospy.Rate(15)

	data = []
	# grep '\ 1793\ \|\ 1794\ ' canbus.txt > 7012
	#with open('/home/ohy/workspace/conti/test', 'r') as fp:
	with open('/home/ohy/workspace/conti/7012', 'r') as fp:
		for line in fp:
			# 1st is 0x702 and 2nd is 0x701
			# assume the first timestamp and target number is same to the second one

			#line = fp.next()
			tmp = str.split(line)
			angle = math.radians(float(tmp[len(tmp)-2]))
			line = fp.next()
			tmp = str.split(line)
			dist = float(tmp[len(tmp) -1])
			z = 1
			if split_by_cycle:
				data.append([tmp[0], int(tmp[2]), dist*math.cos(angle), dist*math.sin(angle), z])
			else:
				# timestamp overflow ?
				data.append([int(tmp[0][0:9]), int(tmp[2]), dist*math.cos(angle), dist*math.sin(angle), z])
	fp.close()

	idx = 0
	counter = 1
	if split_by_cycle:
		pre = data[idx][1]
	else:
		pre = data[idx][0]
		#d = 30	# s
		d = 70	# s
	n = len(data) - 1
	while not rospy.is_shutdown():
		if idx == n:
			break
		idx_pre = idx
		if idx != 0:
			idx = idx + 1
			if split_by_cycle:
				pre = data[idx][1]
			else:
				pre = data[idx][0]

		if split_by_cycle:
			while idx < n and pre < data[idx+1][1]:
				idx = idx + 1
				pre = data[idx][1]
		else:
			while idx < n and data[idx+1][0] < (pre + d) :
				idx = idx + 1
		#print "idx", idx, "idx_pre", idx_pre, "num:", idx - idx_pre
		print "counter:", counter
		counter += 1
		#print data[idx]
		#print pre

		output = PointCloud()
		output.header = std_msgs.msg.Header()
		output.header.stamp = rospy.Time.now()
		output.header.frame_id = "odom"

		number_of_frame = idx - idx_pre
		# create an empty list of correct size
		output.points = [None] * number_of_frame

		# fill up pointcloud with points
		for i in xrange(0, number_of_frame):
			output.points[i] = Point(data[i+idx_pre][2], data[i+idx_pre][3], data[i+idx_pre][4])
			#print output.points[i]
			#print data[i+idx_pre][2], data[i+idx_pre][3], data[i+idx_pre][4]

		# now publish the pointcloud
		cloud_pub.publish(output)
		rate.sleep()

	rospy.spin()
