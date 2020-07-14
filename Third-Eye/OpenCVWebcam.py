import cv2
import boto3
from PIL import Image
import io
from datetime import datetime
from multiprocessing import Process
import DeleteFaceID
from AlertBox import AlertBox
import ctypes
import time

ALERT = AlertBox()
USER32 = ctypes.windll.user32

TURN = 'Yaw'
UP_DOWN = 'Pitch'
TILT = 'Roll'
COLLECTION_ID = 'Third_Eye_References'
BUCKET = "third-eye-reference-bucket"


def show_webcam(mirror=False):
    rekognition = boto3.client('rekognition')
    cam = cv2.VideoCapture(0)
    frames = 0
    locked = False
    try:
        while True:
            # if bad_face or frames == 30:
            #     break
            ret_val, img = cam.read()
            if mirror:
                img = cv2.flip(img, 1)
            # encode image to memory buffer
            # save output buffer as string
            image_string = cv2.imencode('.jpg', img)[1].tostring()
            response = rekognition.index_faces(
                Image={
                    'Bytes':image_string
                },
                CollectionId=COLLECTION_ID,
                QualityFilter='LOW'
            )
            # process = Process(target=RekognitionClient.search, args=(response, ALERT), daemon=True)
            # process.start()
            # iterate through each face indexed and compare to verified
            # reference images in collection
            faces = []
            bad_face = False
            user_face = False
            if len(response['FaceRecords']) == 0 and not ALERT.isHidden:
                notify(False)
                continue
            for record in response['FaceRecords']:
                face_id = record['Face']['FaceId']
                faces.append(face_id)
                face_pose = record['FaceDetail']['Pose']
                if abs(face_pose[TURN]) >= 50.0 or abs(face_pose[UP_DOWN]) >= 40:
                    continue
                try:
                    search = rekognition.search_faces(
                        CollectionId=COLLECTION_ID,
                        FaceId=face_id,
                        MaxFaces=1,
                        FaceMatchThreshold=99.0
                    )
                    if len(search['FaceMatches']) == 0:
                        bad_face = True
                        # notify(True)
                    else:
                        user_face = True
                except rekognition.exceptions.InvalidParameterException:
                    print(f'faceID: {face_id}')
                    print('In Faces' if face_id in faces else 'Not in Faces')

                # upload frame if no matches were found, delete from collection
                # if len(search['FaceMatches']) == 0:
                #     # upload_to_s3(image_string)
                #     bad_face = True
                #     notify(True)
                # else:
                #     user_face = True
            if bad_face:
                print('bad face')
                if user_face:
                    notify(True)
                else:
                    notify(False)
                    locked = True
                    print('locked')
                    USER32.LockWorkStation()
                    time.sleep(3)
                    lock_wait(locked)
            else:
                if not ALERT.isHidden:
                    notify(False)
            if len(faces) > 0:
                rekognition.delete_faces(CollectionId=COLLECTION_ID, FaceIds=faces)
            # frames += 1
    except KeyboardInterrupt:
        print('exiting...')
        DeleteFaceID.delete_faces_in_collection(COLLECTION_ID)
        pass
    ALERT.window.close()
    cam.release()
    cv2.destroyAllWindows()
    return


def lock_wait(locked):
    print('in wait ' + datetime.now().time().strftime("%H:%M:%S"))
    while locked:
        if USER32.GetForegroundWindow() % 10 != 0:
            locked = False
            print('lock = false')
    print('in unlocked ' + datetime.now().time().strftime("%H:%M:%S"))
    return


def notify(value):
    if value:
        if ALERT.isHidden:
            ALERT.activate()
    else:
        if not ALERT.isHidden:
            ALERT.deactivate()
    return


def crop(img, box):
    img_width, img_height = img.size
    left = img_width * box['Left']
    top = img_height * box['Top']
    width = img_width * box['Width']
    height = img_height * box['Height']
    return img.crop((left, top, left+width, top+height))


def upload_to_s3(photo):
    s3_client = boto3.client('s3')
    bucket = BUCKET
    key = datetime.now().strftime("%b-%d-%Y_%H:%M:%S") + '.jpg'
    s3_client.put_object(ACL='public-read', Bucket=bucket, Key=key, Body=photo, ContentType='image/jpeg')


def main():
    show_webcam(mirror=True)


if __name__ == '__main__':
    main()
