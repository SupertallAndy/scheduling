def fileNumOfLines(filePath):
    fileList = open(filePath).readlines()
    return len(fileList)







if __name__ == "__main__":
    print(fileNumOfLines('/Users/weiyuwang/Desktop/flask_upload/0004000000197100.txt'))
