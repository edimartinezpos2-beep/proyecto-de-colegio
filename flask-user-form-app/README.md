# Flask User Form Application

This project is a simple Flask web application that allows users to register by providing their name and email address. The application stores user information in an SQLite database and displays a list of registered users.

## Project Structure

```
flask-user-form-app
├── app.py                # Main application file
├── requirements.txt      # Project dependencies
├── templates             # HTML templates
│   └── index.html       # User registration form and user list
├── static                # Static files
│   └── styles.css       # CSS styles for the application
├── database              # Database files
│   └── users.db         # SQLite database for storing user information
└── README.md             # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd flask-user-form-app
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```
   python app.py
   ```

5. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000` to view the user registration form.

## Usage

- Fill in the form with your name and email address, then click "Guardar" to register.
- The registered users will be displayed in a table below the form.

## License

This project is licensed under the MIT License.