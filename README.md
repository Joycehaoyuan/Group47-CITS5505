# Agile Web Development - CITS5505 Group Project

## 📝⏱️ NutriMate Overview

Struggling with meal planning and nutrition tracking? Want to eat healthier without all the hassle? NutriMate is here to help! 💪

Our project **NutriMate** is a web application designed to help users generate personalized meal plans, track their nutritional intake, visualize their progress, and share their data with friends or health professionals.

It allows users to **create meal plans**, **upload dietary data**, **analyze nutritional trends**, and **share their results** with other users.

## 🎯 Key Features

* User login, registration, and profile management
* Meal plan generation based on dietary preferences and calorie targets
* Manual entry and CSV upload of personal nutrition data
* Comprehensive data visualization and nutritional analytics
* Ability to share meal plans and nutrition data with other users
* Responsive design for desktop and mobile devices

## 👥 Team Members

| Name | Student ID | GitHub Username |
|------|------------|-----------------|
| [Tinghui Jiang] | [23936218] | [Joycehaoyuan] |
| [Yuxin Sun] | [21900579] | [WynonnaSun] |
| [Roshini Vadla] | [24324533] | [RoshiniVadla75] |
| [Keerthana Narkunaraja] | [24300247] | [Keetz3103] |

## 🛠️ Applied Technologies and Libraries

* **Frontend**: HTML, CSS, JavaScript, jQuery, Bootstrap, Chart.js
* **Backend**: Flask, SQLAlchemy
* **Data Processing**: Python, SQLite
* **Authentication**: Flask-Login
* **Form Handling**: Flask-WTF
* **Data Visualization**: Chart.js

## 📱 Application Views

* **Introductory View**: Landing page explaining the app's purpose and benefits
* **Upload Data View**: Enter nutrition data manually or via CSV upload
* **Meal Plan View**: Create and customize personalized meal plans based on preferences
* **Visualization View**: Interactive charts and statistics of nutritional data
* **Share Data View**: Select and share meal plans and nutrition data with other users

## 🚀 How to Run the Application

### Virtual Environment Setup

A Virtual Environment is necessary to develop and test the application. This is performed in a safe, self-contained manner through Python's Virtual Environment.
This project uses a .env file to manage environment variables, especially for sensitive information.

### 1. Initialise a Python Virtual Environment

Ensure that your current working directory contains the `requirements.txt`
file, in this case it is '/venv', then use:

`$ python -m venv venv`

NOTE: Your system may have `python3` aliased as something other than `python`

### 2. Activate the new Virtual Environment

On standard Unix operating systems this would be:

`$ source venv/bin/activate`

On Windows systems:

`$ venv\Scripts\activate`

### 3. Install Requirements

The `requirements.txt` file contains all the Python dependencies that the application requires to run. These can be downloaded and installed with:

`$ pip install -r requirements.txt`

NOTE: Your system may have `pip3` aliased as something other than `pip`.


### 4. Start the server

To start the server and open pages in our browser, the follow command should be executed:

`flask run`

