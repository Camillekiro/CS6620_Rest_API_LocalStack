from flask import Flask, request, Blueprint
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
# config db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db.init_app(app)


class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    draft_pick_number = db.Column(db.String(255), nullable=False)
    pro_team_name = db.Column(db.String(255), nullable=False)
    player_name = db.Column(db.String(255), unique=True, nullable=False)
    amature_team_name = db.Column(db.String(255))

    def __repr__(self):
        return f"{self.draft_pick_number} - {self.pro_team_name} - {self.player_name} - {self.amature_team_name}"

#create API version blueprints
v1 = Blueprint('v1', __name__, url_prefix='/api/v1')
@v1.route('/')
def index():
    return "Hello World!"


@v1.route('/drafts')
def get_drafts():
    drafts = Draft.query.all()
    output = []
    for d in drafts:
        draft_data = {
            "pick_number": d.draft_pick_number,
            "pro_team": d.pro_team_name,
            "player_name": d.player_name,
            "amature_team": d.amature_team_name
        }
        output.append(draft_data)
    return {"draft_data": output}


@v1.route('/drafts/<id>')
def get_draft_record(id):
    draft_rec = db.get_or_404(Draft, id)
    return {
        "pick_number": draft_rec.draft_pick_number,
        "pro_team": draft_rec.pro_team_name,
        "player_name": draft_rec.player_name,
        "amature_team": draft_rec.amature_team_name
    }


@v1.route('/drafts', methods=['POST'])
def add_draft_record():
    draft_rec = Draft(draft_pick_number=request.json["pick_number"], 
                      pro_team_name=request.json["pro_team"], 
                      player_name=request.json["player_name"], 
                      amature_team_name=request.json["amature_team"])
    db.session.add(draft_rec)
    db.session.commit()
    return {"id": draft_rec.id}, 201


@v1.route('/drafts/<id>', methods=['DELETE'])
def delete_draft_record(id):
    draft_rec = db.get_or_404(Draft, id)
    if draft_rec is None:
        return {"message": "record not found"}, 404
    
    db.session.delete(draft_rec)
    db.session.commit()
    return {"message": "Successful Delete!"}, 200


@v1.route('/drafts/<id>', methods=['PUT'])
def update_draft_record(id):
    draft_rec = db.get_or_404(Draft, id)
    if not request.json:
        return {"error": "No JSON data provided"}, 400
    try:
        draft_rec.draft_pick_number = request.json["pick_number"] 
        draft_rec.pro_team_name = request.json["pro_team"]
        draft_rec.player_name = request.json["player_name"]
        draft_rec.amature_team_name = request.json["amature_team"]
        db.session.commit()
        return {"message": "Draft record updated succesfully"}, 200
    except KeyError as e:
        return {"error": f"missing requried field: {e}"}, 400
    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to update record"}, 500

#register the blueprint
app.register_blueprint(v1)
#root route for API info
@app.route('/')
def root():
    return{
        "message": "Draft API",
        "versions": {
            "v1": "/api/v1/"
        },
        "current_version": "1.0"
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)