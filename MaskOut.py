

def getNextImage(x):
	global imageIDX
	global img

	img = listImg[x]


if __name__ == '__main__':
	#listMask = getListMask()
	getListImgFile(folder="")
	getListImg(folder="")

	cv2.namedWindow("chgiang@222")
	cv2.createTrackbar('idx','chgiang@222',0,len(listImg)-1,getNextImage)
	cv2.createTrackbar('rotate','chgiang@222',0,len(listImg)-1,getNextImage)

	while True:
		cv2.imshow("chgiang@222",img)
		

		k = cv2.waitKey(33)
		if k==27:    # Esc key to stop
			cv2.destroyAllWindows()
			break