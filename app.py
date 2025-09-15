from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Student, Subject, Grade, Concession
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/student_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
db.init_app(app)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            # Al registrar el usuario, crea también el estudiante
            student = Student(id=new_user.id, name=username, document='', info='', photo=None)
            db.session.add(student)
            db.session.commit()
            flash('Usuario registrado. Inicia sesión.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            new_password = request.form['new_password']
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Contraseña actualizada. Puedes iniciar sesión.')
            return redirect(url_for('login'))
        else:
            flash('Usuario no encontrado.')
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.filter_by(id=session['user_id']).first()
    return render_template('dashboard.html', student=student)

@app.route('/student/<int:student_id>')
def student_info(student_id):
    student = Student.query.get_or_404(student_id)
    subjects = Subject.query.all()
    concessions = Concession.query.filter_by(student_id=student.id).all()
    return render_template('student_info', student=student, subjects=subjects, concessions=concessions)

@app.route('/update_photo/<int:student_id>', methods=['GET', 'POST'])
def update_photo(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        photo_file = request.files.get('photo')
        if photo_file and allowed_file(photo_file.filename):
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename.replace("\\", "/"))
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            photo_file.save(photo_path)
            student.photo = photo_filename
            db.session.commit()
            flash('Foto actualizada correctamente')
            return redirect(url_for('dashboard'))
    return render_template('update_photo.html', student=student)

@app.route('/add_grades/<int:student_id>/<int:subject_id>', methods=['GET', 'POST'])
def add_grades(student_id, subject_id):
    student = Student.query.get_or_404(student_id)
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        i = 1
        while True:
            value = request.form.get(f'value_{i}')
            percentage = request.form.get(f'percentage_{i}')
            if not value or not percentage:
                break
            grade = Grade(value=float(value), percentage=float(percentage), student_id=student_id, subject_id=subject_id)
            db.session.add(grade)
            i += 1
        db.session.commit()
        flash('Notas agregadas correctamente')
        return redirect(url_for('grades_calculation', student_id=student_id, subject_id=subject_id))
    return render_template('add_grades.html', student=student, subject=subject)

@app.route('/grades_calculation/<int:student_id>/<int:subject_id>')
def grades_calculation(student_id, subject_id):
    student = Student.query.get_or_404(student_id)
    subject = Subject.query.get_or_404(subject_id)
    grades = Grade.query.filter_by(student_id=student_id, subject_id=subject_id).all()
    total_grade = sum(g.value * g.percentage / 100 for g in grades)
    # Determinar rango
    if total_grade <= 60:
        rango = 'BJ'
        rango_text = 'Bajo'
    elif total_grade <= 70:
        rango = 'BS'
        rango_text = 'Básico'
    elif total_grade <= 89:
        rango = 'AL'
        rango_text = 'Alto'
    else:
        rango = 'SP'
        rango_text = 'Superior'
    return render_template('grades_calculation.html', student=student, subject=subject, grades=grades, total_grade=total_grade, rango=rango, rango_text=rango_text)

@app.route('/delete_grade/<int:grade_id>')
def delete_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    student_id = grade.student_id
    subject_id = grade.subject_id
    db.session.delete(grade)
    db.session.commit()
    return redirect(url_for('grades_calculation', student_id=student_id, subject_id=subject_id))

@app.route('/subjects')
def subjects():
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/add_subject', methods=['POST'])
def add_subject():
    name = request.form['name']
    new_subject = Subject(name=name)
    db.session.add(new_subject)
    db.session.commit()
    return redirect(url_for('subjects'))

@app.route('/delete_subject/<int:subject_id>')
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('subjects'))

@app.route('/add_concession/<int:student_id>', methods=['POST'])
def add_concession(student_id):
    description = request.form['description']
    new_concession = Concession(description=description, student_id=student_id)
    db.session.add(new_concession)
    db.session.commit()
    return redirect(url_for('student_info', student_id=student_id))

@app.route('/delete_concession/<int:concession_id>')
def delete_concession(concession_id):
    concession = Concession.query.get_or_404(concession_id)
    student_id = concession.student_id
    db.session.delete(concession)
    db.session.commit()
    return redirect(url_for('student_info', student_id=student_id))

if __name__ == '__main__':
    app.run(debug=True)