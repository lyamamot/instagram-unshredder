#!/usr/bin/env python
from PIL import Image
import math

image = Image.open('TokyoPanoramaShredded.png')
data = image.getdata()
# print image.getpixel((20, 30))

# Width of image band in pixels.
BAND_WIDTH = 32
width, height = image.size

# Returns the pixel data for the given coordinates.
def get_pixel(x, y):
	return data[y * width + x]

# Calculates the distance between the two pixel values.
def get_distance(x1, y1, x2, y2):
	if 0 <= x1 < width and 0 <= x2 < width and 0 <= y1 < height and 0 <= y2 < height:
		pixel1 = get_pixel(x1, y1)
		pixel2 = get_pixel(x2, y2)

		return pow(pow(pixel2[0] - pixel1[0], 2) + pow(pixel2[1] - pixel2[1], 2) + pow(pixel2[2] - pixel1[2], 2), 0.5)
	return None

# Calculate two matrices of distances between band edges from left to right and right to left.
# distance[i, j] = distance between right edge of i and left edge of j if i < j
# We can calculate right to left edges in the same function but less work to just zip later.
def get_distances():
	numBands = width / BAND_WIDTH
	l2rDistance = [[0 for col in range(numBands)] for row in range(numBands)]
	r2lDistance = [[0 for col in range(numBands)] for row in range(numBands)]
	for i in range(len(l2rDistance)):
		for j in range(len(l2rDistance)):
			if i == j:
				continue

			leftJ = (i + 1) * BAND_WIDTH - 1 # left column of band j
			rightI = j * BAND_WIDTH # right column of band i

			distanceSum = 0
			for y in range(height):
				d = get_distance(leftJ, y, rightI, y)

				if d == None:
					distanceSum = None
					break	

				distanceSum += d

			l2rDistance[i][j] = distanceSum
			r2lDistance[j][i] = distanceSum

#		print '{0:2} {1:2} {2}'.format(i + 1, j + 1, distanceSum)
	return (l2rDistance, r2lDistance)

# Returns a map of band indices to the index of the next band, from left to right and from right to left.
def get_sequences():
	l2rDistance, r2lDistance = get_distances()

	l2rSequence, r2lSequence = [], []

	for i, v in enumerate(l2rDistance):
		val = min(x for x in v if x > 0)
		l2rSequence.append((v.index(val), val))

	for i, v in enumerate(r2lDistance):
		val = min(x for x in v if x > 0)
		r2lSequence.append((v.index(val), val))

	return (l2rSequence, r2lSequence)

# Compare edges to find any duplicates and to determine which band is the first.
# For every band, get its left band. For that band, get its right band. These are not necessarily the same.
# If they are the same, assume it is a good match. Otherwise, the match with the shortest distance is the true
# match and the other band is the start.
def get_start_band(l2rSequence, r2lSequence):
	startBand = None
	for i, v in enumerate(r2lSequence):
		# Value and index of band to the left of i.
		leftMatch = v[0] 
		leftValue = v[1]

		# Value and index of band to the right of leftMatch.
		rightMatch = l2rSequence[leftMatch][0]
		rightValue = l2rSequence[leftMatch][1]

#print '{0:2} [{1:2}] {2:2}'.format(leftMatch + 1, i + 1, l2rSequence[i][0] + 1)

		if leftValue < rightValue:
			startBand = rightMatch

		elif rightValue < leftValue:
			startBand = i

	return startBand

# Compare right matches to left matches and eliminate mismatches to find the bands that belong on the end.
l2rSequence, r2lSequence = get_sequences()
startBand = get_start_band(l2rSequence, r2lSequence)
#print '{0} is the start'.format(startBand + 1)

# Create a new image of the same size as the original
# and copy a region into the new image
unshredded = Image.new("RGBA", image.size)

band_number = startBand
for i in range(width / BAND_WIDTH):
	x1, y1 = BAND_WIDTH * band_number, 0
	x2, y2 = x1 + BAND_WIDTH, height

	source_region = image.crop((x1, y1, x2, y2))
	destination_point = (i * BAND_WIDTH, 0)
	unshredded.paste(source_region, destination_point)
	
	band_number = l2rSequence[band_number][0]

# Output the new image.
unshredded.save("unshredded.png", "PNG")

