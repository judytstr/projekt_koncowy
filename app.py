from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Ensure the directory for the database file exists
if not os.path.exists('C:\\Users\\judyt\\PycharmProjects\\projekt_koncowy_SQL'):
    os.makedirs('C:\\Users\\judyt\\PycharmProjects\\projekt_koncowy_SQL')

app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\judyt\\PycharmProjects\\projekt_koncowy_SQL\\mood_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    cycle_length = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(500), nullable=False)


def is_within_7_days(cycle_length, last_period_date):
    today = datetime.now().date()
    next_period_date = last_period_date + timedelta(days=cycle_length)
    return (next_period_date - today).days <= 7


def get_yes_no(answer):
    return answer.lower() == 'tak'


def evaluate_emotions(within_7_days, answers):
    partner_issues = any(answers[:5])
    other_factors = any(answers[5:8])
    sleep_and_hunger = not answers[6] or answers[7]

    if partner_issues:
        if not sleep_and_hunger:
            if within_7_days:
                return ("Być może Twoje zdenerwowanie jest zasadne, jednak weź "
                        "pod uwagę, że hormony mogą je bardzo potęgować.")
            else:
                return (
                    "Jak najbardziej Twoje zdenerwowanie jest zasadne, to nie"
                    " jest wina hormonów ani innych czynników.")
        else:
            if within_7_days:
                return ("Być może Twoje zdenerwowanie jest zasadne, jednak weź "
                        "pod uwagę, że hormony (Twoja miesiączka jest już bardzo"
                        " blisko!) ale także inne czynniki, takie jak niewyspanie,"
                        " stres w pracy, a także głód mogą potęgować Twoje zdenerwowanie.")
            else:
                return (
                    "Twoje zdenerwowanie jest jak najbardziej zasadne. Hormony "
                    "nie mają na nie wpływu, jednak inne czynniki, takie jak niewyspanie,"
                    " stres w pracy, a także głód mogą je potęgować.")
    else:
        if not sleep_and_hunger:
            if within_7_days:
                return ("Twoje zdenerwowanie może nie być do końca zasadne, "
                        "wygląda na to, że hormony bardzo potęgują Twoje"
                        " emocje. Miesiączka jest już blisko!")
            else:
                return ("Wygląda na to, że nie masz powodów do zdenerwowania.")
        else:
            if within_7_days:
                return ("Najprawdopodobniej nie masz powodu, by denerwować na "
                        "swojego partnera. Twoja irytacja może wynikać z faktu, "
                        "że Twoja miesiączka jest już bardzo blisko, a potęgować"
                        " mogą ją inne czynniki, takie jak stres w pracy, "
                        "niewyspanie czy głód.")
            else:
                return ("Wygląda na to, że nie masz powodów do zdenerwowania, "
                        "jednak inne czynniki, takie jak niewyspanie, stres w pracy,"
                        " a także głód mogą potęgować Twoje zdenerwowanie.")


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        cycle_length = int(request.form["cycle_length"])
        last_period_date = datetime.strptime(request.form["last_period_date"],
                                             "%d-%m-%Y").date()
        within_7_days = is_within_7_days(cycle_length, last_period_date)

        answers = [
            get_yes_no(request.form["q1"]),
            get_yes_no(request.form["q2"]),
            get_yes_no(request.form["q3"]),
            get_yes_no(request.form["q4"]),
            get_yes_no(request.form["q5"]),
            get_yes_no(request.form["q6"]),
            get_yes_no(request.form["q7"]),
            get_yes_no(request.form["q8"])
        ]

        result = evaluate_emotions(within_7_days, answers)

        new_entry = MoodEntry(date=datetime.now().date(),
                              cycle_length=cycle_length, result=result)
        db.session.add(new_entry)
        db.session.commit()

        return render_template("result.html", result=result)

    return render_template("form.html")


@app.route("/history")
def history():
    entries = MoodEntry.query.order_by(MoodEntry.date.desc()).all()
    return render_template("history.html", entries=entries)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
