from flask_restful import Resource

class Hello(Resource):
    def get(self):
        return {'task': 'Say "Hello, KKKKKKK!"'}

