from flask import Flask, render_template, request, session, flash

import mysql.connector
import base64, os


from flask import Flask, render_template, request, jsonify



app = Flask(__name__)
app.config['SECRET_KEY'] = 'aaa'



@app.route("/")
def homepage():
    return render_template('index.html')




@app.route('/AdminLogin')
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route('/UserLogin')
def UserLogin():
    return render_template('UserLogin.html')


@app.route('/NewUser')
def NewUser():
    return render_template('NewUser.html')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1diaretinadb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb ")
            data = cur.fetchall()
            flash("you are successfully Login")
            return render_template('AdminHome.html', data=data)

        else:
            flash("UserName or Password Incorrect!")
            return render_template('AdminLogin.html')


@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1diaretinadb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb  ")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['uname']
        password = request.form['password']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1diaretinadb')
        cursor = conn.cursor()
        cursor.execute(
            "insert into regtb values('','" + name + "','" + mobile + "','" + email + "','" + address + "','" + username + "','" + password + "')")
        conn.commit()
        conn.close()
        flash("Record Saved!")

    return render_template('NewUser.html')


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['sname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='1diaretinadb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and password='" + password + "'")
        data = cursor.fetchone()
        if data is None:
            flash('Username or Password is wrong')
            return render_template('UserLogin.html', data=data)

        else:
            conn = mysql.connector.connect(user='root', password='', host='localhost', database='1diaretinadb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username + "' and password='" + password + "'")
            data = cur.fetchall()
            flash("you are successfully logged in")
            return render_template('UserHome.html', data=data)


@app.route('/UserHome')
def UserHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='1diaretinadb')
    cur = conn.cursor()
    cur.execute("SELECT username FROM regtb  where username='" + session['sname'] + "' ")
    data = cur.fetchall()
    return render_template('DoctorHome.html', data=data)


@app.route('/Predict')
def Predict():
    return render_template('Predict.html')


@app.route("/imupload", methods=['GET', 'POST'])
def imupload():
    if request.method == 'POST':
        import cv2
        file = request.files['file']
        file.save('static/Out/Test.jpg')
        org = 'static/Out/Test.jpg'

        from ultralytics import YOLO
        import cv2

        # image = cv2.imread(import_file_path)
        image = cv2.imread(org)
        model = YOLO('runs/detect/diabetic/weights/best.pt')

        class_labels = ['Mild', 'Moderate', 'No_DR', 'Proliferate_DR', 'Severe']

        # Perform object detection
        results = model(image, conf=0.1)

        confidences = results[0].boxes.conf  # Confidence scores
        class_indices = results[0].boxes.cls  # Class indices

        if len(confidences) > 0:
            max_confidence_index = confidences.argmax().item()  # Get index of highest confidence
            predicted_class_index = int(class_indices[max_confidence_index].item())  # Get correct class index

            # Ensure index is within bounds
            if 0 <= predicted_class_index < len(class_labels):
                predicted_class = class_labels[predicted_class_index]  # Map index to label
            else:
                predicted_class = "Unknown Class"

            confidence_score = confidences[max_confidence_index].item()  # Get highest confidence score

            print(f"Predicted Class: {predicted_class}")
            print(f"Confidence Score: {confidence_score:.4f}")  # Display with 4 decimal places
        else:
            predicted_class = "No Detections"
            confidence_score = 0.0
            print("No objects detected.")

        if predicted_class == 'Mild':
            res = "Eye Injections: Medications, like anti-VEGF drugs or corticosteroids, can be injected into the eye to reduce swelling and slow down the growth of new, abnormal blood vessels. "
        elif predicted_class == 'Moderate':
            res = "Blood Sugar Control: Strictly controlling blood sugar levels is crucial to slow down the progression of diabetic retinopathy. "
        elif predicted_class == 'No_DR':
            res = "Nil"
        elif predicted_class == 'Proliferate_DR':
            res = 'Laser Photocoagulation (PRP): This is the primary treatment for PDR, using a laser to create small burns on the retina, which cause the abnormal blood vessels to shrink and prevent further growth. '
        elif predicted_class == 'Severe':
            res = "Focal Laser Treatment: Used to treat DME, this involves applying laser burns to specific areas of the retina to seal off leaking blood vessels. "



        # Optionally, visualize the results
        annotated_frame = results[0].plot()
        outi = "static/Out/out.jpg"
        cv2.imwrite("static/Out/out.jpg", annotated_frame)

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)
        # cv2.waitKey(0)
        cv2.destroyAllWindows()

        return render_template('Predict.html', res=predicted_class, pre=res,outi=outi)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
