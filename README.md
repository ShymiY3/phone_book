# PhoneBook

## Description

PhoneBook is a RESTful web application written in Python using the FastApi framework. It allows users to collect and display phone numbers, with the ability to edit and delete entries created by the same user.

## Requirements

- Python >3.10
- See the `requirements.txt` file for additional dependencies.

## Getting Started

To run the application, follow the steps below:

1. Clone the repository:

   ```
   git clone https://github.com/ShymiY3/phone_book.git
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   
   - On Windows:
   
     ```
     venv\Scripts\activate
     ```
   
   - On Linux:
   
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies using pip:

   ```
   pip install -r requirements.txt
   ```

5. Start the application using uvicorn from the repository's root directory:

   ```
   uvicorn phone_book.main:app
   ```
