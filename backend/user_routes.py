from flask import Flask, request, jsonify ,json,send_from_directory, send_file
from backend.models import User, Subject, Chapter, Quiz, Questions, Scores , UserAnswers
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, JWTManager,get_jwt_identity
from backend import app, db
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload
from datetime import datetime
import os
from datetime import datetime
from backend.cache import cache
from werkzeug.security import check_password_hash, generate_password_hash

os.makedirs("exports", exist_ok=True)
EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'exports')

UPLOAD_FOLDER = 'backend/static/images/profile/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/static/images/profile/<filename>')
def serve_profile_image(filename):
    full_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'profile')
    return send_from_directory(full_path, filename)
jwt_mgr = JWTManager(app) 

@jwt_mgr.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token has expired"}), 401

@jwt_mgr.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"msg": "Invalid token"}), 401

@jwt_mgr.unauthorized_loader
def unauthorized_callback(reason):
    return jsonify({"msg": "Missing token"}), 401

@app.route("/user_login", methods=["POST"])
def user_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email, role="user").first()

    if not user:
        return {"message": "User email incorrect"}, 400

    try:
        if check_password_hash(user.password, password):
            pass
        else:
            return {"message": "Password incorrect"}, 400
    except ValueError:
        if user.password == password:
            user.password = generate_password_hash(password)
            db.session.commit()
        else:
            return {"message": "Password incorrect"}, 400

    token = create_access_token(
        identity=email,
        additional_claims={"type": "user", "id": user.id}
    )

    return {"access_token": token}, 200

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    username = request.form.get('username')
    qualification = request.form.get('qualification')
    dob = request.form.get('dob')
    role = request.form.get('role', 'user')
   
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already in use'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400

    dob_obj = datetime.strptime(dob, '%Y-%m-%d') if dob else None

    new_user = User(
        email=email,
        password=generate_password_hash(password),
        username=username,
        qualification=qualification,
        dob=dob_obj,
        role=role
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201

@app.route("/user_dashboard", methods=["GET"])
@cache.memoize(timeout=10)
@jwt_required()
def user_dashboard():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user_id = user.id

    quizzes = Quiz.query.options(
        joinedload(Quiz.chapter).joinedload(Chapter.subject),
        joinedload(Quiz.questions)
    ).filter_by(is_deleted=False).all()

    all_scores = Scores.query.filter_by(user_id=user_id).filter(Scores.submitted_at.isnot(None)).all()
    attempted_quiz_ids = {score.quiz_id for score in all_scores}

    upcoming_quizzes = []

    for quiz in quizzes:
        if quiz.id in attempted_quiz_ids:
            continue
        if not quiz.date_of_quiz or quiz.date_of_quiz < datetime.now():
            continue
        if not quiz.chapter or not quiz.chapter.subject:
            continue

        upcoming_quizzes.append({
            "id": quiz.id,
            "title": quiz.title,
            "date": quiz.date_of_quiz.isoformat(),
            "duration": quiz.time_duration,
            "chapter_name": quiz.chapter.name,
            "subject_name": quiz.chapter.subject.name,
            "num_questions": len(quiz.questions)
        })

    return jsonify({
        "user": user.to_json(),
        "upcoming_quizzes": upcoming_quizzes
    })

@app.route("/user/quiz/<int:quiz_id>/questions", methods=["GET"])
@jwt_required()
def get_quiz_questions(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"message": "Quiz not found"}), 404

    questions = quiz.questions
    return jsonify([q.to_json() for q in questions]), 200

@app.route('/user/scores/<int:quiz_id>', methods=['GET'])
@cache.memoize(timeout=60)
@jwt_required()
def get_user_score(quiz_id):
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user_id = user.id

    score = Scores.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()
    if not score:
        return jsonify({"message": "Score not found"}), 404

    user_answers = UserAnswers.query.filter_by(user_id=user_id, quiz_id=quiz_id).all()
    answers_by_qid = {ua.question_id: ua for ua in user_answers}

    quiz = Quiz.query.get(quiz_id)
    questions = Questions.query.filter_by(quiz_id=quiz_id).order_by(Questions.que_no).all()

    questions_json = []
    for q in questions:
        ua = answers_by_qid.get(q.id)
    questions_json.append({
    'id': q.id,
    'question_title': q.question_title,
    'question_statement': q.question_statement,
    'option_1': q.option_1,
    'option_2': q.option_2,
    'option_3': q.option_3,
    'option_4': q.option_4,
    'correct_option': str(q.correct_option).replace("option_", "") if q.correct_option else None,
    'selected_option': str(ua.selected_option).replace("option_", "") if ua and ua.selected_option else None,
    'is_correct': ua.is_correct if ua else False
})

    return jsonify({
        "quiz": {
            "subjectId": quiz.chapter.subject.id if quiz.chapter and quiz.chapter.subject else None,
            "subjectName": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "N/A",
            "chapterId": quiz.chapter.id if quiz.chapter else None,
            "chapterName": quiz.chapter.name if quiz.chapter else "N/A",
            "id": quiz.id,
            "name": quiz.title,
            "duration": quiz.time_duration
        },
        "attempted": True,
        "marksScored": score.marks_scored,
        "totalScore": score.total_score,
        "submitted_at": score.submitted_at.isoformat() if score.submitted_at else None,
        "questions": questions_json,
        "questionsRight": score.marks_scored,
        "questionsUnattempted": score.total_score - score.marks_scored
    }), 200

