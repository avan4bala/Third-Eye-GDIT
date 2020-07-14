import boto3
import csv
import os

# with open('accessKeys.csv', 'r') as input:
#     next(input)
#     reader = csv.reader(input)
#     for line in reader:
#         access_key_id = line[0]
#         secret_access_key = line[1]


BUCKET = "third-eye-reference-bucket"
COLLECTION = "Third_Eye_References"


def index_faces_keys(keys, attributes=()):
    rekognition = boto3.client("rekognition")
    s3 = boto3.resource('s3')
    obj = s3.Object(BUCKET, 'IDs/faceIDs.txt')
    # idFile = open('C:\\Users\\alexm\\Documents\\DevSecOps\\faceIDs.txt', 'a+')
    idFile = obj.get()['Body'].read()
    tokens = True
    external_id = os.getlogin()
    for key in keys:
        response = rekognition.index_faces(
            Image={
             "S3Object": {
                "Bucket": BUCKET,
                "Name": key,
             }
            },
            CollectionId=COLLECTION,
            ExternalImageId=external_id,
            DetectionAttributes=attributes,
            MaxFaces=1,
            QualityFilter='LOW'
        )
    response = rekognition.list_faces(CollectionId=COLLECTION, MaxResults=1)
    while tokens:
        for face in response['Faces']:
            if face['ExternalImageId'] == external_id:
                faceId = face['FaceId']
                # idFile.write(faceId + '\n')
                idFile += str.encode(faceId) + b'\r\n'
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response = rekognition.list_faces(CollectionId=COLLECTION, NextToken=nextToken, MaxResults=1)
        else:
            tokens = False
    obj.put(ACL='public-read', Body=idFile)
    return


def index_faces_bucket(bucket, collection_id, attributes=()):
    rekognition = boto3.client("rekognition")
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(bucket)
    obj_file = s3.Object(BUCKET, 'IDs/faceIDs.txt')
    idFile = str.encode('')
    tokens = True
    external_id = os.getlogin()
    ignore = my_bucket.objects.filter(Prefix='IDs/')
    for obj in my_bucket.objects.all():
        if obj in ignore:
            continue
        key = obj.key
        response = rekognition.index_faces(
            Image={
             "S3Object": {
                "Bucket": bucket,
                "Name": key,
             }
            },
            CollectionId=collection_id,
            ExternalImageId=external_id,
            DetectionAttributes=attributes,
            MaxFaces=1,
            QualityFilter='LOW'
        )
        face = response['FaceRecords'][0]['Face']
        id = face['FaceId']
        idFile += str.encode(id) + b'\r\n'
    # response = rekognition.list_faces(CollectionId=COLLECTION, MaxResults=1)
    # while tokens:
    #     for face in response['Faces']:
    #         faceId = face['FaceId']
    #         idFile += str.encode(faceId) + b'\r\n'
    #     if 'NextToken' in response:
    #         nextToken = response['NextToken']
    #         response = rekognition.list_faces(CollectionId=collection_id,
    #                                           NextToken=nextToken, MaxResults=1)
    #     else:
    #         tokens = False
    obj_file.put(ACL='public-read', Body=idFile)
    return
