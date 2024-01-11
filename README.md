# FastAPI Todo App

A simple FastAPI application for managing todos and user authentication.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [Todo Operations](#todo-operations)
  - [User Operations](#user-operations)
- [API Documentation](#api-documentation)
- [License](#license)

## Overview

This FastAPI application provides a simple API for managing todos, user authentication, and admin-specific functionalities. It includes endpoints for creating, updating, deleting todos, changing passwords, and retrieving user information.

## Features

- User Authentication with JWT tokens
- CRUD operations for Todos
- User-specific operations
- Admin-specific operations

## Getting Started

### Prerequisites

- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite

### Installation

```console
cd ToDoApp/
pip install requirements.txt
```

## Usage
To run the project:
```console
uvicorn main:app --reload
```

### Authentication

To use the API, you need to authenticate by obtaining an access token. Send a POST request to `/auth/token` with valid credentials.

### Todo Operations

- **Read Todos:** `GET /todo`
  - Retrieve a list of all todos.

- **Read Todo by ID:** `GET /todo/{todo_id}`
  - Retrieve a specific todo by its ID.

- **Create Todo:** `POST /todo`
  - Create a new todo by sending a POST request with the required parameters.

- **Update Todo by ID:** `PUT /todo/{todo_id}`
  - Update a specific todo by its ID using a PUT request with the desired changes.

- **Delete Todo by ID:** `DELETE /todo/{todo_id}`
  - Delete a specific todo by its ID.

### User Operations

- **Get User Information:** `GET /user/get_user`
  - Retrieve information about the authenticated user.

- **Change Password:** `PUT /user/change_password`
  - Change the password of the authenticated user.

## API Documentation

Access the Swagger documentation and interactive API at [http://localhost:8000/docs](http://localhost:8000/docs) and the ReDoc documentation at [http://localhost:8000/redoc](http://localhost:8000/redoc).


## License

This project is licensed under the [MIT License](LICENSE).


