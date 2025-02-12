import boto3
import sys
from datetime import datetime, timezone, timedelta
from botocore.exceptions import ClientError, ProfileNotFound

def get_ecr_client(profile_name, region):
    try:
        session = boto3.Session(profile_name=profile_name)
        return session.client('ecr', region_name=region)
    except ProfileNotFound:
        print(f"ERROR: AWS profile '{profile_name}' not found.")
        sys.exit(1)

def is_sha_digest(digest):
    if ':' in digest:
        sha = digest.split(':')[1]
        return len(sha) == 64
    return False

def should_delete_image(image, cutoff_date):
    if not is_sha_digest(image['imageDigest']):
        print(f"Skipping image with non-SHA digest: {image['imageDigest']}")
        return False
    
    pushed_date = image['imagePushedAt'].replace(tzinfo=timezone.utc)
    if pushed_date >= cutoff_date:
        print(f"Skipping image newer than cutoff: {pushed_date} >= {cutoff_date}")
        return False
    
    return True

def clean_old_images():
    PROFILE_NAME = 'sso-om-prod'
    REGION = 'us-east-1'
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)
    
    print(f"Using cutoff date: {cutoff_date}")
    ecr_client = get_ecr_client(PROFILE_NAME, REGION)
    
    try:
        paginator = ecr_client.get_paginator('describe_repositories')
        repositories = []
        
        for page in paginator.paginate():
            repositories.extend(page['repositories'])
        
        if not repositories:
            print("No ECR repositories found.")
            return
        
        total_deleted = 0
        total_size_saved = 0
        
        for repo in repositories:
            repo_name = repo['repositoryName']
            print(f"\nProcessing repository: {repo_name}")
            
            try:
                image_paginator = ecr_client.get_paginator('describe_images')
                images = []
                
                for image_page in image_paginator.paginate(repositoryName=repo_name):
                    images.extend(image_page['imageDetails'])
                
                print(f"Found {len(images)} total images in {repo_name}")
                
                images_to_delete = []
                for img in images:
                    if should_delete_image(img, cutoff_date):
                        images_to_delete.append({
                            'imageDigest': img['imageDigest'],
                            'pushedAt': img['imagePushedAt'],
                            'size': img['imageSizeInBytes'],
                            'tags': img.get('imageTags', [])
                        })
                
                print(f"Found {len(images_to_delete)} images to delete in {repo_name}")
                
                for img in images_to_delete:
                    try:
                        print(f"\nDeleting image:")
                        print(f"  Digest: {img['imageDigest']}")
                        print(f"  Tags: {', '.join(img['tags']) if img['tags'] else '<no tags>'}")
                        print(f"  Pushed: {img['pushedAt'].strftime('%Y-%m-%d %H:%M:%S')}")
                        size_mb = img['size'] / (1024 * 1024)
                        print(f"  Size: {size_mb:.2f} MB")
                        
                        ecr_client.batch_delete_image(
                            repositoryName=repo_name,
                            imageIds=[{'imageDigest': img['imageDigest']}]
                        )
                        
                        total_size_saved += img['size']
                        total_deleted += 1
                        print("  ✓ Successfully deleted")
                        
                    except ClientError as e:
                        print(f"  ✗ Error deleting image: {str(e)}")
            
            except ClientError as e:
                print(f"Error accessing repository {repo_name}: {str(e)}")
        
        total_size_mb = total_size_saved / (1024 * 1024)
        print(f"\nCleaning completed:")
        print(f"Total images deleted: {total_deleted}")
        print(f"Total space freed: {total_size_mb:.2f} MB")
    
    except ClientError as e:
        print(f"Error listing repositories: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("WARNING: This script will delete ECR images older than 2 months with SHA digests.")
    confirmation = input("Do you want to continue? (yes/no): ")
    
    if confirmation.lower() == 'yes':
        clean_old_images()
    else:
        print("Operation cancelled.")
