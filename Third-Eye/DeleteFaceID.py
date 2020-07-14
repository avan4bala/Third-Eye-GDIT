import boto3

# with open('C:\\Users\\alexm\Documents\\DevSecOps\\faceIds.txt', 'r') as file:
#     IDs = []
#     for line in file:
#         IDs.append(line.rstrip('\n'))

BUCKET = "third-eye-reference-bucket"
COLLECTION = "Third_Eye_References"

s3 = boto3.resource('s3')
obj = s3.Object(BUCKET, 'IDs/faceIDs.txt')
idFileEncoded = obj.get()['Body'].read()
idFileDecoded = idFileEncoded.decode('utf-8')
IDs = idFileDecoded.split('\n')


def delete_faces_in_collection(collection_id):
    max_results = 2
    tokens = True

    client = boto3.client('rekognition')
    response = client.list_faces(CollectionId=collection_id,
                                 MaxResults=max_results)

    while tokens:

        faces = response['Faces']

        for face in faces:
            if face['FaceId'] not in IDs:
                res = client.delete_faces(CollectionId=collection_id,
                                          FaceIds=[face['FaceId']])
        if 'NextToken' in response:
            next_token = response['NextToken']
            response = client.list_faces(CollectionId=collection_id,
                                         NextToken=next_token, MaxResults=max_results)
        else:
            tokens = False
    return


# def main():
#     collection_id = 'Third_Eye_References'
#
#     delete_faces_in_collection(collection_id)
#
#
# if __name__ == "__main__":
#     main()
