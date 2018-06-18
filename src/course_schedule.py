from copy import deepcopy
from processing import *
from util import isSameMajor, isSameInstructor, checkInstAvailability, degreeSort, greedy_coloring, courseObjDict_to_dict




def main_course():
    # Edge list
    edges_l = []
    # course list contains course objects (4 levels)
    elementaryCourseList = []
    intermediateCourseList = []
    advanceCourseList = []
    otherCourseList = []
    # recitation list contains course objects (4 levels)
    elementaryRecList = []
    intermediateRecList = []
    advanceRecList = []
    otherRecList = []
    # calculate degrees within each course level group
    # only edges between courses in the same level will be counted
    for index, courseList in enumerate([elementaryCourse, intermediateCourse, advanceCourse, otherCourse]):
        for course1 in courseList:
            degree_count = 0
            for course2 in courseList:
                # check edges within that level
                # 1. no two courses by same instructors
                # 2. no two courses from the same major
                if course1 != course2 and (isSameMajor(courses[course1], courses[course2]) or isSameInstructor(courses[course1], courses[course2])):
                    edges_l.append(Edge(courses[course1].course_num, courses[course2].course_num))
                    degree_count += 1
                    courses[course1].adjacentCourses.append(courses[course2])
            # update degree
            courses[course1].degree = degree_count
            # add course_obj to corresponding list
            if index == 0:
                if courses[course1].recitation:
                    elementaryRecList.append(courses[course1])
                elementaryCourseList.append(courses[course1])
            elif index == 1:
                if courses[course1].recitation:
                    intermediateRecList.append(courses[course1])
                intermediateCourseList.append(courses[course1])
            elif index == 2:
                if courses[course1].recitation:
                    advanceRecList.append(courses[course1])
                advanceCourseList.append(courses[course1])
            else:
                if courses[course1].recitation:
                    otherRecList.append(courses[course1])
                otherCourseList.append(courses[course1])



    # sort course list of each level according to degree
    elementaryCourseList.sort(key=lambda course: course.degree, reverse=True)
    elementaryRecList.sort(key=lambda course: course.degree, reverse=True)
    intermediateCourseList.sort(key=lambda course: course.degree, reverse=True)
    intermediateRecList.sort(key=lambda course: course.degree, reverse=True)
    advanceCourseList.sort(key=lambda course: course.degree, reverse=True)
    advanceRecList.sort(key=lambda course: course.degree, reverse=True)
    otherCourseList.sort(key=lambda course: course.degree, reverse=True)
    otherRecList.sort(key=lambda course: course.degree, reverse=True)




    # run greedy coloring
    # first assign slots to lectures
    # run courses of each level seperately
    colorSet = {'lecture': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'recitation': [11, 12, 13, 14, 15]}

    elementaryCourseResult = greedy_coloring(colorSet, 'lecture', elementaryCourseList, instructors)
    elementaryCourseResult = courseObjDict_to_dict(elementaryCourseResult)

    intermediateCourseResult = greedy_coloring(colorSet, 'lecture', intermediateCourseList, instructors)
    intermediateCourseResult = courseObjDict_to_dict(intermediateCourseResult)

    advanceCourseResult = greedy_coloring(colorSet, 'lecture', advanceCourseList, instructors)
    advanceCourseResult = courseObjDict_to_dict(advanceCourseResult)

    elementaryRecResult = greedy_coloring(colorSet, 'recitation', elementaryRecList, instructors)
    elementaryRecResult = courseObjDict_to_dict(elementaryRecResult)

    intermediateRecResult = greedy_coloring(colorSet, 'recitation', intermediateRecList, instructors)
    intermediateRecResult = courseObjDict_to_dict(intermediateRecResult)

    advanceRecResult = greedy_coloring(colorSet, 'recitation', advanceRecList, instructors)
    advanceRecResult = courseObjDict_to_dict(advanceRecResult)

    otherCourseResult = greedy_coloring(colorSet, 'lecture', otherCourseList, instructors)
    otherCourseResult = courseObjDict_to_dict(otherCourseResult)

    otherRecResult = greedy_coloring(colorSet, 'recitation', otherRecList, instructors)
    otherRecResult = courseObjDict_to_dict(otherRecResult)

    print()

    allResult = {}

    for key in elementaryCourseResult.keys():
        allResult[key] = elementaryCourseResult[key]

    for key in intermediateCourseResult.keys():
        if key not in allResult.keys():
            allResult[key] = intermediateCourseResult[key]
        else:
            allResult[key].extend(intermediateCourseResult[key])

    for key in advanceCourseResult.keys():
        if key not in allResult.keys():
            allResult[key] = advanceCourseResult[key]
        else:
            allResult[key].extend(advanceCourseResult[key])

    for key in elementaryRecResult.keys():
        allResult[key] = elementaryRecResult[key]

    for key in intermediateRecResult.keys():
        if key not in allResult.keys():
            allResult[key] = intermediateRecResult[key]
        else:
            allResult[key].extend(intermediateRecResult[key])

    for key in advanceRecResult.keys():
        if key not in allResult.keys():
            allResult[key] = advanceRecResult[key]
        else:
            allResult[key].extend(advanceRecResult[key])

    for key in otherCourseResult.keys():
        if key not in otherCourseResult.keys():
            allResult[key] = otherCourseResult[key]
        else:
            allResult[key].extend(otherCourseResult[key])

    for key in otherRecResult.keys():
        if key not in otherRecResult.keys():
            allResult[key] = otherRecResult[key]
        else:
            allResult[key].extend(otherRecResult[key])

    allResultStr = ''
    for idx in range(len(sorted(allResult.keys()))):
        temp = allResult[sorted(allResult.keys())[idx]]
        allResultStr += ','.join([title for title in temp])
        allResultStr += '|'
        # print("|")
    return allResultStr
