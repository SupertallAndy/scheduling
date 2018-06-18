import random
linkPenalty = 10
spreadPenalty = 10
instructorPenalty = float("inf")
consecutiveFail = float("inf")

def isSameMajor(course_obj1, course_obj2):
    return course_obj1.course_num.split(' ')[0] == course_obj2.course_num.split(' ')[0]


def isSameInstructor(course_obj1, course_obj2):
    if (not course_obj1.instructor) or (not course_obj2.instructor):
        return None
    return set(course_obj1.instructor) & set(course_obj2.instructor)


# a course object, collection of instructors and color to be assigned
def checkInstAvailability(course_obj, instructors, color):
    # check availability for each instructor teaching this course
    if course_obj.instructor:
        for instructor in course_obj.instructor:
            if color in instructors[instructor].unavailable:
                return False
    return True


# sort and return the course object collection
def degreeSort(courses):
    return sorted(courses.items(), key=lambda course: course[1].degree, reverse=True)


def greedy_coloring(colorSet, courseType, courseList, instructors):
    color_used = set()
    slot_dict = {}
    for course in courseList:
        # if the first color
        if not color_used:
            # randomly assign a color
            if course.pattern != '3' or courseType == 'recitation':
                color_chosen = [random.choice(colorSet[courseType])]
            else:
                # consecutive time slot if long lecture
                first_half = random.choice(colorSet[courseType])
                color_chosen = [first_half, first_half+1]
            # update color used
            course.color = color_chosen
            color_used.update(color_chosen)
            # update slot dict
            for color in color_chosen:
                if color in slot_dict:
                    slot_dict[color].append(course)
                else:
                    slot_dict[color] = [course]
        else:
            if courseType == 'recitation':
                color_chosen = choose_color_rec(course, colorSet[courseType], instructors, slot_dict)
            else:
                color_chosen = choose_color(course, colorSet[courseType], instructors, slot_dict)
            # if successfully assigned a color
            if color_chosen:
                # update color used
                color_assigned = [color_chosen] if (course.pattern != '3' or courseType == 'recitation') else [color_chosen, color_chosen+1]
                course.color = color_assigned
                color_used.update(color_assigned)
                # update slot dict
                for color in color_assigned:
                    if color in slot_dict:
                        slot_dict[color].append(course)
                    else:
                        slot_dict[color] = [course]                       
            else:
                return None
    return slot_dict








def choose_color(courseToColor, colorList, instructors, slot_dict):
    # initialize score dict
    colorScore_dict = {}
    for color in colorList:
        colorScore_dict[color] = 0
    # if only need one slot
    if courseToColor.pattern != '3':
        # calculate score
        for candidateColor in colorScore_dict:
            # check adjacent courses
            for adjacentCourse in courseToColor.adjacentCourses:
                if set([candidateColor]) & set(adjacentCourse.color):
                    colorScore_dict[candidateColor] += linkPenalty
            # check instructor availability
            for eachInstructor in courseToColor.instructor:
                if set(instructors[eachInstructor].unavailable) & set([candidateColor]):
                    colorScore_dict[candidateColor] += instructorPenalty
            # spread penalty
            colorScore_dict[candidateColor] += spread_penalty(slot_dict, candidateColor)
    # if need two slots
    else:
        # calculate score
        for candidateColor in colorScore_dict:
            # check adjacent courses
            for adjacentCourse in courseToColor.adjacentCourses:
                slot_intersection = set([candidateColor, candidateColor+1]) & set(adjacentCourse.color)
                if (slot_intersection and len(slot_intersection - set([6, 11])) > 0) or ((adjacentCourse.color[0] if adjacentCourse.color else 0) == 6 and candidateColor == 6):
                    colorScore_dict[candidateColor] += linkPenalty
            # check instructor availability
            for eachInstructor in courseToColor.instructor:
                if set(instructors[eachInstructor].unavailable) & set([candidateColor, candidateColor+1]):
                    colorScore_dict[candidateColor] += instructorPenalty
            # spread penalty
            colorScore_dict[candidateColor] += spread_penalty(slot_dict, candidateColor)
    # pick the color with the minimum penalty score
    # return None if violation
    chosen_color = min(colorScore_dict, key=colorScore_dict.get)
    return chosen_color if colorScore_dict[chosen_color] != float('inf') else None
        

                    

def choose_color_rec(courseToColor, colorList, instructors, slot_dict):
    # initialize score dict
    colorScore_dict = {}
    for color in colorList:
        colorScore_dict[color] = 0
    
    # calculate score
    for candidateColor in colorScore_dict:
        # check adjacent courses
        for adjacentCourse in courseToColor.adjacentCourses:
            if set([candidateColor]) & set(adjacentCourse.color):
                colorScore_dict[candidateColor] += linkPenalty
        # check instructor availability
        for eachInstructor in courseToColor.instructor:
            if set(instructors[eachInstructor].unavailable) & set([candidateColor]):
                colorScore_dict[candidateColor] += instructorPenalty
        # spread penalty
            colorScore_dict[candidateColor] += spread_penalty(slot_dict, candidateColor)
    
    # pick the color with the minimum penalty score
    # return None if violation
    chosen_color = min(colorScore_dict, key=colorScore_dict.get)
    return chosen_color if colorScore_dict[chosen_color] != float('inf') else None


def courseObjDict_to_dict(courseObjDict):
    result = {}
    for key, value in courseObjDict.items():
        try:
            result[key] = [course.course_title for course in value]
        except:
            print(value)
    return result



def spread_penalty(slot_dict, candidateColor):
    if candidateColor not in slot_dict:
        return 0
    else:
        return len(slot_dict[candidateColor]) * spreadPenalty