#!/usr/bin/env python
from PIL import Image
import math

class Unshredder(object):
	def __init__(self, imageFile):
		self.image = Image.open(imageFile)
		self.width, self.height = self.image.size
		self.data = self.image.getdata()

		# Width of image band in pixels.
		self.NUM_BANDS = 20
		self.BAND_WIDTH = self.width / self.NUM_BANDS

	def get_pixel(self, x, y):
		"""Returns the pixel data for the given coordinates."""
		return self.data[y * self.width + x]

	def get_distance(self, x1, y1, x2, y2):
		"""Calculates the distance between the two pixel values as a measure of how similar they are."""
		if 0 <= x1 < self.width and 0 <= x2 < self.width and 0 <= y1 < self.height and 0 <= y2 < self.height:
			pixel1 = self.get_pixel(x1, y1)
			pixel2 = self.get_pixel(x2, y2)

			return pow(pow(pixel2[0] - pixel1[0], 2) + pow(pixel2[1] - pixel2[1], 2) + pow(pixel2[2] - pixel1[2], 2), 0.5)

		# Pixel is out of bounds.
		return None

	def get_band_distance(self, i, j):
		"""Returns the sum of distances between the rightmost column of pixels in band i and lefmost column of pixels in band j."""
		if i == j:
			return 0

		leftJ = (i + 1) * self.BAND_WIDTH - 1 # left column of band j
		rightI = j * self.BAND_WIDTH # right column of band i

		distanceSum = 0
		for y in range(self.height):
			d = self.get_distance(leftJ, y, rightI, y)

			if d == None:
				distanceSum = None
				break	

			distanceSum += d

		return distanceSum


	def get_distances(self):
		"""
		Calculate a matrix of sums of distances between band edges.
		distance[i, j] = distance between right edge of i and left edge of j if i < j.
		"""
		distance = [[self.get_band_distance(row, col) for col in range(self.NUM_BANDS)] for row in range(self.NUM_BANDS)]

		return distance

	def get_sequence(self, distance):
		sequence = []
		for i, v in enumerate(distance):
			val = min(x for x in v if x > 0)
			sequence.append((v.index(val), val))
		return sequence

	def get_sequences(self):
		"""Returns a map of band indices to the index of the next band, from left to right and from right to left."""
		distance = self.get_distances()

		return (self.get_sequence(distance), self.get_sequence(zip(*distance)))

	def get_start_band(self, l2rSequence, r2lSequence):
		"""
		Compare edges to find any duplicates and to determine which band is the first.
		For every band, get its left band. For that band, get its right band. These are not necessarily the same.
		If they are the same, assume it is a good match. Otherwise, the match with the shortest distance is the true
		match and the other band is the start.
		"""
		startBand = None
		for i, v in enumerate(r2lSequence):
			# Value and index of band to the left of i.
			leftMatch = v[0] 
			leftValue = v[1]

			# Value and index of band to the right of leftMatch.
			rightMatch = l2rSequence[leftMatch][0]
			rightValue = l2rSequence[leftMatch][1]

#	print '{0:2} [{1:2}] {2:2}'.format(leftMatch + 1, i + 1, l2rSequence[i][0] + 1)

			if leftValue < rightValue:
				startBand = rightMatch

			elif rightValue < leftValue:
				startBand = i

		return startBand

	def unshred(self):
		# Compare right matches to left matches and eliminate mismatches to find the bands that belong on the end.
		l2rSequence, r2lSequence = self.get_sequences()
		startBand = self.get_start_band(l2rSequence, r2lSequence)
		#print '{0} is the start'.format(startBand + 1)

		# Save the unshredded image according to the calculated sequence.
		unshredded = Image.new("RGBA", self.image.size)

		band_number = startBand
		for i in range(self.width / self.BAND_WIDTH):
			x1, y1 = self.BAND_WIDTH * band_number, 0
			x2, y2 = x1 + self.BAND_WIDTH, self.height

			source_region = self.image.crop((x1, y1, x2, y2))
			destination_point = (i * self.BAND_WIDTH, 0)
			unshredded.paste(source_region, destination_point)
			
			band_number = l2rSequence[band_number][0]

		# Output the new image.
		unshredded.save("deshredded.png", "PNG")


if __name__ == '__main__':
	import sys
	if len(sys.argv) == 1:
		print 'Usage: unshredder.py <filename>'
		sys.exit()

	unshredder = Unshredder(sys.argv[1])
	unshredder.unshred()
