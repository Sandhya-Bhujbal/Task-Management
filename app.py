from flask import Flask, request, jsonify
from app.models import db, bcrypt, User
from app.config import engine, get_session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity


app = Flask(__name__)

# Example route that uses the database
@app.route('/')
def index():
    session = get_session()
    # Use the session to interact with the database
    return 'Database connected!'

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Create the database
with app.app_context():
    db.create_all()

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    current_user = get_jwt_identity()
    new_task = Task(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'Todo'),
        priority=data.get('priority', 'Low'),
        due_date=data.get('due_date', None),
        user_id=current_user['username']  # assuming username is unique
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully!'}), 201

@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    current_user = get_jwt_identity()
    filters = []
    
    status = request.args.get('status')
    if status:
        filters.append(Task.status == status)
        
    priority = request.args.get('priority')
    if priority:
        filters.append(Task.priority == priority)
        
    due_date = request.args.get('due_date')
    if due_date:
        filters.append(Task.due_date == due_date)
    
    search = request.args.get('search')
    if search:
        filters.append(Task.title.like(f'%{search}%') | Task.description.like(f'%{search}%'))
    
    tasks = Task.query.filter(*filters, Task.user_id == current_user['username']).all()
    return jsonify([task.as_dict() for task in tasks]), 200

@app.route('/tasks/<int:id>', methods=['GET'])
@jwt_required()
def get_task(id):
    task = Task.query.get_or_404(id)
    return jsonify(task.as_dict()), 200

@app.route('/tasks/<int:id>', methods=['PUT'])
@jwt_required()
def update_task(id):
    data = request.get_json()
    task = Task.query.get_or_404(id)
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    task.due_date = data.get('due_date', task.due_date)
    
    db.session.commit()
    return jsonify({'message': 'Task updated successfully!'}), 200

@app.route('/tasks/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'}), 200


if __name__ == '__main__':
    app.run(debug=True)
