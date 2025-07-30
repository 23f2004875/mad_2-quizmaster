from backend.workers import celery
from backend.models import db 
from celery.schedules import crontab
from backend.models import User,Scores,Quiz
from sqlalchemy import func
from backend.quiz_email_config import send_email
from datetime import datetime, timedelta 
from backend import models
User = models.User
import matplotlib.pyplot as plt
from io import BytesIO
import base64

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender,**kwargs):
    sender.add_periodic_task(
        # crontab(minute=0,hour=16),
        crontab(),
        daily_reminder.s(),
        name="daily reminder"
    )

    sender.add_periodic_task(
        crontab(0,0,day_of_month=1),
        monthly_report.s(),
        name="monthly report"
    )

@celery.task()
def daily_reminder():
    now = datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    new_quiz_exists = Quiz.query.filter(
        Quiz.date_of_quiz >= start_of_day,
        Quiz.is_deleted == False
    ).first() is not None

    users = User.query.all()
    for user in users:
        attempted_today = Scores.query.filter(
            Scores.user_id == user.id,
            Scores.time_stamp_of_attempt >= start_of_day
        ).first() is not None

        if new_quiz_exists or not attempted_today:
            subject = f"🔥 {user.username}, Ready to Conquer Today’s Quiz?"

            message = f"""
            <html>
            <head>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; color: #333; }}
                .container {{ max-width: 700px; margin: auto; background: #f9f9f9; padding: 20px; border-radius: 10px; }}
                .header {{ background: #28a745; color: white; padding: 15px; text-align: center; border-radius: 8px; }}
                ul {{ padding-left: 20px; }}
                .cta {{
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                .footer {{ font-size: 12px; color: gray; margin-top: 30px; text-align: center; }}
            </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🚀 Ready for Today's Challenge, {user.username}?</h2>
                    </div>

                    <p>We've got a new quiz lined up for you today – are you in?</p>
                    <p>Here's why you should take it:</p>
                    <ul>
                        <li>🧠 Sharpen your mind daily</li>
                        <li> 🔥 Today's Quiz is Live – Beat the Clock, {user.username}!</li>
                        <li>📈 A Smarter You Starts with One Click – Take the Quiz</li>
                        <li>👑 Only the Bold Win. Take Today’s Quiz and Dominate!li>
                    </ul>

                    <p style="text-align:center;">
                        <a href="http://localhost:8081/user_login" class="cta">🚀 Take the Quiz Now</a>
                    </p>

                    <div class="footer">
                        This is your daily reminder. Stay sharp, stay curious. 💡
                    </div>
                </div>
            </body>
            </html>
            """
            send_email(to=user.email, sub=subject, message=message)
            print(f"DAILY_REMINDER sent to {user.username}")

    return "DAILY_REMINDER SENT"


def generate_chart_image(x, y, title, xlabel, ylabel):
    plt.figure(figsize=(8, 4))
    plt.bar(x, y, color="#4CAF50")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{image_base64}"