The application should now be running at [http://localhost:5050](http://localhost:5050/). If you want to modify the port number, you can modify it in `.flaskenv` and
`pip install python-dotenv`. 

## ⚙️ Module Design

### 1. Authentication Module

#### Function Overview

The Authentication Module handles user registration, login, logout, and account management, ensuring secure access to the application.

#### Main Features

* **Registration**: Users can create an account by providing username, email, and password.
* **Login**: Registered users can securely log in to access personalized features.
* **Logout**: Users can safely end their sessions.
* **Password Management**: Includes password hashing for security.

#### Main Files

* `app/models.py`: Defines the `User` model with authentication methods.
* `app/forms.py`: Contains `RegistrationForm` and `LoginForm` for user input validation.
* `app/routes.py`: Implements authentication-related routes and view functions.
* `app/templates/`: Contains HTML templates (`login.html`, `register.html`).

### 2. Upload Nutrition Tracking Module

#### Function Overview

The Nutrition Tracking Module enables users to record and monitor their daily nutritional intake through manual entry or CSV upload.

#### Main Features

* **Manual Data Entry**: Users can enter nutrition data manually, including calories, protein, carbs, and fat.
* **CSV Upload**: Users can upload nutrition data in CSV format for bulk processing.
* **Meal Recording**: Users can record individual meals within their daily log.
* **Notes**: Users can add notes to their nutrition entries.

#### Main Files

* `app/models.py`: Defines the `UserDietaryData` model.
* `app/forms.py`: Contains `UploadDietaryDataForm` and `UploadCSVForm`.
* `app/routes.py`: Implements routes for data upload and processing.
* `app/templates/`: Contains HTML templates (`upload_data.html`).
* `app/static/js/upload.js`: Calculate calories based on user inputs.

### 3. Meal Planning Module

#### Function Overview

The Meal Planning Module allows users to generate and customize meal plans based on their dietary preferences, calorie targets, and meal count preferences.

#### Main Features

* **Diet Selection**: Users can choose from various diet types (Keto, Mediterranean, Paleo, Vegan, Vegetarian, or Anything).
* **Calorie Targeting**: Users can set daily calorie targets for their meal plans.
* **Meal Customization**: Users can refresh individual meals to get alternatives.
* **Recipe Suggestions**: Users can get recipe suggestions based on ingredients in their meal plan.

#### Main Files

* `app/models.py`: Defines the `MealPlan` and `Food` models.
* `app/forms.py`: Defines the `MealPlanForm` for user input.
* `app/routes.py`: Handles meal plan generation and customization.
* `app/utils.py`: Contains utility functions for meal plan generation and food selection.
* `app/templates/`: Contains HTML templates (`meal_plan.html`).
* `app/static/js/meal-plan.js`: Client-side functionality for meal plan interaction.

### 4. Data Visualization Module

#### Function Overview

The Data Visualization Module provides users with interactive charts and statistics to analyze their nutritional trends over time.

#### Main Features

* **Calorie Tracking**: Visualize calorie intake trends over time.
* **Macronutrient Analysis**: Chart protein, carbs, and fat consumption.
* **Statistical Overview**: Provide summaries of nutritional averages.
* **Comparison Tools**: Compare actual intake with target values.

#### Main Files

* `app/routes.py`: Implements the visualization view functions.
* `app/templates/`: Contains HTML templates (`visualize_data.html`).
* `app/static/js/chart-config.js`: JavaScript for generating and configuring charts.
* `app/static/js/delete-data.js`: Delete nutritional data records.

### 5. Data Sharing Module

#### Function Overview

The Data Sharing Module allows users to share their meal plans and nutritional data with other users on the platform.

#### Main Features

* **Share Meal Plans**: Users can share specific meal plans with other users.
* **Share Dietary Data**: Users can share their nutrition logs with others.
* **View Shared Data**: Users can access data that others have shared with them.
* **Manage Shares**: Users can view and delete their shared data.

#### Main Files

* `app/models.py`: Defines the `SharedData` model.
* `app/forms.py`: Contains the `ShareDataForm`.
* `app/routes.py`: Handles data sharing functionality.
* `app/templates/`: Contains HTML templates (`share_data.html`, `shared_with_me.html`).
* `app/static/js/share-data.js`: Client-side functionality for data sharing.

### 6. Recipe Module

#### Function Overview

The Recipe Module provides recipe suggestions based on meal ingredients and supports recipe management within the application.

#### Main Features

* **Recipe Suggestions**: Generate recipe ideas based on food items in meal plans.
* **Recipe Details**: View detailed recipe information including ingredients and instructions.
* **API Integration**: Connect with external recipe APIs for additional suggestions.

#### Main Files

* `app/models.py`: Defines the `Recipe` and `RecipeIngredient` models.
* `app/recipe_api.py`: Implements recipe API integration and processing.
* `app/routes.py`: Routes for recipe-related functionality.
* `app/static/js/meal-plan.js`: Contains recipe suggestion modal functionality.

### 7. Profile Module

#### Function Overview

The Profile Module allows users to view and manage their account information and activity statistics.

#### Main Features

* **View Activity**: Users can see statistics on their meal plans and data entries.
* **Account Information**: Users can view their account details.
* **Quick Access**: Provides shortcuts to main application features.

#### Main Files

* `app/routes.py`: Implements profile-related routes.
* `app/templates/`: Contains HTML templates (`profile.html`).

## 🧪 How to Run Tests

### Running Tests

NutriMate uses both unit tests (pytest) and UI tests (Selenium) to ensure application quality and functionality. Our comprehensive test suite covers models, routes, forms, and user interface interactions.

### 1. Setup Testing Environment

First, install the required testing packages:

```bash
pip install -r requirements.txt
```

Note: `requirements.txt` already includes `pytest`, `selenium` and other testing dependencies.

### 2. Running All Tests (Unit + Selenium)

To run the complete test suite:

```bash
pytest
```

Or alternatively:

```bash
python -m pytest
```

### 3. Running Only Unit Tests

To run only the unit tests:

```bash
pytest tests/unit
```

Or alternatively:

```bash
python -m pytest tests/unit
```

Unit tests cover:

- Database models validation
- Form validation logic
- Utility functions
- Route handlers
- Authentication functionality

### 4. Running Only Selenium Tests

To run only the UI/integration tests with Selenium:

```bash
pytest tests/selenium -m selenium
```

Or alternatively:

```bash
python -m pytest tests/selenium -m selenium
```

Selenium tests cover:

- User registration and login flows
- Meal plan creation process
- Data upload functionality
- Visualization interactions
- Data sharing features

Note: Make sure you have Chrome or Firefox installed and the appropriate WebDriver configured for Selenium tests.

### 5. Running Specific Test Files

You can run individual test files for targeted testing:

```bash
# To test model functionality
pytest tests/unit/test_models.py

# To test specific UI functionality
pytest tests/selenium/test_upload.py -m selenium
```





