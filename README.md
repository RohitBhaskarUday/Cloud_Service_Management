# FastAPI Cloud Services Management

## Overview

The FastAPI Cloud Subscription Service is a backend system designed to manage subscription plans in the cloud, user subscriptions, permissions, and API access control. It utilizes FastAPI for streamlined API development and interacts seamlessly with MongoDB for efficient database operations, optimized for high-performance cloud service environments.

### Project Team Members - Group Project 17

- Rohit Bhaskar Uday (CWID: 884451915)
- Sumanth Mittapally (CWID: 885157511)
- Rohit Chowdary Yadla (CWID: 885146852)

### Demonstration

[[Link to the Demonstration of the Project](#)](https://drive.google.com/drive/folders/1zHODMalBaeZrOLWZeWYdzkeB-A_WSIjk?usp=drive_link)

## Prerequisite Requirements

- Python version 3.6 or newer
- MongoDB

## Features

- **Subscription Plan Administration:** Creation, reading, updating, and deletion of subscription plans.
- **Permission Oversight:** Modification and deletion of permissions.
- **User Subscription Management:** Handling user subscriptions across various plans.
- **Access Regulation:** Managing user access to diverse API endpoints according to subscription levels.
- **API Usage Monitoring:** Tracking and limiting user API usage.

## Configuration

### MongoDB Setup:

Ensure MongoDB is installed and running locally or configure the connection details in `database.py`.

## Running the API

Start the FastAPI server:

```bash
uvicorn app.main:app
This command starts the FastAPI server locally. The --reload flag enables auto-reloading when code changes are detected (for development).
```
## Accessing the API
Launch Postman.
Set the request URL to http://127.0.0.1:8000/.
This interface allows you to explore and test the available endpoints interactively using Postman
