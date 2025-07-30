from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
     
image_domain = "http://localhost:8080"

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    qualification = db.Column(db.String)
    dob = db.Column(db.DateTime)    
    image_url = db.Column(db.String, default= image_domain+'/static/images/profiles/default.png') 
    role = db.Column(db.String, default='user')  

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'username': self.username,
            'qualification': self.qualification,
            'dob': self.dob.isoformat() if self.dob else None,
            'image_url': self.image_url,
            'role':self.role,
        }

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    image_url = db.Column(db.String, default= image_domain+'/static/images/subjects/default.png')  

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url
        }

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    
    subject = db.relationship('Subject', backref=db.backref('chapters', lazy=True))

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'subject': self.subject.to_json() if self.subject else None
        }    

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    title = db.Column(db.String)
    date_of_quiz = db.Column(db.DateTime)
    time_duration = db.Column(db.Integer)
    is_deleted = db.Column(db.Boolean, default=False)


    chapter = db.relationship('Chapter', backref=db.backref('quizzes', lazy=True))

    def to_json(self):
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'title': self.title,
            'date_of_quiz': self.date_of_quiz.isoformat() if self.date_of_quiz else None,
            'time_duration': self.time_duration,
            'is_deleted':self.is_deleted
        }

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    que_no = db.Column(db.Integer, nullable=False) 
    question_title=db.Column(db.String)
    question_statement = db.Column(db.String, nullable=False)
    option_1 = db.Column(db.String, nullable=False)
    option_2 = db.Column(db.String, nullable=False)
    option_3 = db.Column(db.String)
    option_4 = db.Column(db.String)
    selected_option = db.Column(db.String, nullable=True)
    correct_option = db.Column(db.String,nullable=False)

    quiz = db.relationship('Quiz', backref=db.backref('questions', lazy=True))

    def to_json(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'que_no':self.que_no,
            'question_title':self.question_title,
            'question_statement': self.question_statement,
            'option_1': self.option_1,
            'option_2': self.option_2,
            'option_3': self.option_3,
            'option_4': self.option_4,
            'selected_option':self.selected_option,
            'correct_option':self.correct_option
        }


class Scores(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id') ,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)
    marks_scored = db.Column(db.Integer)
    total_score = db.Column(db.Integer)
    submitted_at = db.Column(db.DateTime)

   
    quiz = db.relationship('Quiz', backref=db.backref('scores', lazy=True))
    user = db.relationship('User', backref=db.backref('scores', lazy=True))

    def to_json(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'time_stamp_of_attempt': self.time_stamp_of_attempt.isoformat() if self.time_stamp_of_attempt else None,
            'marks_scored': self.marks_scored,
            'total_score': self.total_score , 
            'submitted_at':self.submitted_at
        }

class UserAnswers(db.Model):
    __tablename__ = 'user_answers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option = db.Column(db.String, nullable=True)
    correct_option = db.Column(db.String, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)

    user = db.relationship('User', backref=db.backref('user_answers', lazy=True))
    quiz = db.relationship('Quiz', backref=db.backref('user_answers', lazy=True))
    question = db.relationship('Questions', backref=db.backref('user_answers', lazy=True))

    def to_json(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'selected_option': self.selected_option, 
            'correct_option': self.correct_option,
            'is_correct': self.is_correct
        }
