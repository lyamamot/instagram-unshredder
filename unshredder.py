#!/usr/bin/env python
from PIL import Image
image = Image.open('TokyoPanoramaShredded.png')
data = image.getdata()
# print image.getpixel((20, 30))

# Width of image band in pixels.
BAND_WIDTH = 32
width, height = image.size

# Returns the pixel data for the given coordinates.
def get_pixel(x, y):
	return data[y * width + x]

# Calculate the hash value of a single pixel.
def get_hash(x, y):
	pixel = get_pixel(x, y)

	hash = 37 
	for p in range(3):
		hash = 17 * hash + pixel[p]
	return hash

# Iterate over the image bands and calculate edge hashes separately for left and right sides.
def get_band_hashes():
	numBands = range(width / BAND_WIDTH)
	leftHashes, rightHashes = {},{}
	for x in numBands:
		left = x * BAND_WIDTH
		right = (x + 1) * BAND_WIDTH - 1

		leftHash = 37
		rightHash = 37
		for y in range(height):
			leftHash = 17 * leftHash + get_hash(left, y)
			rightHash = 17 * rightHash + get_hash(right, y)

#leftHashes[x] = leftHash >> 1344
#		rightHashes[x] = rightHash >> 1344
		leftHashes[x] = leftHash
		rightHashes[x] = rightHash
		print '{0:3} {1:7} {2:7}'.format(x + 1, leftHash >> 1400, rightHash >> 1400)

	return (leftHashes, rightHashes)

# Iterate over the image bands and calculate edge hashes separately for left and right sides.
def get_band_sums():
	numBands = range(width / BAND_WIDTH)
	leftSums, rightSums = {}, {}
	for x in numBands:
		left = x * BAND_WIDTH
		right = (x + 1) * BAND_WIDTH - 1

		leftSum = 0
		rightSum = 0
		for y in range(height):
			leftSum += get_hash(left, y)
			rightSum += get_hash(right, y)

		leftSums[x] = leftSum
		rightSums[x] = rightSum

		print '{0:3} {1:7} {2:7}'.format(x + 1, leftSum, rightSum)

	return (leftSums, rightSums)

lefts, rights = get_band_hashes()

# Returns the number of the band that matches the given band on the left side.
def get_left_match(n):
	mindex = -1
	minval = None
	for k, v in rights.iteritems():
		if k == n:
			continue

		diff = abs(lefts[n] - v)
		if minval is None or minval > diff:
			minval = diff
			mindex = k

	if mindex == n:
		return None

	return mindex

# Returns the number of the band that matches the given band on the right side.
def get_right_match(n):
	mindex = -1
	minval = None
	for k, v in lefts.iteritems():
		if k == n:
			continue

		diff = abs(rights[n] - v)
		if minval is None or minval > diff:
			minval = diff
			mindex = k

	if mindex == n:
		return None

	return mindex

for i in range(width / BAND_WIDTH):
	left = get_left_match(i)
	right = get_right_match(i)

	print '{0:4} {1:3} {2:4}'.format(left + 1, i + 1, right + 1)
