def write(name, distance):
    f = open('marathon.txt', 'a')
    f.write(f"{name} - {distance}\n")
    f.close()