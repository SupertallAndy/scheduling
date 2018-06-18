import csv
import operator
import random
import json

slot_course = {}

linked_same_penalty = float("inf")
three_exam_penalty = float("inf")
night_penalty = [20, 30, 40, 50, 60]
all_slots = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
consecutive_penalty = 5
exam_courses = []
courses = {}
students = {}
# use a character randomly from a to z to represent color
used_color = []
vertices = []
edges = []


# ---------------------Construct the graph---------------------------------#
# student enrolled in two courses link two vertices
# edge weight is number of such students
class Student:
    def __init__(self, id):
        self.id = id
        self.courses = []


# Each course is a vertex of the graph
class Course:
    def __init__(self, subject, catalog, section, title, instructor):
        self.sbjct = subject
        self.cat = catalog
        self.sec = section
        self.title = title
        self.instructor = instructor
        self.student = []
        self.exam = False
        self.color = ""
        # The degree defined here is the total number of edge weights
        self.degree = 0
        self.adjacency = []


# Edge between two vertices
class Edge:
    def __init__(self, vertex1, vertex2, w):
        self.v1 = vertex1
        self.v2 = vertex2
        self.weight = w


def calcEdgeWeight(vertex1, vertex2, courses):
    v1set = set(courses[vertex1].student)
    v2set = set(courses[vertex2].student)
    return len(v1set & v2set)


def calc_degree(exam_courses, courses):
    for v1 in exam_courses:
        for v2 in exam_courses:
            if v1 != v2:
                weight = calcEdgeWeight(v1, v2, courses)
                if weight:
                    new_edge = Edge(v1, v2, weight)
                    # v1->v2, v2->v1 will be two edges in the edge list
                    edges.append(new_edge)
                    courses[v1].degree += weight
                    courses[v1].adjacency.append(courses[v2])


# ---------------------Color the graph---------------------------------#
# check whether student take three exams in 24 hours
def check_three_exam(color, students, courses):
    student_exam_colors = {}
    for student in list(students.values()):
        student_exam_colors[student] = [courses[course_code].color for course_code in student.courses if
                                        course_code in exam_courses and courses[course_code].color != ""]
    for student in student_exam_colors.keys():
        for color1 in student_exam_colors[student]:
            for color2 in student_exam_colors[student]:
                if (abs(ord(color1) - ord(color2))) == 5:
                    if (abs(ord(color1) - ord(color))) == 5 or (abs(ord(color2) - ord(color))) == 5:
                        return True

                return False


# choose which color to give for vertex
def choose_color(ver, used_colors, courses, students, exam_courses):
    color_score = {}
    violation_record = {}
    all_inf = True
    for color in used_colors:
        if color not in color_score.keys():
            color_score[color] = 0
        if color not in violation_record.keys():
            violation_record[color] = []
        for v in ver.adjacency:
            if color == v.color:
                color_score[color] += linked_same_penalty
                violation_record[color].append(("two_at_same_time", float("inf")))
        if check_three_exam(color, students, courses):
            color_score[color] += three_exam_penalty
            violation_record[color].append(("three_in_24h", float("inf")))
        if ord(color) >= 107:
            color_score[color] = 10
            violation_record[color] = [("night_penalty", 10)]
        crowd_penalty = max(0, len(slot_course[color]) + 1 - len(exam_courses) / 10 * 3 / 2)
        color_score[color] += crowd_penalty
        violation_record[color].append(("crowd_exams", crowd_penalty))
    remain_color = [col for col in all_slots if col not in used_colors]
    # new_color = random.choice(remain_color)
    new_color = remain_color[0]
    color_score[new_color] = 0
    violation_record[new_color] = []
    if ord(new_color) >= 107:
        color_score[new_color] = 10
        violation_record[new_color] = [("night_penalty", 10)]
    for score in color_score.values():
        if score < float("inf"):
            all_inf = False
    if all_inf and len(used_color) >= 15:
        # restart the algorithm
        chosen_color = 'fail'
    else:
        print(color_score)
        chosen_color = min(color_score, key=lambda k: color_score[k])
        print(chosen_color)
        if chosen_color == new_color:
            used_color.append(new_color)
    return chosen_color, color_score[chosen_color], violation_record[chosen_color]


