#!/usr/bin/python
'''
    Derived from https://github.com/gdiepen/face-recognition
'''

#Import the OpenCV and dlib libraries
import cv2
import dlib


#Initialize a face cascade using the frontal face haar cascade provided with
#the OpenCV library
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#The deisred output width and height
OUTPUT_SIZE_WIDTH = 1280
OUTPUT_SIZE_HEIGHT = 720

def detectAndTrackLargestFace():
    #Open the first webcame device
    capture = cv2.VideoCapture(0)

    #Create two opencv named windows
    cv2.namedWindow("GORTI, BAE, WALL CAPSTONE", cv2.WINDOW_AUTOSIZE)

    #Position the windows next to eachother
    cv2.moveWindow("GORTI, BAE, WALL CAPSTONE",400,100)

    #Start the window thread for the two windows we are using
    cv2.startWindowThread()

    #Create the tracker we will use
    tracker = dlib.correlation_tracker()

    #The variable we use to keep track of the fact whether we are
    #currently using the dlib tracker
    trackingFace = 0

    #The color of the rectangle we draw around the face
    rectangleColor = (0,0,255)


    try:
        while True:
            #Retrieve the latest image from the webcam
            rc,fullSizeBaseImage = capture.read()

            #Resize the image to 320x240
            baseImage = cv2.resize( fullSizeBaseImage, ( 1280, 720))


            #Check if a key was pressed and if it was Q, then destroy all
            #opencv windows and exit the application
            pressedKey = cv2.waitKey(2)
            if pressedKey == ord('Q'):
                cv2.destroyAllWindows()
                exit(0)



            #Result image is the image we will show the user, which is a
            #combination of the original image from the webcam and the
            #overlayed rectangle for the largest face
            resultImage = baseImage.copy()






            #If we are not tracking a face, then try to detect one
            if not trackingFace:

                #For the face detection, we need to make use of a gray
                #colored image so we will convert the baseImage to a
                #gray-based image
                gray = cv2.cvtColor(baseImage, cv2.COLOR_BGR2GRAY)
                #Now use the haar cascade detector to find all faces
                #in the image
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)

                #In the console we can show that only now we are
                #using the detector for a face
                #print("Using the cascade detector to detect face")


                #For now, we are only interested in the 'largest'
                #face, and we determine this based on the largest
                #area of the found rectangle. First initialize the
                #required variables to 0
                maxArea = 0
                x = 0
                y = 0
                w = 0
                h = 0


                #Loop over all faces and check if the area for this
                #face is the largest so far
                #We need to convert it to int here because of the
                #requirement of the dlib tracker. If we omit the cast to
                #int here, you will get cast errors since the detector
                #returns numpy.int32 and the tracker requires an int
                for (_x,_y,_w,_h) in faces:
                    if  _w*_h > maxArea:
                        x = int(_x)
                        y = int(_y)
                        w = int(_w)
                        h = int(_h)
                        maxArea = w*h

                #If one or more faces are found, initialize the tracker
                #on the largest face in the picture
                if maxArea > 0 :

                    #Initialize the tracker
                    tracker.start_track(baseImage,
                                        dlib.rectangle( x-10,
                                                        y-20,
                                                        x+w+10,
                                                        y+h+20))

                    #Set the indicator variable such that we know the
                    #tracker is tracking a region in the image
                    trackingFace = 1

            #Check if the tracker is actively tracking a region in the image
            if trackingFace:

                #Update the tracker and request information about the
                #quality of the tracking update
                trackingQuality = tracker.update( baseImage )



                #If the tracking quality is good enough, determine the
                #updated position of the tracked region and draw the
                #rectangle
                if trackingQuality >= 8.75:
                    tracked_position =  tracker.get_position()

                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())
                    cv2.rectangle(resultImage, (t_x, t_y),
                                                (t_x + t_w , t_y + t_h),
                                                rectangleColor ,2)
                    drone_directions = getDroneDir(t_x,t_y,t_w,t_h)
                    

                    avgx = (t_x+t_x+t_w)/2
                    avgy = (t_y+t_y+t_h)/2
                    #print("tx {0} ty {1} w {2} h {3} avgx {4} avgy {5}".format(t_x,t_y,t_w,t_h,avgx,avgy))
                    cv2.circle(resultImage, (int(avgx),int(avgy)), 5, (255,0,0), thickness=1, lineType=8, shift=0)


                    for i in range(0,len(drone_directions)):
                        if("good" in drone_directions[i]):
                            color = (0,255,0)
                        else:
                            color = (0,0,255)
                        cv2.putText(resultImage,drone_directions[i], (t_x+t_w + 10,t_y+30+30*i), cv2.FONT_HERSHEY_SIMPLEX, 1, color,2)


                else:
                    #If the quality of the tracking update is not
                    #sufficient (e.g. the tracked region moved out of the
                    #screen) we stop the tracking of the face and in the
                    #next loop we will find the largest face in the image
                    #again
                    trackingFace = 0





            #Since we want to show something larger on the screen than the
            #original 320x240, we resize the image again
            #
            #Note that it would also be possible to keep the large version
            #of the baseimage and make the result image a copy of this large
            #base image and use the scaling factor to draw the rectangle
            #at the right coordinates.
            largeResult = cv2.resize(resultImage,
                                     (OUTPUT_SIZE_WIDTH,OUTPUT_SIZE_HEIGHT))

            #Finally, we want to show the images on the screen
            cv2.imshow("GORTI, BAE, WALL CAPSTONE", largeResult)




    #To ensure we can also deal with the user pressing Ctrl-C in the console
    #we have to check for the KeyboardInterrupt exception and destroy
    #all opencv windows and exit the application
    except KeyboardInterrupt as e:
        cv2.destroyAllWindows()
        exit(0)

def getDroneDir(x,y,w,h):
    avgx = (x+x+w)/2
    avgy = (y+y+h)/2

    devx = (avgx/OUTPUT_SIZE_WIDTH)
    devy = (avgy/OUTPUT_SIZE_HEIGHT)

    #print(devx,devy)

    drone_set = []

    if(devx < 0.25):
        drone_set.append("drone far left, correct right")
    elif(devx < 0.40):
        drone_set.append("drone left, ease right")
    elif(devx > 0.75):
        drone_set.append("drone far right, correct left")
    elif(devx > 0.60):
        drone_set.append("drone right, ease left")
    else:
        drone_set.append("drone X good")

    if(devy < 0.25):
        drone_set.append("drone far above, correct down")
    elif(devy < 0.40):
        drone_set.append("drone above, ease down")
    elif(devy > 0.75):
        drone_set.append("drone far down, correct up")
    elif(devy > 0.60):
        drone_set.append("drone down, ease up")
    else:
        drone_set.append("drone Y good")

    return drone_set

    #print("X")
    #print(avgx/OUTPUT_SIZE_WIDTH)
    #X 0.1 - 0.5
    #print("Y")#Y 0.1 - 0.5
    #print(avgy/OUTPUT_SIZE_HEIGHT)
if __name__ == '__main__':
    detectAndTrackLargestFace()