@celery.task()
def monthly_report():
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO
    from collections import defaultdict
    from datetime import datetime
    from backend.models import db,User, Scores, Quiz, Chapter, Subject, UserAnswers
    from backend.quiz_email_config import send_email

    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    users = User.query.all()

    for user in users:
        scores = (
            db.session.query(
                Scores.marks_scored,
                Scores.total_score,
                Scores.time_stamp_of_attempt,
                Quiz.title.label('quiz_title'),
                Quiz.time_duration,
                Chapter.name.label('chapter_name'),
                Subject.name.label('subject_name')
                )
            .select_from(Scores)
            .join(Quiz, Scores.quiz_id == Quiz.id)
            .join(Chapter, Quiz.chapter_id == Chapter.id)
            .join(Subject, Chapter.subject_id == Subject.id)  
            .filter(
                Scores.user_id == user.id,
                Scores.time_stamp_of_attempt >= start_of_month
            )
            .all()
        )
        total_attempted = len(scores)
        if total_attempted == 0:
            continue

        category_scores = defaultdict(list)
        total_scored = 0
        total_possible = 0
        quiz_rows = ""

        for s in scores:
            percent = (s.marks_scored / s.total_score) * 100 if s.total_score else 0
            category_scores[s.subject_name].append(percent)
            total_scored += s.marks_scored
            total_possible += s.total_score

            quiz_rows += f"""
                <tr>
                    <td>{s.quiz_title}</td>
                    <td>{s.subject_name} / {s.chapter_name}</td>
                    <td>{percent:.2f}%</td>
                    <td>{s.time_stamp_of_attempt.strftime('%d %b %Y')}</td>
                    <td>{s.time_duration} mins</td>
                </tr>
            """

        average_score = (total_scored / total_possible) * 100 if total_possible else 0
        top_category = max(category_scores.items(), key=lambda x: sum(x[1])/len(x[1]))[0]

        total_answers = UserAnswers.query.filter_by(user_id=user.id).count()
        correct_answers = UserAnswers.query.filter_by(user_id=user.id, is_correct=True).count()
        incorrect_answers = total_answers - correct_answers

        subjects = list(category_scores.keys())
        avg_scores = [sum(v)/len(v) for v in category_scores.values()]

        plt.figure(figsize=(6, 3.5))
        bars = plt.bar(subjects, avg_scores, color="#4CAF50")
        plt.ylim(0, 100)
        plt.ylabel("Avg. Score (%)")
        plt.title("Performance by Subject")
        plt.xticks(rotation=20, ha='right')
        for bar, score in zip(bars, avg_scores):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{score:.0f}%", ha='center', fontsize=9)

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        subject = f"📊 {user.username}, Your Full Quiz Report for {datetime.utcnow():%B}!"

        message = f"""
        <html>
        <head>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; color: #333; }}
            .container {{ max-width: 750px; margin: auto; background: #f9f9f9; padding: 20px; border-radius: 10px; }}
            .header {{ background: #4CAF50; color: white; padding: 15px; text-align: center; border-radius: 8px; }}
            .profile-img {{
                width: 80px;
                height: 80px;
                border-radius: 50%;
                border: 3px solid #4CAF50;
                margin-bottom: 10px;
            }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
            th {{ background-color: #eee; }}
            .footer {{ font-size: 12px; color: gray; margin-top: 20px; text-align: center; }}
            .cta-button {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="header">
                <h2>Monthly Quiz Report</h2>
                <p>Hello, <strong>{user.username}</strong>!</p>
            </div>

            <p><strong>📅 Report for:</strong> {datetime.utcnow():%B %Y}</p>
            <p><strong>🎓 Qualification:</strong> {user.qualification or 'N/A'}</p>
            <p><strong>🎂 Date of Birth:</strong> {user.dob.strftime('%d %b %Y') if user.dob else 'N/A'}</p>

            <hr>

            <h3>📈 Performance Overview</h3>
            <ul>
                <li><strong>Total Quizzes Attempted:</strong> {total_attempted}</li>
                <li><strong>Average Score:</strong> {average_score:.2f}%</li>
                <li><strong>Best Category:</strong> {top_category}</li>
                <li><strong>Correct Answers:</strong> {correct_answers}</li>
                <li><strong>Incorrect Answers:</strong> {incorrect_answers}</li>
            </ul>

            <h3>📊 Subject-wise Performance</h3>
            <img src="data:image/png;base64,{chart_base64}" style="max-width:100%; border:1px solid #ccc; border-radius:8px;" alt="Performance Chart"/>

            <h3>📄 Quiz Attempts</h3>
            <table>
                <thead>
                    <tr>
                        <th>Quiz Title</th>
                        <th>Subject / Chapter</th>
                        <th>Score</th>
                        <th>Date</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
                    {quiz_rows}
                </tbody>
            </table>

            <p style="text-align: center;">
               <a href="http://localhost:8081/user_login" class="cta-button">
    ➕ Take Another Quiz
</a>

            </p>

            <div class="footer">
                🚀 Keep pushing your limits! This report was generated on {datetime.utcnow().strftime('%d %b %Y')}.
            </div>
        </div>
        </body>
        </html>
        """

        send_email(to=user.email, sub=subject, message=message)
        print(f"MONTHLY_REPORT sent to {user.username}")

    return "MONTHLY_REPORT with Chart"

