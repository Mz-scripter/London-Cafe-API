from flask import Flask, jsonify, render_template, request
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/random", methods=["GET"])
def random_cafe():
    with app.app_context():
        cafes = db.session.query(Cafe).all()
        cafe_details = random.choice(cafes)
        # return jsonify(cafe=cafe_details.to_dict())
        return jsonify(cafe =  {'name':cafe_details.name, 'map_url':cafe_details.map_url, 'img_url':cafe_details.img_url, 'location':cafe_details.location, 'amenities':{'seats':cafe_details.seats, 'has_toilet':cafe_details.has_toilet, 'has_wifi':cafe_details.has_wifi, 'has_sockets':cafe_details.has_sockets, 'can_take_calls':cafe_details.can_take_calls, 'coffee_price':cafe_details.coffee_price}})
        db.session.commit()
@app.route("/all", methods=["GET"])
def all_cafes():
    with app.app_context():
        all_cafes = db.session.query(Cafe).all()
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
        db.session.commit()

@app.route("/search", methods=["GET"])
def search():
    with app.app_context():
        loc = request.args.get('loc').title()
        all_cafes = Cafe.query.filter_by(location=loc).all()
        if not all_cafes:
            return jsonify(error={'Not Found':"Sorry, we don't have a cafe at that location."})
        else:
            return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/add", methods=["POST"])
def add_cafe():
    with app.app_context():
        new_cafe = Cafe(
                        name=request.form.get('name'),
                        map_url=request.form.get('map_url'),
                        img_url=request.form.get('img_url'),
                        location=request.form.get('location'),
                        has_sockets=bool(request.form.get('has_sockets')),
                        has_toilet=bool(request.form.get('has_toilet')),
                        has_wifi=bool(request.form.get('has_wifi')),
                        can_take_calls=bool(request.form.get('can_take_calls')),
                        seats=request.form.get('seats'),
                        coffee_price=f"£{request.form.get('coffee_price')}"
                        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(respose={'success':'Successfully added the new Cafe'})

@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    with app.app_context():
        cafe = Cafe.query.get(cafe_id)
        if not cafe:
            return jsonify(error={'Not Found': 'Sorry, a cafe with that id was not found in the database'})
        new_price = request.args.get('new_price')
        cafe.coffee_price = f"£{new_price}"
        db.session.commit()
        return jsonify(response={'success':'Successfully updated the price'})

@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def deleteCafe(cafe_id):
    with app.app_context():
        cafe = Cafe.query.get(cafe_id)
        if not cafe:
            return jsonify(error={'Not Found':'Sorry, a cafe with that id was not found in the database'}), 404
        api_key = request.args.get('api_key')
        if api_key != "mz050607":
            return jsonify(error={'Forbidden':"Sorry, that's not allowed. Make sure you have the correct api_key"}), 403
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={'success':"Successfully deleted the cafe from the database."}), 200
    

## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
