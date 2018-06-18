class Course:
    def __init__(self, category, cat_num, course_title, course_num, instructor, prerequisite, notes, recitation, length):
        self.category = category
        self.cat_num = cat_num
        self.course_title = course_title
        self.course_num = course_num
        self.instructor = toInstructorList(instructor)
        self.prerequisite = toPreqList(prerequisite)
        self.notes = notes if notes else None
        self.recitation = isRecitationRequired(recitation)
        self.pattern = length
        self.degree = 0
        self.adjacentCourses = []
        self.color = []


class Instructor:
    def __init__(self, name, course, schedule):
        self.name = name
        self.courses_teach = [course]
        self.unavailable = [int(n) for n in schedule.split(',')] if schedule else []


class Edge:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2


def toPreqList(prerequisite):
    if not prerequisite:
        return False
    prerequisite = prerequisite.replace("(", "")
    prerequisite = prerequisite.replace(")", "")
    prerequisite = prerequisite.replace("or", ",")
    prerequisite = prerequisite.replace("and", ",")
    courses = [course.strip(' ') for course in prerequisite.split(",")]
    return courses


def toInstructorList(instructor):
    if not instructor:
        return []
    elif ';' not in instructor:
        return [instructor]
    else:
        return [instructor.strip(' ') for instructor in instructor.split(';')]


def isRecitationRequired(value):
    return True if int(value) else False


def prereqCount(courses):
    prereqCount = {}
    for _, course in courses.items():
        if course.prerequisite:
            for eachPrereq in course.prerequisite:
                if eachPrereq not in prereqCount.keys():
                    prereqCount[eachPrereq] = 1
                else:
                    prereqCount[eachPrereq] += 1
        # else:
        #     prereqCount[course.course_num] = 0

    # courses neither have prereq or not as prereq of other course labeled as -1
    # advance courses labeled as 0
    for course in courses:
        if course not in prereqCount:
            if courses[course].prerequisite:
                prereqCount[course] = 0
            else:
                prereqCount[course] = -1

    # adjust situation such as precalc
    adjustPrereqCount = prereqCount.copy()
    for title, course in courses.items():
        if course.prerequisite:
            for eachPrereq in course.prerequisite:
                adjustPrereqCount[eachPrereq] += prereqCount[title]
    
    return adjustPrereqCount

