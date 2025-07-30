from flask import Flask,request,jsonify ,send_from_directory, send_file
from backend.models import User , Subject , Chapter , Quiz ,Questions,Scores
from flask_jwt_extended import create_access_token ,get_jwt,JWTManager
from flask_jwt_extended import jwt_required
from backend import app,db
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta
import os,csv
from flask_socketio import SocketIO
from backend.cache import cache
from threading import Thread
from werkzeug.security import check_password_hash

jwt_mgr = JWTManager() 
socketio = SocketIO(app, cors_allowed_origins="*")

os.makedirs("exports", exist_ok=True)
EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'exports')


UPLOAD_FOLDER = 'backend/static/images/subjects/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/static/images/subjects/<filename>')
def serve_subject_image(filename):
    full_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'subjects')
    return send_from_directory(full_path, filename)

blacklist = set()
@jwt_mgr.token_in_blocklist_loader
def check_if_token_is_blacklisted(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist

@jwt_mgr.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token has expired"}), 401

@jwt_mgr.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"msg": "Invalid token"}), 401

@jwt_mgr.unauthorized_loader
def unauthorized_callback(reason):
    return jsonify({"msg": "Missing token"}), 401

@app.route("/")
def home():
    return"home"

@app.route("/admin_login", methods=["POST"])
def admin_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    admin_from_db = User.query.filter_by(email=email, role="admin").first()

    if not admin_from_db:
        return {"message": "Admin email incorrect"}, 400

    if not check_password_hash(admin_from_db.password, password):
        return {"message": "Password incorrect"}, 400

    token = create_access_token(
        identity=email,
        additional_claims={"type": "admin", "id": admin_from_db.id}
    )
    return {"access_token": token}, 200

@cache.cached(timeout=50, key_prefix=lambda: f"user:{get_jwt_identity()}")
@app.route("/admin_dashboard",methods=["GET"])
# @cache.memoize(timeout=50)
@jwt_required()
def admin_dashboard():
    print("Executing admin_dashboard logic")

    subjects=Subject.query.all()
    json_response=[]
    for subject in subjects:
        json_response.append(subject.to_json())
    return {"subjects":json_response}
  
@app.route("/admin/subject/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_subject_details(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found"}), 404

    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    
    result = []
    for chapter in chapters:
        quizzes = Quiz.query.filter_by(chapter_id=chapter.id, is_deleted=False).all()

        result.append({
            **chapter.to_json(),
            "quiz_count": len(quizzes)
        })

    return jsonify({
        "subject": subject.to_json(),
        "chapters": result
    }), 200

@app.route("/subject_create", methods=["POST"])
@jwt_required()
def subject_create():
    data = request.form
    if "name" not in data or "description" not in data:
        return jsonify({"message": "Missing required fields"}), 400   

    name = data.get("name")
    description = data.get("description")

    existing_subject = Subject.query.filter_by(name=name).first()
    if existing_subject:
        return jsonify({"message": "Subject already exists"}), 400

    image_url = "/static/images/subjects/default.png"  
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            file.save(filepath)

            image_url = f"/static/images/subjects/{filename}"  

    subject = Subject(name=name, description=description, image_url=image_url)
    db.session.add(subject)
    db.session.commit()

    return jsonify({"message": "Subject created", "id": subject.id, "image_url": image_url}), 200

@app.route("/subject_update", methods=["POST"])
@jwt_required()
def subject_update():
    data = request.get_json()
    id = data["id"]
    name = data["name"]
    description = data["description"]

    subject = Subject.query.get(id)
    if not subject:
        return {"message": "Subject not found"}, 404

    subject.name = name
    subject.description = description
    db.session.commit()
    return {"message": "subject updated"}, 200

