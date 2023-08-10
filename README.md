
# Image Data Processing Service

This service provides an API for processing and managing image data. It allows users to upload image data for processing 
and storage, and to retrieve processed image data based on a specified depth range.

## Prerequisites

- Docker: Ensure you have Docker installed and running on your system. If not, you can download and install Docker 
  from the [official site](https://www.docker.com/get-started).

## Getting Started

### 1. Clone the Repository

To get started, first clone the repository from GitHub:

```bash
git clone 
```


### 2. Navigate to the Project Directory

Once cloned, navigate to the project directory:

```bash
cd 
```


### 3. Setup and Running the Service

To start the service, run the following command:

```bash
make compose
```

This command will build the Docker images for the application and the database, 
and then start the containers using Docker Compose. Once the service is up and running, you can access the API endpoints.

The service will have an image uploaded to the database upon startup. This image is located in the [image](/image)

## API Endpoints

### 1. Upload Image Data

Upload image data for processing and storage.

  ```bash
  curl -X 'POST' \
  'http://localhost:8080/upload-image' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @sample_image.json
  ```
  
Notes:

Ensure that the data.json file is located in the current path or directory from which you're executing the command. 
If it's in a different location, replace @data.json with the full path to the file (e.g., @/path/to/data.json).

For testing purposes, a sample image file named sample_image.json has been provided. 
This file is located inside the tests folder. You can use this file as a reference or for initial testing of the 
POST endpoint. 

### 2. Get Image Data

Fetch image data based on depth range and colormap.



  ```bash
  curl -X 'GET' \
  'http://localhost:8080/image-depth-range' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "depth_min": 900.1,
  "depth_max": 9000.8,
  "colormap": "COLORMAP_JET"
}'

  ```