@app.route("/user/quiz/<int:quiz_id>/submit", methods=["POST"])
@jwt_required()
def submit_quiz_answers(quiz_id):
    email = get_jwt_identity()
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user_id = user.id
    data = request.json

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"message": "Quiz not found"}), 404

    existing_score = Scores.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()
    if existing_score:
        return jsonify({
            "message": "You already submitted this quiz",
            "score": existing_score.marks_scored,
            "total": existing_score.total_score
    }), 200

    all_questions = {q.id: q for q in quiz.questions}
    total_questions = len(all_questions)
    correct_count = 0
    user_answers_to_save = []

    submitted_answers = {
        item['question_id']: item.get('selected_option')
        for item in data
    }

    for question_id, question in all_questions.items():
        selected = str(submitted_answers.get(question_id)) if submitted_answers.get(question_id) is not None else None
        correct = question.correct_option
        is_correct = (selected == correct) if selected is not None else False

        if is_correct:
            correct_count += 1

        user_answers_to_save.append(UserAnswers(
            user_id=user_id,
            quiz_id=quiz_id,
            question_id=question_id,
            selected_option=selected,
            correct_option=correct,
            is_correct=is_correct
        ))

    db.session.bulk_save_objects(user_answers_to_save)

    score_entry = Scores(
        quiz_id=quiz_id,
        user_id=user_id,
        marks_scored=correct_count,
        total_score=total_questions,
        submitted_at=datetime.utcnow()  
    )
    db.session.add(score_entry)
    db.session.commit()

    return jsonify({
        "message": "Quiz submitted successfully",
        "score": correct_count,
        "total": total_questions
    }), 200

@app.route("/user/all_quizzes", methods=["GET"])
@jwt_required()
def get_all_quizzes():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user_id = user.id

    all_quizzes = Quiz.query.all()
    user_attempted = Scores.query.filter_by(user_id=user_id).all()
    attempted_quiz_ids = [s.quiz_id for s in user_attempted]

    quiz_list = []
    now = datetime.now()

    for quiz in all_quizzes:

        score = next((s for s in user_attempted if s.quiz_id == quiz.id), None)
        submitted_at = score.submitted_at if score else None

        if score and score.submitted_at:
            status = "Attempted"
        elif score and not score.submitted_at:
            status = "In Progress"
        elif quiz.date_of_quiz and quiz.date_of_quiz < now:
            status = "Missed"
        else:
            status = "Unattempted"

        subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "N/A"
        chapter_name = quiz.chapter.name if quiz.chapter else "N/A"

        quiz_list.append({
            "id": quiz.id,
            "title": quiz.title,
            "time_duration": quiz.time_duration,
            "date_of_quiz": quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            "submitted_at": submitted_at.isoformat() if submitted_at else None,
            "status": status,
            "subject": subject_name,
            "chapter": chapter_name
        })

    return jsonify({"quizzes": quiz_list})

@app.route("/user/subjects", methods=["GET"])
@cache.memoize(timeout=60)
@jwt_required()
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([s.to_json() for s in subjects]),200

