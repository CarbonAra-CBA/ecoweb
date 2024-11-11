# A~F 등급까지 매기기

def grade_point(totalsize_kb):
    if totalsize_kb <= 272.51:
        return "A+"
    elif totalsize_kb <= 531.15:
        return "A"
    elif totalsize_kb <= 975.85:
        return "B"
    elif totalsize_kb <= 1410.39:
        return "C"
    elif totalsize_kb <= 1875.01:
        return "D"
    elif totalsize_kb <= 2419.56:
        return "E"
    elif totalsize_kb >= 2419.57:
        return "F"

    return None
