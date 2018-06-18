import csv
from dataClass import Course, Instructor, Edge, prereqCount

tierNum = 4

courses = {}
instructors = {}

with open('files_needed/prerequisite.csv') as prereq:
    # set readers
    prereqReader = csv.DictReader(prereq, delimiter = ',')
    # create course and instructor dictionary
    for row in prereqReader:
        course = Course(row['category'], row['cat_num'], row['course_title'], row['course_num'], row['instructor'], row['prerequisite'], row['notes'], row['recitation'], row['length'])
        if course.instructor:
            for instructor in course.instructor:
                if instructor not in instructors:
                    instructors[instructor] = Instructor(instructor, course.course_num, row['not available'])
                else:
                    instructors[instructor].courses_teach.append(course.course_num)
        courses[row['course_num']] = course

prereqCounts = prereqCount(courses)


preqTiers = {}
for course, count in prereqCounts.items():
    if count not in preqTiers.keys():
        preqTiers[count] = [course]
    else:
        preqTiers[count].append(course)


maxNumPerTier = len(courses.keys())/tierNum

countList = list(preqTiers.keys())
countList.sort()

advanceCourse = []
intermediateCourse = []
elementaryCourse = []
otherCourse = []
for count in countList:
    if count == -1:
        otherCourse += preqTiers[count]
    elif len(advanceCourse) < maxNumPerTier * 0.8:
        advanceCourse += preqTiers[count]
    elif len(intermediateCourse) < maxNumPerTier:
        intermediateCourse += preqTiers[count]
    else:
        elementaryCourse += preqTiers[count]
