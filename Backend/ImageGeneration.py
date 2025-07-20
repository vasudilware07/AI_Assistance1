import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
import time

def open_images(prompt):
    folder_path = r"Data\images"
    Files = [f"{prompt.replace(' ', '_')}{i + 1}.jpg" for i in range(4)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image {image_path}")
            img.show()
        except IOError:
            print(f"Unable to open Image Path: {image_path}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}
#headers = {"Authorization": "Bearer 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"}

async def query(payload):
    retries = 3  # Number of retries
    for attempt in range(retries):
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        if response.status_code == 429:  # Rate limit exceeded
            print(f"Rate limit exceeded. Waiting for 60 seconds before retry {attempt + 1}...")
            await asyncio.sleep(60)  # Wait for 60 seconds
            continue
        elif response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        return response.content
    raise Exception("Max retries reached. Unable to complete the request.")

async def generate_images(prompt: str):
    tasks = []

    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, High Resolution, seed = {randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        await asyncio.sleep(20)  # Add a 20-second delay between requests
        
    image_bytes_list = await asyncio.gather(*tasks)

    # Ensure the Data folder exists
    os.makedirs("Data", exist_ok=True)

    for i, image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\images\{prompt.replace(' ', '_')}{i + 1}.jpg", "wb") as f:
            f.write(image_bytes)

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()

        Prompt, Status = Data.split(",")

        if Status.strip() == "True":
            print("Generating Images...")
            GenerateImages(prompt=Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            break

        else:
            time.sleep(1)

    except FileNotFoundError:
        print("Frontend\Files\ImageGeneration.data file not found. Waiting...")
        time.sleep(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(1)