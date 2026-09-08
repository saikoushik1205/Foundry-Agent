import azure.functions as func
import json

app = func.FunctionApp()

@app.route(route="GetStudentInfo", auth_level=func.AuthLevel.ANONYMOUS)
def GetStudentInfo(req: func.HttpRequest) -> func.HttpResponse:

    student_info = {
        "name": "Sai Koushik",
        "student_id": "N24H01A0623",
        "college": "NIAT",
        "course": "B.Tech Computer Science",
        "year": "3rd Year",
        "skills": [
            "Python",
            "SQL",
            "Angular",
            "Node.js",
            "GenAI"
        ]
    }

    return func.HttpResponse(
        json.dumps(student_info),
        mimetype="application/json",
        status_code=200
    )