# Color the whole graph
def color_the_graph(vertices, used_color, courses, students, exam_courses):
    total_score = 0
    total_violation = []
    # Sort vertices by degree
    calc_degree(exam_courses, courses)
    vertices.sort(key=operator.attrgetter("degree"))
    for i in range(len(vertices) - 1, -1, -1):
        ver = vertices[i]
        # This is the first vertex to color, do not consider score
        if len(used_color) == 0:
            ver.color = random.choice(all_slots[:10])
            used_color.append(ver.color)
            if ver.color not in slot_course.keys():
                slot_course[ver.color] = []
            slot_course[ver.color].append(ver)
            # print(ver.title, ver.color)
        else:
            chosen_clr, score, violation_record = choose_color(ver, used_color, courses, students, exam_courses)
            total_score += score
            total_violation.extend(violation_record)
            # print(ver.title, chosen_clr)
            if chosen_clr != "fail":
                ver.color = chosen_clr
                if ver.color not in slot_course.keys():
                    slot_course[ver.color] = []
                slot_course[ver.color].append(ver)
            else:
                raise ("This round failed")
                # color_the_graph(vertices, used_color, courses, students)
    return total_score, total_violation


def main(ebs_f, ecws_f):
    #global vertices
    assign_results = ""
    with open(ecws_f) as ecws, open(ebs_f) as ebs:
        # set readers
        ecwsReader = csv.DictReader(ecws, delimiter=',')
        ebsReader = csv.DictReader(ebs, delimiter=',')

        # create course and student objs
        for row in ecwsReader:
            course_code = row['Sbjct Cd'].strip() + '-' + row['Catalog Nbr'].strip()
            student_id = row['Student'].strip()
            if course_code not in courses.keys():
                courses[course_code] = Course(subject=row['Sbjct Cd'].strip(), catalog=row['Catalog Nbr'].strip(),
                                              section=row['Class Section Cd'].strip(),
                                              title=row['Course Title '].strip(),
                                              instructor=row['Instructor Name'].strip())
                # handle special courses (Chinese, Math)
                if 'CHIN-SHU' in course_code or 'MATH-SHU' in course_code:
                    courses[course_code].exam = True
                    exam_courses.append(course_code)

            courses[course_code].student.append(student_id)

            if student_id not in students.keys():
                students[student_id] = Student(student_id)

            if courses[course_code] not in students[student_id].courses:
                students[student_id].courses.append(courses[course_code])

        for row in ebsReader:
            if row['Subject'].strip() == 'CHIN-SHU' or row['Subject'].strip() == 'MATH-SHU':
                continue
            course_code = row['Subject'].strip() + '-' + row['Cat#'].strip()
            courses[course_code].exam = True
            # add to exam courses list
            exam_courses.append(course_code)

    vertices = [courses[course_code] for course_code in courses.keys() if course_code in exam_courses]
    total_score, total_violation = color_the_graph(vertices, used_color, courses, students, exam_courses)
    # print(len(sorted(slot_course.keys())))
    # for idx in range(len(sorted(slot_course.keys()))):
    #     assign_results += ','.join([ver.title for ver in slot_course[sorted(slot_course.keys())[idx]]])
    #     assign_results += '|'
    #     print("|")
    print("score: ", total_score)
    #print("violation: ", total_violation)
    return slot_course


# slot_course是对应真正assign到real 5 * 3 slots的结果
def modify(course_title, new_slot):
    global slot_course
    need_modify = []
    ver = ''
    for i in range(len(vertices)):
        ver = vertices[i]
        if ver.title == course_title:
            break
    #print("Need to move ", course_title, " from ", ver.color, " to ", new_slot)
    if new_slot not in used_color:
        used_color.append(new_slot)
        slot_course[new_slot] = [ver]
    else:
        slot_course[new_slot].append(ver)
        slot_course[ver.color].remove(ver)
        ver.color = new_slot
        selection = {}
        for adj in ver.adjacency:
            if adj.color == new_slot:
                #print(adj.title, " is also at ", adj.color)
                for col in slot_course.keys():
                    if col != new_slot:
                        selection[col] = 0
                        for course in slot_course[col]:
                            if course in adj.adjacency:
                                selection[col] += 1
                min_t = min(selection.items(), key=lambda x: x[1])
                new_adj_c = min_t[0]
                need_modify.append((adj.title, new_adj_c))
    return need_modify


def regenerate(course_title, new_slot):
    need_modify = modify(course_title, new_slot)
   # print(need_modify)
    while len(need_modify) != 0:
        for tup in need_modify:
            need_modify_ = modify(tup[0], tup[1])
            need_modify.extend(need_modify_)
            need_modify.remove(tup)
    return slot_course

def main_rege(course_title, new_slot):
    new_results = ''
    slot_course = regenerate(course_title, new_slot)
    print(len(sorted(slot_course.keys())))
    print([ver.title for ver in slot_course[new_slot]])
    for idx in range(len(sorted(slot_course.keys()))):
        new_results += ','.join([ver.title for ver in slot_course[sorted(slot_course.keys())[idx]]])
        new_results += '|'
        print("|")
    return new_results

if __name__ == "__main__":
    slot_course = main("/Users/weiyuwang/Desktop/flask_upload/exams_by_subjects.csv", "/Users/weiyuwang/Desktop/flask_upload/exam_courses_w_students.csv")
    print(slot_course.keys())