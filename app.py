from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy


from sqlalchemy import Boolean, Column, String


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
db = SQLAlchemy(app)


# @dataclass
class TODO(db.Model):
    __tablename__ = "todo"

    id = Column(db.Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    discription = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=True)

    def __init__(self, title, discription):
        self.title = title
        self.discription = discription

    def serialize(self):
        return {"id": self.id, "title": self.title, "discription": self.discription}


with app.app_context():
    db.create_all()


@app.route("/test/", methods=["GET"])
def test():
    return make_response(jsonify({"message": "test route"}), 200)


@app.route("/todo/", methods=["POST"])
def create_todo():
    try:
        data = request.get_json()
        todo = TODO(title=data["title"], discription=data["discription"])
        db.session.add(todo)
        db.session.commit()
        data = {
            "id": todo.id,
            "title": todo.title,
            "is_active": todo.is_active,
            "discription": todo.discription,
        }

        return (make_response(jsonify(data)), 201)
    except Exception as e:
        return make_response(jsonify({"message": f"{e}"}), 500)


@app.route("/todo/", methods=["GET"])
def get_todo():
    todos = TODO.query.all()
    data = [
        {
            "id": todo.id,
            "title": todo.title,
            "is_active": todo.is_active,
            "discription": todo.discription,
        }
        for todo in todos
    ]
    return make_response(jsonify(data), 200)


@app.route("/todo/<int:id>/", methods=["PUT"])
def update_todo(id):
    try:
        todo_to_update = TODO.query.filter_by(id=id).first()
        if todo_to_update:
            data = request.get_json()

            for key, value in data.items():
                if key == "id":
                    continue
                setattr(todo_to_update, key, value)

            db.session.add(todo_to_update)
            db.session.commit()

            data = {
                "id": todo_to_update.id,
                "title": todo_to_update.title,
                "is_active": todo_to_update.is_active,
                "discription": todo_to_update.discription,
            }

            return make_response(jsonify(data), 201)

        return make_response({"message": "todo not found"}, 400)
    except Exception as e:
        return make_response(jsonify({"message": f"{e}"}), 500)


@app.route("/todo/<int:id>/", methods=["DELETE"])
def delete_todo(id):
    try:
        todo_to_delete = TODO.query.filter_by(id=id).first()
        if todo_to_delete:
            db.session.delete(todo_to_delete)
            db.session.commit()
            return make_response(jsonify({"message": f"deleted"}), 200)
        return make_response({"message": "todo not found"}, 400)

    except Exception as e:
        return make_response(jsonify({"message": f"{e}"}), 500)
