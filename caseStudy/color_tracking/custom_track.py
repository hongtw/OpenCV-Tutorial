# USAGE
# python track.py --video video/iphonecase.mov

# import the necessary packages
import numpy as np
import argparse
import time
import cv2

def record(event, x, y, flags, param):
    click_times = param['click_times']
    img = param['image']
    pts = param['pts']
    if click_times < 4:
        if event == cv2.EVENT_LBUTTONDBLCLK or event == cv2.EVENT_LBUTTONDOWN:
            param['click_times'] += 1
            cv2.circle(img, (x, y), 3,(0, 255, 0), -1 )
            pts.append([x, y])

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help = "path to the (optional) video file")
args = vars(ap.parse_args())

# define the upper and lower boundaries for a color
# to be considered "blue"
# blueLower = np.array([100, 67, 0], dtype = "uint8")
# blueUpper = np.array([255, 128, 50], dtype = "uint8")
blueLower = None
blueUpper = None

# load the video
camera = cv2.VideoCapture(args["video"])



# keep looping
while True:
	# grab the current frame
	(grabbed, frame) = camera.read()

	# check to see if we have reached the end of the video
	if not grabbed:
		break

	if cv2.waitKey(1) & 0xFF == ord("s"):
		image = frame.copy()
		param = {'image':image, 'click_times':0, "pts":[]}
		cv2.namedWindow('Choosing')
		cv2.setMouseCallback('Choosing', record, param)
		while True:
			cv2.imshow('Choosing', image)
			k=cv2.waitKey(1)
			if k==ord('q'):    
				break
			elif len(param['pts']) == 4:
				try:
					pts = np.array(param['pts'])
					cv2.drawContours(image, [pts], -1, (0, 255, 0), -1)
					# image[image != [0 ,255, 0]] = [0,0,0]
					image = cv2.inRange(
						image, 
						np.array([0, 255, 0], dtype = "uint8"), 
						np.array([0, 255, 0], dtype = "uint8"))
					break
				except Exception as err:
					print("ERROR", err)
		new_frame = frame.copy()			
		phone = cv2.bitwise_and(new_frame, new_frame, mask=image)
		b, g, r = cv2.split(phone)
		b = b[b>0]
		g = g[g>0]
		r = r[r>0]
		b_range = (max(0, b.mean() - b.std()), np.max(b))
		g_range = (max(0, g.mean() - g.std()), np.max(g))
		r_range = (max(0, r.mean() - r.std()), np.max(r))
		print(f'b_range:{b_range}, g_range:{g_range}, r_range:{r_range}')
		blueLower,  blueUpper = list(zip(b_range, g_range, r_range))
		blueLower = np.array(blueLower, dtype='uint8')
		blueUpper = np.array(blueUpper, dtype='uint8')
		print(f"blueLower:{blueLower}, blueUpper:{blueUpper}")
		cv2.imshow('Choosing', phone)

	# determine which pixels fall within the blue boundaries
	# and then blur the binary image
	if np.any(blueLower) and np.any(blueUpper):
		blue = cv2.inRange(frame, blueLower, blueUpper)
		blue = cv2.GaussianBlur(blue, (3, 3), 0)

		# find contours in the image
		(_, cnts, _) = cv2.findContours(blue.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)

		# check to see if any contours were found
		if len(cnts) > 0:
			# sort the contours and find the largest one -- we
			# will assume this contour correspondes to the area
			# of my phone
			cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]

			# compute the (rotated) bounding box around then
			# contour and then draw it		
			rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
			'''
			- box = cv2.minAreaRect(cnt) -> 得到最小外接矩形的 (center(x,y), (w,h), angle)
			- cv2.boxPoints(box)  -> 得到四個頂點
			'''
			cv2.drawContours(frame, [rect], -1, (0, 255, 0), 2)

			cv2.imshow("Binary", blue)
	# show the frame and the binary image
	cv2.imshow("Tracking", frame)

	# if your machine is fast, it may display the frames in
	# what appears to be 'fast forward' since more than 32
	# frames per second are being displayed -- a simple hack
	# is just to sleep for a tiny bit in between frames;
	# however, if your computer is slow, you probably want to
	# comment out this line
	time.sleep(0.025)

	# if the 'q' key is pressed, stop the loop
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()