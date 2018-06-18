import os, csv
from flask import Flask, request, redirect, url_for, send_file, send_from_directory, render_template, make_response
from werkzeug.utils import secure_filename
from useFile import *
from exam_greedy import *
from course_schedule import *

UPLOAD_FOLDER = 'files_needed/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])
SAVE_PATH = ''
RES = ""
COURSE_RES = ""
used_colors_ = []
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# flag true if required file uploaded
ready4schedule = False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def checkFileExist(file_save_path, filename):
# add multiple conditions to check multiple file existence
    if os.path.exists(file_save_path + filename):
        return True
    else:
        return False

def generateSchedule(root_path, ebs_f, ecws_f, newExam=None, deleteExam=None):
    # if required files exist, proceed
    if checkFileExist(root_path, ebs_f) and checkFileExist(root_path, ecws_f):
        #exam_result = main_exam(root_path + ebs_f, root_path + ecws_f)[0]
        exam_result, _, examTitleList, examCodeList, used_colors = main_exam(root_path + ebs_f, root_path + ecws_f, newExam=newExam, deleteExam=deleteExam)
        global RES
        RES = exam_result
        return exam_result, examTitleList, examCodeList, used_colors
    else:
        return False

def generateCourseSchedule(root_path, pre_f):
    if checkFileExist(root_path, pre_f):
        global COURSE_RES
        course_result = main_course()
        COURSE_RES = course_result
        return course_result
    else:
        return False


@app.route('/', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        # Get the name of the uploaded files
        uploaded_files = request.files.getlist("file")
        filenames = []
        for file in uploaded_files:
        # Check if the file is one of the allowed types/extensions
            if file and allowed_file(file.filename):
                # Make the filename safe, remove unsupported chars
                filename = secure_filename(file.filename)
                # Move the file form the temporal folder to the upload
                # folder we setup
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                # Save the filename into a list, we'll use it later
                filenames.append(filename)
            else:
                if not filename:
                    return render_template('index.html', msg = "No file.")
                if not allowed_file(file.filename):
                    return render_template('index.html', msg = "Not supported file.")
        return render_template('index.html', filenames=filenames, msg = "Upload success." )
    return render_template('index.html')

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/examSchedule', methods=['POST'])
def useFile():
    global used_colors_
    root_path = UPLOAD_FOLDER
    ebs_f = "exams_by_subjects.csv"
    ecws_f = "exam_courses_w_students.csv"
    result_s, examTitleList, examCodeList, used_colors = generateSchedule(root_path, ebs_f, ecws_f)
    used_colors_ = used_colors[:]
    result_f = open(UPLOAD_FOLDER + "result.csv", "w")
    RES_ = result_s.split("|")
    writer = csv.writer(result_f)
    for i in range(len(RES_)):
        writer.writerow(["Time slot " + str(i + 1)] + RES_[i].split(","))
    examTitleList = sorted(examTitleList)
    if result_s:
        return render_template('exam.html', js_msg = result_s, examTitleList=examTitleList, examCodeList=examCodeList)
    else:
        return render_template('index.html', msg = "Required file missing, upload first.")

@app.route('/courseSchedule', methods=['POST'])
def useFile2():
    save_path = UPLOAD_FOLDER
    # replace file name
    filename = "prerequisite.csv"
    result = generateCourseSchedule(save_path, filename)
    result_f = open(UPLOAD_FOLDER + "course_result.csv", "w")
    RES_ = result.split("|")
    writer = csv.writer(result_f)
    for i in range(len(RES_)):
        writer.writerow(["Time slot " + str(i + 1)] + RES_[i].split(","))
    if result:
        return render_template('course.html', js_msg = result)
    else:
        return render_template('index.html', msg = "Required file missing, upload first.")

@app.route('/download', methods=['POST'])
def download():
    # change filename for download
    filename = "final_exams.csv"
    # create response
    response = make_response(send_file(UPLOAD_FOLDER + "result.csv"))
    response.headers['Content-Disposition'] = 'attachment; filename=' + filename
    response.mimetype = 'text/csv'
    return response

@app.route('/downloadCourse', methods=['POST'])
def download2():
    # change filename for download
    filename = "course_assignments.csv"
    # create response
    response = make_response(send_file(UPLOAD_FOLDER + "course_result.csv"))
    response.headers['Content-Disposition'] = 'attachment; filename=' + filename
    response.mimetype = 'text/csv'
    return response

@app.route('/regenerate', methods=['POST'])
def rege():
    course_title = request.form.get("selected_exam")
    new_time = request.form.get("selected_time")
    re_result, examCodeList, examTitleList = main_rege(course_title, new_time, used_colors_)
    print("course_title: ",course_title)
    print("new_time: ", new_time)
    result_f = open(UPLOAD_FOLDER + "result.csv", "w")
    RES_ = re_result.split("|")
    writer = csv.writer(result_f)
    for i in range(len(RES_)):
        writer.writerow(["Time slot " + str(i + 1)] + RES_[i].split(","))
    return render_template('exam.html', js_msg = re_result, examCodeList=examCodeList, examTitleList=examTitleList)


@app.route('/addExam', methods=['POST'])
def addExam():
    course_code = request.form.get("examCourse")
    # run exam scheduling process
    root_path = UPLOAD_FOLDER
    ebs_f = "exams_by_subjects.csv"
    ecws_f = "exam_courses_w_students.csv"
    result_s, examTitleList, examCodeList, used_colors = generateSchedule(root_path, ebs_f, ecws_f, newExam=course_code)
    result_f = open(UPLOAD_FOLDER + "result.csv", "w")
    RES_ = result_s.split("|")
    writer = csv.writer(result_f)
    for i in range(len(RES_)):
        writer.writerow(["Time slot " + str(i + 1)] + RES_[i].split(","))
    if result_s:
        # update ebs.csv
        ebsFile = open(UPLOAD_FOLDER + ebs_f, "a")
        ebsUpdate = csv.writer(ebsFile)
        ebsUpdate.writerow(['Y', '3 hr', course_code.split(" ")[0], course_code.split(" ")[1], "LEC"])
        return render_template('exam.html', js_msg = result_s, examTitleList=examTitleList, examCodeList=examCodeList)
    else:
        return render_template('index.html', msg = "Adding failed.")


@app.route('/deleteExam', methods=['POST'])
def deleteExam():
    course_code = request.form.get("examCourse")
    # run exam scheduling process
    root_path = UPLOAD_FOLDER
    ebs_f = "exams_by_subjects.csv"
    ecws_f = "exam_courses_w_students.csv"
    result_s, examTitleList, examCodeList, used_colors = generateSchedule(root_path, ebs_f, ecws_f, deleteExam=course_code)
    result_f = open(UPLOAD_FOLDER + "result.csv", "w")
    RES_ = result_s.split("|")
    writer = csv.writer(result_f)
    for i in range(len(RES_)):
        writer.writerow(["Time slot " + str(i + 1)] + RES_[i].split(","))
    if result_s:
        # update ebs.csv
        oldEbsFile = open(UPLOAD_FOLDER + ebs_f, "r")
        data = list(csv.reader(oldEbsFile))
        newEbsFile = open(UPLOAD_FOLDER + ebs_f, "w")
        ebsUpdate = csv.writer(newEbsFile)
        for row in data:
            if row[2] + " " + row[3] != course_code:
                ebsUpdate.writerow(row)
        return render_template('exam.html', js_msg = result_s, examTitleList=examTitleList, examCodeList=examCodeList)
    else:
        return render_template('index.html', msg = "Deleting failed.")

if __name__ == "__main__":
    app.run("0.0.0.0", port = 80, debug=True)
