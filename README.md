# Speech Analytics Task

## Description

Simple REST API for speech-analytics using flask.

## Installation

### Using Docker

1. Clone the repository:
   ```sh
   git clone https://github.com/mostafanasser2000/speech-analytics-task.git
   ```
2. Navigate to the project directory:
   ```sh
   cd rdi-task
   ```
3. Build and the docker image:
   ```sh
   docker build -t flask-app .
   ```
4. Run the application using docker:
   ```sh
   ./run.sh
   ```

### Normal Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/mostafanasser2000/speech-analytics-task.git
   ```
2. Navigate to the project directory:
   ```sh
   cd speech-analytics-task
   ```
3. Create a virtual environment:
   ```sh
   python -m venv .venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```
5. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

6. Run tests:
   ```sh
   pytest tests/test_api.py
   ```
7. Run the application using guicorn or uwsgi:
   ```sh
   ./guicorn.sh
   ```
