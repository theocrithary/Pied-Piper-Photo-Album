#!/usr/bin/env python3
import os
import boto
from flask import Flask
from config import ecs_test_drive

app = Flask(__name__)

#### Get ECS credentials from external config file
ecs_access_key_id = ecs_test_drive['ecs_access_key_id']  
ecs_secret_key = ecs_test_drive['ecs_secret_key']
bucket_name = ecs_test_drive['bucket_name']

## Open a session with your ECS
session = boto.connect_s3(ecs_access_key_id, ecs_secret_key, host='object.ecstestdrive.com')  
## Get hold of your bucket
b = session.get_bucket(bucket_name)
print ("ECS connection is: " + str(session))
print ("Bucket is: " + str(b))

print ("Uploading photos ...")
## Create a list of filenames in "photos" to upload to ECS
for each_photo in os.listdir("photos"):
    print ("Uploading " + str(each_photo))
    k = b.new_key(each_photo)
    src = os.path.join("photos", each_photo)
    k.set_contents_from_filename(src)
    k.set_acl('public-read')

## Alterntively walk recursively a dir tree. It creates a string and 2 lists
##
##for (dirpath, dirnames, filenames) in os.walk("photos"):

bucket_url = "http://" + ecs_access_key_id.split('@')[0] + ".public.ecstestdrive.com/" + bucket_name

print ("Upload complete!")
print ("Starting the photoalbum")

@app.route('/')
def mainmenu():

    begin_page = """
    <html><head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
    <title>Pied Piper - Photo Album</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
    </head>
    <body>
    <div class="container">
        <h1 class="gallery-title">My first photo-book in Python</h1><hr>
        <div class="row">"""

    mid_page = ""
    ## List all the keys in the bucket and grab the images with html code
    for photo in b.list():
        print(photo.key)
        mid_page += """<div class="col-xs-6 col-md-3">{}
        <a href="{}/{}" class="thumbnail"><img src="{}/{}"></a></div>""".format(photo.key, bucket_url, photo.key, bucket_url, photo.key)
    
    end_page = """
        </div></div>
    </div>
    </body>
    </html>"""

    return begin_page + mid_page + end_page

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', '5000')), threaded=True)