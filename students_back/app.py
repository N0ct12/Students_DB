from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123@localhost:5432/Students'  # Update with your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Define the models
class Students(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    marks = db.relationship('Marks', backref='student', cascade="all, delete-orphan", lazy=True)


class Marks(db.Model):
    __tablename__ = 'marks'
    id = db.Column(db.Integer, primary_key=True)
    students_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    math = db.Column(db.Integer)
    english = db.Column(db.Integer)
    algem = db.Column(db.Integer)


@app.route('/')
def index():
    students = db.session.query(Students.id, Students.name, Marks.math, Marks.english, Marks.algem).outerjoin(Marks,
                                                                                                              Students.id == Marks.students_id).all()
    return render_template('main_page.html', data=students)


@app.route('/add', methods=['GET', 'POST'])
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        math = request.form.get('math')
        english = request.form.get('english')
        algem = request.form.get('algem')

        # Create a new student
        new_student = Students(name=name)
        db.session.add(new_student)
        db.session.commit()

        # Add marks only if at least one subject has a grade
        if math or english or algem:
            new_marks = Marks(
                students_id=new_student.id,
                math=math if math else None,
                english=english if english else None,
                algem=algem if algem else None
            )
            db.session.add(new_marks)
            db.session.commit()

        return redirect('/')
    return render_template('add_student.html')


@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Students.query.get_or_404(student_id)
    marks = Marks.query.filter_by(students_id=student_id).first()

    if request.method == 'POST':
        # Update student name
        student.name = request.form['name']

        # Get grade data from form
        math = request.form.get('math')
        english = request.form.get('english')
        algem = request.form.get('algem')

        # Convert empty strings to None
        math = int(math) if math else None
        english = int(english) if english else None
        algem = int(algem) if algem else None

        # Update or create marks record
        if marks:
            marks.math = math
            marks.english = english
            marks.algem = algem
        else:
            marks = Marks(
                students_id=student_id,
                math=math,
                english=english,
                algem=algem
            )
            db.session.add(marks)

        # Commit changes to the database
        db.session.commit()

        return redirect('/')

    # Current grades for the form
    grades = {'math': marks.math if marks else '', 'english': marks.english if marks else '', 'algem': marks.algem if marks else ''}

    return render_template('edit_student.html', student=student, grades=grades)


@app.route('/delete/<int:student_id>', methods=['GET', 'POST'])
def delete(student_id):
    print(f"Accessing delete route for student_id: {student_id}")
    student = Students.query.get_or_404(student_id)
    marks = Marks.query.filter_by(students_id=student_id).first()

    if request.method == 'POST':
        scope = request.form.get('scope')
        subject = request.form.get('subject')  # Add this to handle specific subject deletion
        print(f"Received scope: {scope}")
        print(f"Received subject: {subject}")

        if scope == 'student':
            if student:
                db.session.delete(student)
                db.session.commit()  # Commit the deletion of the student
                print(f"Deleted student with id: {student_id}")
            else:
                print(f"Student with id: {student_id} not found")

        elif scope == 'marks':
            if marks:
                if subject:
                    if subject == 'math':
                        marks.math = None
                    elif subject == 'english':
                        marks.english = None
                    elif subject == 'algem':
                        marks.algem = None
                    print(f"Deleted {subject} mark for student with id: {student_id}")
                else:
                    marks.math = None
                    marks.english = None
                    marks.algem = None
                    print(f"Deleted all marks for student with id: {student_id}")
                db.session.commit()  # Commit the changes to the marks
            else:
                print(f"No marks found for student with id: {student_id}")

        return redirect('/')

    return render_template('delete_student.html', student=student, marks=marks)


if __name__ == '__main__':
    app.run(debug=True)
