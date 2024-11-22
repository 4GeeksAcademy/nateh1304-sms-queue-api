"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from database import Queue
#from models import Person
from sms import send_SMS

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
queue = Queue()

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/new', methods=['POST'])
def add_to_queue():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    mode = data.get('mode', 'FIFO').upper()

    if not name or not phone:
        return jsonify({'error': 'Name and phone are required'}), 400

    try:
        queue.set_mode(mode)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    queue.enqueue({'name': name, 'phone': phone})
    position = queue.size() 
    
    send_SMS(f"Hello {name}, you have been added to the queue. There are {position} people ahead of you.", phone)
    return jsonify({'message': 'User added to the queue', 'queue_position': position}), 201


@app.route('/next', methods=['GET'])
def get_next():
    if queue.size() == 0:
        return jsonify({'message': 'The queue is empty'}), 200

    next_person = queue.dequeue()
    if next_person:
        name = next_person['name']
        phone = next_person['phone']
        message = f"Hello {name}, it is now your turn."
        return jsonify({'message': f'{name} has been processed'}), 200
    else:
        return jsonify({'error': 'Unable to process next person'}), 500


# @app.route('/next', methods=['GET'])
# def get_next():
#     if queue.size() == 0:
#         return jsonify({'message': 'The queue is empty'}), 200

#     next_person = queue.dequeue()
#     if next_person:
#         name = next_person['name']
#         phone = next_person['phone']
#         message = f"Hello {name}, it is now your turn."
#         return jsonify({'message': f'{name} has been processed'}), 200
#     else:
#         return jsonify({'error': 'Unable to process next person'}), 500

@app.route('/all', methods=['GET'])
def get_all():
    return jsonify(queue.get_queue()), 200
    
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
