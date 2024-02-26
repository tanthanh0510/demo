import torch
import torchvision

from PIL import Image
import boto3
import os

s3 = boto3.client('s3')

def uploadFile(file_name, bucket="mic-vietnam", object_name=None):
    if object_name is None:
        object_name = file_name
    try:
        response = s3.upload_file(file_name, bucket, object_name)
        urlObject = s3.generate_presigned_url(
            'get_object', Params={'Bucket': bucket, 'Key': object_name})
        urlObject = urlObject.split('?')[0]
        return urlObject
    except Exception as e:
        raise e

def blend(origin, mask1=None, mask2=None):
    img = torchvision.transforms.functional.to_pil_image(origin + 0.5).convert("RGB")
    if mask1 is not None:
        mask1 =  torchvision.transforms.functional.to_pil_image(torch.cat([
            torch.zeros_like(origin),
            torch.stack([mask1.float()]),
            torch.zeros_like(origin)
        ]))
        img = Image.blend(img, mask1, 0.2)
        
    if mask2 is not None:
        mask2 =  torchvision.transforms.functional.to_pil_image(torch.cat([
            torch.stack([mask2.float()]),
            torch.zeros_like(origin),
            torch.zeros_like(origin)
        ]))
        img = Image.blend(img, mask2, 0.2)
    
    return img