@app.route("/subject_delete/<int:subject_id>", methods=["DELETE"])
@jwt_required()
def subject_delete(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return {"message": "Subject doesn't exist"}, 404

    related_chapter_ids = db.session.query(Chapter.id).filter_by(subject_id=subject_id).all()
    related_chapter_ids = [chapter_id for (chapter_id,) in related_chapter_ids]

    Quiz.query.filter(Quiz.chapter_id.in_(related_chapter_ids)).delete(synchronize_session=False)
    db.session.commit()

    Chapter.query.filter(Chapter.id.in_(related_chapter_ids)).delete(synchronize_session=False)
    db.session.commit()

    db.session.delete(subject)
    db.session.commit()

    return {"message": "Subject, related chapters, and quizzes deleted"}, 200


@app.route("/chapter_create", methods=["POST"])
@jwt_required()
def chapter_create():
    data = request.get_json()
    name = data.get("name")
    description = data.get("description")
    subject_id = data.get("subject_id")  
    existing_chapter = db.session.query(Chapter).filter_by(name=name).first()
    if existing_chapter:
        return jsonify({"message": "Chapter already exists"}), 400
    if not subject_id:
        return jsonify({"error": "subject_id is required"}), 400

    new_chapter = Chapter(name=name, description=description, subject_id=subject_id)

    db.session.add(new_chapter)
    db.session.commit()
    return jsonify({"message": "Chapter added successfully"}), 201    

@app.route("/chapter_update", methods=["POST"])
@jwt_required()
def chapter_update():
    data = request.get_json()
    id = data.get("id")
    name = data.get("name")
    description = data.get("description")
    subject_id = data.get("subject_id")  

    chapter = Chapter.query.get(id)
    
    if not chapter:
        return jsonify({"message": "Chapter not found"}), 404

    if subject_id:
        chapter.subject_id = subject_id  
    
    chapter.name = name
    chapter.description = description

    db.session.commit()
    return jsonify({"message": "Chapter updated successfully"}), 200

@app.route("/chapter_delete", methods=["POST"])
@jwt_required()
def chapter_delete():
    data = request.get_json()
    id = data.get("id")
    
    chapter = Chapter.query.get(id)
    
    if not chapter:
        return jsonify({"message": "Chapter doesn't exist"}), 400

    Quiz.query.filter_by(chapter_id=id).delete()

    db.session.delete(chapter)
    
    try:
        db.session.commit()
        return jsonify({"message": "Chapter deleted successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Error: Unable to delete chapter due to associated quizzes."}), 500
  
@app.route("/admin/subject/<int:subject_id>/chapter/<int:chapter_id>", methods=["GET"])
@cache.memoize(timeout=50)
@jwt_required()
def get_chapter_data(subject_id, chapter_id):
    subject = Subject.query.get(subject_id)
    chapter = Chapter.query.get(chapter_id)
    
    if not subject or not chapter:
        return jsonify({"error": "Subject or Chapter not found"}), 404

    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

    return jsonify({
        "subject": subject.to_json(),
        "chapter": chapter.to_json(),
        "quizzes": [quiz.to_json() for quiz in quizzes]
    })

@app.route("/admin/subject/<int:subject_id>/chapter/<int:chapter_id>/quiz/<int:quiz_id>", methods=["GET"])
@cache.memoize(timeout=50)
@jwt_required()
def get_quiz_with_questions(subject_id, chapter_id, quiz_id):
    subject = Subject.query.get(subject_id)
    chapter = Chapter.query.get(chapter_id)

    if not subject or not chapter:
        return jsonify({"error": "Subject or Chapter not found"}), 404

    quiz = Quiz.query.filter_by(id=quiz_id, chapter_id=chapter_id).first()
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    questions = Questions.query.filter_by(quiz_id=quiz.id).order_by(Questions.que_no.asc()).all()

    return jsonify({
        "subject": subject.to_json(),
        "chapter": chapter.to_json(),
        "quiz": quiz.to_json(),
        "questions": [q.to_json() for q in questions]
    })

@app.route("/quiz_create", methods=["POST"])
@jwt_required()
def create_quiz():
    data = request.json

    chapter_id = data.get('chapter_id')
    title = data.get('title', 'Untitled Quiz')
    date_of_quiz = data.get('date_of_quiz')
    duration = data.get('duration')

    if not chapter_id or not title or not date_of_quiz or not duration:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        if isinstance(duration, str) and ':' in duration:
            hours, minutes = map(int, duration.split(':'))
            duration = hours * 60 + minutes  
        elif isinstance(duration, int):
            duration = duration
        else:
            return jsonify({"error": "Invalid duration format"}), 400
    except ValueError:
        return jsonify({"error": "Invalid duration format"}), 400

    new_quiz = Quiz(
        chapter_id=chapter_id,
        title=title,
        date_of_quiz=datetime.strptime(date_of_quiz, '%Y-%m-%d').date(),
        time_duration=duration
    )

    db.session.add(new_quiz)
    db.session.commit()

    return jsonify(new_quiz.to_json()), 201

@app.route("/question_create", methods=["POST"])
@jwt_required()
def create_question():
    data = request.json
    new_question = Questions(
        quiz_id=data['quiz_id'],
        que_no=data['que_no'],
        question_title=data['question_title'],
        question_statement=data['question_statement'],
        option_1=data['option_1'],
        option_2=data['option_2'],
        option_3=data.get('option_3'),
        option_4=data.get('option_4'),
        correct_option=data['correct_option']
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify(new_question.to_json()), 201

@app.route("/quiz_update/<int:quiz_id>", methods=["PUT"])
@jwt_required()
def update_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.json
    
    quiz.title = data.get('title', quiz.title)

    if 'date_of_quiz' in data:
        try:
            quiz.date_of_quiz = datetime.fromisoformat(data['date_of_quiz']).date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD or ISO 8601 format."}), 400

    if 'time_duration' in data:
        time_duration = data['time_duration']
        if isinstance(time_duration, str) and ':' in time_duration:
            try:
                hours, minutes = map(int, time_duration.split(':'))
                quiz.time_duration = hours * 60 + minutes
            except ValueError:
                return jsonify({"error": "Invalid duration format. Use HH:MM."}), 400
        else:
            try:
                quiz.time_duration = int(time_duration)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid time duration. Use numeric values."}), 400

    db.session.commit()
    return jsonify(quiz.to_json()), 200

@app.route("/quiz_delete/<int:quiz_id>", methods=["DELETE"])
@jwt_required()
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.scores:
        quiz.is_deleted = True
        try:
            db.session.commit()
            return jsonify({"message": "Quiz soft-deleted (has scores)."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to soft-delete: {str(e)}"}), 500

    try:
        Questions.query.filter_by(quiz_id=quiz.id).delete()
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({"message": "Quiz hard-deleted (no scores)."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to hard-delete: {str(e)}"}), 500
 
@app.route("/question_update/<int:question_id>", methods=["PUT"])
@jwt_required()
def update_question(question_id):
    data = request.json
    question = Questions.query.get_or_404(question_id)
    
    question.que_no = data.get('que_no', question.que_no)
    question.question_title = data.get('question_title', question.question_title)
    question.question_statement = data.get('question_statement', question.question_statement)
    question.option_1 = data.get('option_1', question.option_1)
    question.option_2 = data.get('option_2', question.option_2)
    question.option_3 = data.get('option_3', question.option_3)
    question.option_4 = data.get('option_4', question.option_4)
    question.correct_option = data.get('correct_option', question.correct_option)
    
    db.session.commit()
    return jsonify(question.to_json()), 200

@app.route("/question_delete/<int:question_id>", methods=["DELETE"])
@jwt_required()
def delete_question(question_id):
    question = Questions.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Question deleted successfully"}), 200

@app.route('/search_subjects', methods=['GET'])
@jwt_required()
def search_subjects():
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify({'message': 'Search query cannot be empty'}), 400

    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    
    if not subjects:
        return jsonify({'message': 'No matching subjects found'}), 404
    
    data = []
    for sub in subjects:
        total_quizzes = sum(len(chapter.quizzes) for chapter in sub.chapters if chapter.quizzes)
        
        data.append({
            'id': sub.id,
            'name': sub.name,
            'description': sub.description,
            'image_url': sub.image_url,
            'chapters': len(sub.chapters),
            'quizzes': total_quizzes
        })
    
    return jsonify({'subjects': data}), 200

@app.route('/admin/quiz_mgmt', methods=['GET'])
@cache.memoize(timeout=50)
@jwt_required()
def get_quizzes():
    try:
        quizzes = Quiz.query.all()
        data = []
        for quiz in quizzes:
            chapter = quiz.chapter
            subject = chapter.subject
            data.append({
                'id': quiz.id,
                'title': quiz.title,
                'subject_id': subject.id,
                'subject_name': subject.name,    
                'chapter_id': chapter.id,
                'chapter_name': chapter.name,    
            })
        return jsonify({'quizzes': data}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch quizzes'}), 500

@app.route('/search_quizzes', methods=['GET'])
@jwt_required()
def search_quizzes():
    query = request.args.get('query', '').strip()
    
    if not query:
        return jsonify({'message': 'Search query cannot be empty'}), 400

    quizzes = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()
    
    if not quizzes:
        return jsonify({'message': 'No matching quizzes found'}), 404
    
    data = []
    for quiz in quizzes:
        chapter = quiz.chapter
        subject = chapter.subject
        data.append({
            'id': quiz.id,
            'title': quiz.title,
            'subject_id': subject.id,
            'subject_name': subject.name,      
            'chapter_id': chapter.id,
            'chapter_name': chapter.name        
        })
    
    return jsonify({'quizzes': data}), 200

@app.route('/admin/chapters', methods=['GET'])
@jwt_required()
def get_chapters():
    try:
        chapters = Chapter.query.all()
        data = []
        for ch in chapters:
            data.append({
                'id': ch.id,
                'name': ch.name,
                'description': ch.description,
                'subject_id': ch.subject.id,
                'subject_name': ch.subject.name
            })
        return jsonify({'chapters': data}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch chapters'}), 500
    
@app.route('/admin/chapters/search', methods=['GET'])
@jwt_required()
def search_chapters():
    query = request.args.get('query', '').strip().lower()
    
    if not query:
        return jsonify({'chapters': []}), 200

    chapters = Chapter.query.join(Subject).filter(
        db.or_(
            Chapter.name.ilike(f"%{query}%"),
            Subject.name.ilike(f"%{query}%")
        )
    ).all()

    data = []
    for chapter in chapters:
        data.append({
            'id': chapter.id,
            'name': chapter.name,
            'description': chapter.description,
            'subject_id': chapter.subject.id,
            'subject_name': chapter.subject.name
        })

    return jsonify({'chapters': data}), 200

@app.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        users = User.query.all()
        result = []

        for user in users:
            user_data = user.to_json()
            scores = []
            total_marks = 0
            total_max = 0

            if user.image_url:
                user_data['image_url'] = f"http://127.0.0.1:8080{user.image_url}"
            else:
                user_data['image_url'] = "http://127.0.0.1:8080/static/images/profile/default.png"

            for score in user.scores:
                quiz = score.quiz
                if not quiz or not quiz.chapter or not quiz.chapter.subject:
                    continue  

                chapter = quiz.chapter
                subject = chapter.subject

                total_marks += score.marks_scored
                total_max += score.total_score

                scores.append({
                    'quiz_id': quiz.id,
                    'quiz_title': quiz.title,
                    'chapter': chapter.name,
                    'subject': subject.name,
                    'marks_scored': score.marks_scored,
                    'total_score': score.total_score,
                    'attempted_on': score.time_stamp_of_attempt.isoformat()
                })

            user_data['scores'] = scores
            user_data['user_id'] = user.id
            user_data['total_attempts'] = len(scores)
            user_data['average_score'] = round((total_marks / total_max) * 100, 2) if total_max > 0 else 0.0

            result.append(user_data)

        return jsonify({'users': result}), 200

    except Exception as e:
        print("Error in /admin/users:", e)  
        return jsonify({'message': 'Failed to fetch users'}), 500

@app.route('/admin/export_users_csv', methods=['POST'])
@jwt_required()
def export_users_csv():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exported_users_{now}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)  

    def generate_csv_with_context():
        with app.app_context():  
            try:
                users = User.query.all()
                with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["User ID", "Username", "Email", "Qualification", "DOB", "Total Attempts", "Average Score (%)"])
                    for user in users:
                        total_attempts = len(user.scores)
                        total_marks = sum(s.marks_scored for s in user.scores)
                        total_score = sum(s.total_score for s in user.scores)
                        avg_score = round((total_marks / total_score) * 100, 2) if total_score > 0 else 0.0
                        writer.writerow([
                            user.id,
                            user.username,
                            user.email,
                            user.qualification or "N/A",
                            user.dob.strftime("%Y-%m-%d") if user.dob else "N/A",
                            total_attempts,
                            avg_score
                        ])
                print(f"[CSV EXPORT COMPLETE] {filename}")
                socketio.emit('csv_ready', {'filename': filename})
            except Exception as e:
                print("[CSV EXPORT ERROR]", e)

    Thread(target=generate_csv_with_context).start()
    return jsonify({"message": "CSV export started"}), 202

@app.route('/exports/<filename>')
def download_export(filename):
    full_path = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(full_path):
        return "File not found", 404
    return send_file(full_path, as_attachment=True)

@app.route("/admin/summary", methods=["GET"])
@jwt_required()
def admin_summary():
    from sqlalchemy.sql import func

    users = User.query.all()
    quizzes = Quiz.query.all()
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    scores = Scores.query.all()

    qualifications = {}
    for user in users:
        q = user.qualification or "N/A"
        qualifications[q] = qualifications.get(q, 0) + 1

    quiz_per_subject = {}
    for quiz in quizzes:
        if quiz.chapter and quiz.chapter.subject:
            subject_name = quiz.chapter.subject.name
            quiz_per_subject[subject_name] = quiz_per_subject.get(subject_name, 0) + 1

    avg_score_subject = {}
    count_per_subject = {}
    for score in scores:
        if score.quiz and score.quiz.chapter and score.quiz.chapter.subject:
            subject_name = score.quiz.chapter.subject.name
            avg_score_subject[subject_name] = avg_score_subject.get(subject_name, 0) + score.marks_scored
            count_per_subject[subject_name] = count_per_subject.get(subject_name, 0) + score.total_score

    avg_score_subject = {
        sub: round((avg_score_subject[sub] / count_per_subject[sub]) * 100, 2)
        for sub in avg_score_subject
        if count_per_subject[sub] > 0
    }

    user_vs_avg = []
    for user in users:
        total = sum(score.total_score for score in user.scores if score.quiz)
        obtained = sum(score.marks_scored for score in user.scores if score.quiz)
        avg = round((obtained / total) * 100, 2) if total else 0
        user_vs_avg.append({"username": user.username, "avg_score": avg})

    quiz_per_chapter = {}
    for chapter in chapters:
        quiz_per_chapter[chapter.name] = len(chapter.quizzes)

    subject_attempts = {}
    for score in scores:
        if score.quiz and score.quiz.chapter and score.quiz.chapter.subject:
            sub = score.quiz.chapter.subject.name
            subject_attempts[sub] = subject_attempts.get(sub, 0) + 1

    return jsonify({
        "qualifications": qualifications,
        "quiz_per_subject": quiz_per_subject,
        "avg_score_subject": avg_score_subject,
        "user_vs_avg": user_vs_avg,
        "quiz_per_chapter": quiz_per_chapter,
        "subject_attempts": subject_attempts
    }), 200

@app.route("/admin_logout", methods=["POST"])
@jwt_required()
def admin_logout():
    jti = get_jwt()["jti"]
    blacklist.add(jti) 
    return jsonify({"msg": "Admin logged out successfully"}), 200              


if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
