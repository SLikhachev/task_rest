
from flask_restful import Resource

class Test(Resource):
    
    def get(self):

        return { "message": "I'm Just WORKING" }

