# Backend - Full Stack Trivia API

### Installing Dependencies for the Backend

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

4. **Key Dependencies**

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

### Database Setup

With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## ToDo Tasks

These are the files you'd want to edit in the backend:

1. _./backend/flaskr/`__init__.py`_
2. _./backend/test_flaskr.py_

One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.

2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.

3. Create an endpoint to handle GET requests for all available categories.

4. Create an endpoint to DELETE question using a question ID.

5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.

6. Create a POST endpoint to get questions based on category.

7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.

8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.

9. Create error handlers for all expected errors including 400, 404, 422 and 500.

## API Reference

---

### Introduction:

The Trivia API is:

- REST-based
- Requires no authentication
- Only returns JSON responses.
  All URLS referenced have the following base URL to be used in a local environment: `http://127.0.0.1:5000/`

### Errors

When an error occurs during a request to this API, you will receive:

- A HTTP error code (4xx, 5xx)
- A JSON response with the following format

```
    {
        "error": 404,
        "message": "resource not found",
        "success": False
    }
```

### **Endpoints**

**`GET` /categories**

Gets a list of categories

Example request:

```
curl http://127.0.0.1:5000/categories
```

Example response:

```
{
    "categories": {
        "1":"Science",
        "2":"Art",
        "3": "Geography",
        "4": "History",
        "5": Entertainment",
        "6": "Sports"
    },
    "success": true
}
```

**`GET` /questions**

Gets a list of questions (optionally by page) showing 10 results per page
Paramaters:
page (optional): Specify which page of results to return (starting at 1)

Example request:

```
curl http://127.0.0.1:5000/questions
curl http://127.0.0.1:5000/questions?page=2
```

Example response:

```
    {
        "success": true,
        "questions": [
            {
                "id": 20,
                "question": "What is the heaviest organ in the human body?",
                "answer": "The Liver",
                "category": 1,
                "difficulty": 4
            },
            {
                "id": 21,
                "question": "Who discovered penicillin?",
                "answer": "Alexander Fleming",
                "category": 1,
                "difficulty": 3
            },
            ...
        ],
        "total_questions": 45,
        "current_category": null,
        "categories": {
            "1":"Science",
            "2":"Art",
            "3": "Geography",
            "4": "History",
            "5": Entertainment",
            "6": "Sports"
        }
    }
```

**`GET` /categories/{id}/questions**

Gets the questions in the requested category specified by id

Parameters: `id` - The id of the category

Example request:

```
curl http://127.0.0.1:5000/categories/1/questions
```

Example response:

```
{
    'questions': [
        {
            'id': 20,
            'question': 'What is the heaviest organ in the human body?',
            'answer': 'The Liver',
            'difficulty': 4,
            'category': 1
        },
    ],
    'total_questions': 45,
    'current_category': 'Science',
    'success': true
}
```

**`DELETE` /questions/{id}**

Deletes the requested question specified by id.

Parameters: `id` - The id of the question to be deleted.

Example request:

```
curl -X DELETE http://127.0.0.1:5000/questions/1
```

Example response:
Returns a 204 status code on success.

```
No response
```

**`POST` /quizzes**

Provides the next question in the quiz that hasn't previously been answered.

Request body:

```
    {
        'previous_questions': [1, 4, 20, 15],
        'quiz_category': {
            "id": 1,
            "type":"Science",
        }
    }

    previous_questions - An array of question ids that have previously been shown in the quiz
    quiz_category - A category object including `id` and `type` of the requested category
```

Example request:

```
curl http://127.0.0.1:5000/quizzes -X POST -d '{"previous_questions", [1, 4, 20, 15], "quiz_category": {"id": 1, "type":"Science",}}' -H "Content-Type:"application/json"
```

Example response: A single question object

```
{
    'question':  {
        'id': 20,
        'question': 'What is the heaviest organ in the human body?',
        'answer': 'The Liver',
        'difficulty': 4,
        'category': 1
    }
}
```

**`POST` /questions**
Creates a new question or searches for questions by search term

**Search**
Request Body:

```
    {"searchTerm": "What"}
```

Example search request:

```
curl http://127.0.0.1:5000/questions -X POST -H "Content-Type:application/json" -d '{"searchTerm":"What"}'
```

Example search response:

```
{
    "questions": [
        {
            "id": 20,
            "question": "What is the heaviest organ in the human body?",
            "answer": "The Liver",
            "category": 1,
            "difficulty": 4
        },
        {
            "id": 21,
            "question": "Who discovered penicillin?",
            "answer": "Alexander Fleming",
            "category": 1,
            "difficulty": 3
        },
        ...
    ],
    "total_questions": 20,
    "current_category": null,
    "success": true
}
```

**Create question**
Request body:

```
{
    'question':  'Heres a new question string',
    'answer':  'Heres a new answer string',
    'difficulty': 1,
    'category': 3,
}
```

Example create request:

```
curl http://127.0.0.1:5000/questions -X POST -H "Content-Type:application/json" -d '{"question": "Heres a new question string", "answer": "Heres a new answer string", "difficulty": 1, "category": 3}'
```

Example create response

```
Returns a 201 status code with no response body
```

## Review Comment to the Students

````

This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code.

Endpoints
GET '/api/v1.0/categories'
GET ...
POST ...
DELETE ...

GET '/api/v1.0/categories'

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs.
  {'1' : "Science",
  '2' : "Art",
  '3' : "Geography",
  '4' : "History",
  '5' : "Entertainment",
  '6' : "Sports"}

```

## Testing

To run the tests, run

```

dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py

```

```

```

```
````
