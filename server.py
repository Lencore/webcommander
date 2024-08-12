from flask import Flask, render_template, request
import flask_restful as restful
import os
import time
from datetime import datetime

app = Flask(__name__)
api = restful.Api(app)

@app.route('/')
def index():
    return render_template('index.html')

class DataUpdate(restful.Resource):
    def _is_updated(self, request_time):
        return os.stat('data.txt').st_mtime > request_time

    def get(self):
        request_time = time.time()
        timeout = 30  # Тайм-аут 30 секунд

        while not self._is_updated(request_time):
            time.sleep(0.5)
            if time.time() - request_time > timeout:
                return {'message': 'No updates available'}, 204  # Нет обновлений

        with open('data.txt') as data:
            content = data.read()

        return {'content': content,
                'date': datetime.now().strftime('%Y/%m/%d %H:%M:%S')}

class Data(restful.Resource):
    def get(self):
        with open('data.txt') as data:
            content = data.read()
        return {'content': content}

class SendData(restful.Resource):
    def post(self):
        new_content = request.json.get('content')
        if new_content is None:
            return {'error': 'No content provided'}, 400

        try:
            with open('data.txt', 'w') as data:
                data.write(new_content)
            return {'message': 'File updated successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(DataUpdate, '/data-update')
api.add_resource(Data, '/data')
api.add_resource(SendData, '/send')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
