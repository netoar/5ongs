# 5ongs
Final project of Udacity nanodegree

This is a Flask application that provides a web interface to manage songs and their ratings. Users can perform various operations such as creating, editing, and deleting songs, as well as viewing the list of songs.

Setup and Installation
1. Clone the repository to your local machine.
2. Install the required dependencies by running the following command:

pip install -r requirements.txt

3. Set up the database by executing the following command:

python model/db_config.py

4. Run the application using the following command:

python app.py

5. Access the application by visiting https://fiveongs-app.onrender.com/ in your web browser. You can check the environment variables in the `environment_variables.sh` file.

# Application Structure
The application follows the MVC (Model-View-Controller) architectural pattern. The main components of the application are:

- app.py: This is the entry point of the application and contains the Flask app creation and configuration code.
- model: This directory contains the database models and configuration files.
- templates: This directory contains the HTML templates for rendering the web pages.
- auth.py: This file contains helper functions for user authentication and authorization.
- utils.py: This file contains utility functions used in the application.

# Routes and Endpoints
The following routes and endpoints are available in the application:

- /: The home page of the application. Displays a list of songs and allows users to log in and log out.
- /callback: The callback URL for the authentication flow. Handles the retrieval of access tokens and user information.
- /logout: Logs out the user and clears the session.
- /song: Displays the list of songs.
- /song/create: Allows authenticated users to create a new song. Supports both GET and POST requests.
- /song/<int:song_id>/edit: Allows authenticated users to edit an existing song. Supports both GET and POST requests.
- /song/<int:song_id>: Displays the details of a specific song.
- /song/<int:song_id>/delete: Allows authenticated users to delete a song. Supports POST request.

# Authentication and Authorization
The application uses OAuth 2.0 for authentication and authorization. Users can log in using their preferred OAuth provider (configured in the auth.py file). The application supports the following permissions:

- post:songs: Allows the user to create new songs.
- post:rate: Allows the user to rate a song.
- delete:songs: Allows the user to delete songs.

Certain routes and endpoints in the application require specific permissions, and unauthorized access will result in appropriate error responses.

# Error Handling
The application includes error handlers for the following HTTP status codes:

- 400 Bad Request: Handles invalid requests or missing parameters.
- 404 Not Found: Handles requests for nonexistent resources.
- 422 Unprocessable Entity: Handles requests with invalid data or unable to process.
- 500 Internal Server Error: Handles server-side errors.

# Dependencies
The application uses the following dependencies:

- Flask: A lightweight web framework for building web applications.
- Flask SQLALchemy: Provides integration with SQLAlchemy for database operations.
- Flask CORS: Enables Cross-Origin Resource Sharing (CORS) for handling requests from different domains.
- Jose: A JavaScript Object Signing and Encryption (JOSE) library for JSON Web Tokens (JWT) handling.
- urllib: Provides URL parsing functionality.
- secrets: Generates secure random tokens for session management.