@app.route("/user/subject/<int:subject_id>/chapters", methods=["GET"])
@cache.memoize(timeout=60)
@jwt_required()
def get_subject_chapters(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({"message": "Subject not found"}), 404

    chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    return jsonify({
        "subjectname": subject.name,   
        "chapters": [
            {
                "id": chapter.id,
                "title": chapter.name,
                "description": chapter.description
            } for chapter in chapters
        ]
    })

@app.route("/user/subject/<int:subject_id>/chapter/<int:chapter_id>/quizzes", methods=["GET"])
@jwt_required()
def get_chapter_quizzes(subject_id, chapter_id):
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user_id = user.id

    chapter = Chapter.query.get(chapter_id)
    if not chapter or chapter.subject_id != subject_id:
        return jsonify({"message": "Chapter not found"}), 404

    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    user_scores = Scores.query.filter_by(user_id=user_id).all()
    score_map = {score.quiz_id: score for score in user_scores}

    quiz_list = []
    now = datetime.utcnow()

    for quiz in quizzes:
        score = score_map.get(quiz.id)
        submitted_at = score.submitted_at if score else None

        if score and submitted_at:
            status = "Attempted"
        elif score and not submitted_at:
            status = "In Progress"
        elif quiz.date_of_quiz and quiz.date_of_quiz < now:
            status = "Missed"
        else:
            status = "Unattempted"

        quiz_list.append({
            "id": quiz.id,
            "title": quiz.title,
            "time_duration": quiz.time_duration,
            "date_of_quiz": quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            "submitted_at": submitted_at.isoformat() if submitted_at else None,
            "status": status
        })

    return jsonify({
        "chapter_name": chapter.name,
        "quizzes": quiz_list
    })

@app.route('/user/missed_scores/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_missed_quiz(quiz_id):
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user_id = user.id
    score = Scores.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()

    if score:
        return jsonify({"attempted": True}), 200

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"message": "Quiz not found"}), 404

    questions = Questions.query.filter_by(quiz_id=quiz_id).order_by(Questions.que_no).all()

    questions_json = []
    for q in questions:
        questions_json.append({
            'id': q.id,
            'text': q.question_statement,
            'options': {
                'A': q.option_1,
                'B': q.option_2,
                'C': q.option_3,
                'D': q.option_4
            },
            'correctOption': q.correct_option 
        })

    return jsonify({
        "quiz": {
            "subjectId": quiz.chapter.subject.id if quiz.chapter and quiz.chapter.subject else None,
            "subjectName": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "N/A",
            "chapterId": quiz.chapter.id if quiz.chapter else None,
            "chapterName": quiz.chapter.name if quiz.chapter else "N/A",
            "id": quiz.id,
            "name": quiz.title,
            "duration": quiz.time_duration
        },
        "attempted": False,
        "questions": questions_json
    }), 200

@app.route("/user/summary", methods=["GET"])
@jwt_required()
def get_user_summary():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    scores = Scores.query.filter_by(user_id=user.id).all()
    attempted_quiz_ids = {s.quiz_id for s in scores}

    all_quizzes = Quiz.query.filter_by(is_deleted=False).all()
    
    data = []
    attempted = 0
    missed = 0
    unattempted = 0

    for quiz in all_quizzes:
        quiz_data = {
            "quiz_id": quiz.id,
            "quiz_title": quiz.title or "Untitled",
            "subject": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "Unknown",
            "time_duration": (quiz.time_duration or 0) * 60
        }

        if quiz.id in attempted_quiz_ids:
            score = next((s for s in scores if s.quiz_id == quiz.id), None)
            quiz_data.update({
                "marks_scored": score.marks_scored,
                "total_score": score.total_score or 100,
                "timestamp": score.time_stamp_of_attempt.strftime("%Y-%m-%d %H:%M:%S") if score.time_stamp_of_attempt else "Unknown"
            })
            data.append(quiz_data)
            attempted += 1
        elif quiz.date_of_quiz and quiz.date_of_quiz < datetime.utcnow():
            missed += 1
        else:
            unattempted += 1

    return jsonify({
        "scores": data,
        "summary": {
            "attempted": attempted,
            "missed": missed,
            "unattempted": unattempted
        }
    })

@app.route("/user/profile", methods=["GET"])
@jwt_required()
def user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"user": user.to_json()})

@app.route('/user/update_profile', methods=['POST'])
@jwt_required()
def update_profile():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    new_email = data.get('email', user.email)

    if new_email != user.email:
        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user:
            return jsonify({"message": "Email already in use by another account."}), 400
        user.email = new_email

    user.qualification = data.get('qualification', user.qualification)

    dob_str = data.get('dob')
    if dob_str:
        try:
            user.dob = datetime.strptime(dob_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    db.session.commit()
    return jsonify({"message": "Profile updated successfully."})

@app.route("/user/upload_profile_image", methods=["POST"])
@jwt_required()
def upload_profile_image():
    if 'image' not in request.files:
        return jsonify({"msg": "No image part in the request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"msg": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user.image_url = f"/static/images/profile/{filename}"  
    db.session.commit()

    return jsonify({
        "message": "Image uploaded successfully.",
        "image_url": user.image_url  
    }), 200

@app.route('/user/change_password', methods=['POST'])
@jwt_required()
def change_password():
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not check_password_hash(user.password, old_password):
        return jsonify({"message": "Old password is incorrect"}), 400

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password changed successfully."})
