import pymysql
from math import log2
from math import log

conn = pymysql.connect('localhost', 'root', 'root', 'project2')
cursor = conn.cursor()
entropy = (lambda yes, no, total: ((-1) * (yes / total) * (log2(yes / total))) - ((no / total) * log2(no / total)))
tree = {}


def main():
    """
    This dictionary contains the number of ocurrences of the decision column
    Entropies = {"Yes":#YesOcurrences, "No":#NoOcurrenes}
    """
    occurrences = getDecisionOccurrences("SELECT COUNT(*) FROM data3 WHERE prestarAuto = \"Si\"",
                                         "SELECT COUNT(*) FROM data3 WHERE prestarAuto = \"no\"",
                                         "SELECT COUNT(*) FROM data3")

    print("Number of 'yes' and 'no' occurrences in the decision column:")
    print(occurrences)
    print("Entropy(Decision): %.3f" % entropy(occurrences["yes"], occurrences["no"], occurrences["rows"]))
    column_values = getValues()
    print("Different values for every column of the entire table:")
    print(column_values)



def getDecisionOccurrences(query1, query2, query3):
    D = {}
    # Returns a tuple
    cursor.execute(query1)
    resY = cursor.fetchone()
    # Returns a tuple
    cursor.execute(query2)
    resN = cursor.fetchone()
    # Returns a tuple
    cursor.execute(query3)
    numberOfRows = cursor.fetchone()
    D["yes"] = int(resY[0])
    D["no"] = int(resN[0])
    D["rows"] = int(numberOfRows[0])
    return D


def getValues():
    cols = {"autoPrestado": None, "categoriaAuto": None, "TipoPago": None}
    i = 0
    for key in cols:
        cursor.execute("SELECT DISTINCT " + key + " FROM data3")
        result = cursor.fetchall()
        cols[key] = list(result)
        for i in range(len(cols[key])):
            cols[key][i] = str(cols[key][i]).replace(",", "")
            cols[key][i] = str(cols[key][i]).replace("(", "")
            cols[key][i] = str(cols[key][i]).replace("'", "")
            cols[key][i] = str(cols[key][i]).replace(")", "")

    return cols


def getGain(colVals, de):
    cols = list(colVals.keys())
    yesNoOccurences = {}
    occurencesTotal = {}
    entropies = {}
    colsEntropies = []
    gain = {}
    for col in cols:
        occurencesTotal.__setitem__(col, list())
        yesNoOccurences.__setitem__(col, list())
        gain.__setitem__(col, None)
    count = "SELECT COUNT(*) FROM data3 WHERE "
    equals = " = "
    NOocc = " AND DECISION = \"no\""
    YESocc = " AND DECISION = \"si\""
    j = 0
    for col in cols:
        l = []
        for reg in range(len(colVals[col])):
            # print(count + col + equals + colVals[col][reg])
            q = count + col + equals + '"' + colVals[col][reg] + '"'
            cursor.execute(q)
            total = cursor.fetchone()
            # print(int(str(total).replace(",", "").replace("(", "").replace(")", "")))
            o = int(str(total).replace(",", "").replace("(", "").replace(")", ""))
            l.append(o)
        occurencesTotal[col] = l

    for col in cols:
        ynOcc = []
        for reg in range(len(colVals[col])):
            y = count + col + equals + '"' + colVals[col][reg] + '"' + YESocc
            n = count + col + equals + '"' + colVals[col][reg] + '"' + NOocc
            cursor.execute(y)
            yt = cursor.fetchone()
            cursor.execute(n)
            nt = cursor.fetchone()
            ynOcc.append(int(str(yt).replace(",", "").replace("(", "").replace(")", "")))
            ynOcc.append(int(str(nt).replace(",", "").replace("(", "").replace(")", "")))
        yesNoOccurences[col] = ynOcc

    # print(occurencesTotal)
    # print(yesNoOccurences)

    for col in cols:
        for reg in range(len(colVals[col])):
            entropies.__setitem__(col + "-" + colVals[col][reg], None)

    eSunny = entropy(yesNoOccurences["outlook"][0], yesNoOccurences["outlook"][1], occurencesTotal["outlook"][0])
    colsEntropies.append(eSunny)
    eOvercast = entropy(yesNoOccurences["outlook"][2], yesNoOccurences["outlook"][3],
                        occurencesTotal["outlook"][1]) if not yesNoOccurences["outlook"].__contains__(0) else float(0)
    colsEntropies.append(eOvercast)
    eRain = entropy(yesNoOccurences["outlook"][4], yesNoOccurences["outlook"][5], occurencesTotal["outlook"][2])
    colsEntropies.append(eRain)
    eHot = entropy(yesNoOccurences["temperature"][0], yesNoOccurences["temperature"][1],
                   occurencesTotal["temperature"][0])
    colsEntropies.append(eHot)
    eMild = entropy(yesNoOccurences["temperature"][2], yesNoOccurences["temperature"][3],
                    occurencesTotal["temperature"][1])
    colsEntropies.append(eMild)
    eCool = entropy(yesNoOccurences["temperature"][4], yesNoOccurences["temperature"][5],
                    occurencesTotal["temperature"][2])
    colsEntropies.append(eCool)
    eHigh = entropy(yesNoOccurences["humidity"][0], yesNoOccurences["humidity"][1], occurencesTotal["humidity"][0])
    colsEntropies.append(eHigh)
    eNormal = entropy(yesNoOccurences["humidity"][2], yesNoOccurences["humidity"][3], occurencesTotal["humidity"][1])
    colsEntropies.append(eNormal)
    eWeak = entropy(yesNoOccurences["wind"][0], yesNoOccurences["wind"][1], occurencesTotal["wind"][0])
    colsEntropies.append(eWeak)
    eStrong = entropy(yesNoOccurences["wind"][2], yesNoOccurences["wind"][3], occurencesTotal["wind"][1])
    colsEntropies.append(eStrong)
    # print("Entropies:")
    j = 0
    for key in entropies:
        entropies[key] = format(colsEntropies[j], ".3f")
        j += 1
        # print(key+ ":" + entropies[key])

    # Calculate Gain
    windGain = de - ((occurencesTotal["wind"][0]) / 14) * (eWeak) - ((occurencesTotal["wind"][1]) / 14) * (eStrong)
    gain["wind"] = format(windGain, ".3f")
    humidityGain = de - ((occurencesTotal["humidity"][0]) / 14) * (eHigh) - ((occurencesTotal["humidity"][1]) / 14) * (
        eNormal)
    gain["humidity"] = format(humidityGain, ".3f")
    temperatureGain = de - ((occurencesTotal["temperature"][0]) / 14) * (eHot) - (
                (occurencesTotal["temperature"][1]) / 14) * (eMild) - ((occurencesTotal["temperature"][2]) / 14) * (
                          eCool)
    gain["temperature"] = format(temperatureGain, ".3f")
    outlookGain = de - ((occurencesTotal["outlook"][0]) / 14) * (eSunny) - ((occurencesTotal["outlook"][1]) / 14) * (
        eOvercast) - ((occurencesTotal["outlook"][2]) / 14) * (eRain)
    gain["outlook"] = format(outlookGain, ".3f")
    return gain


def getGainSubset(column, columnValue, table):
    count = "SELECT COUNT(*) FROM tennis WHERE "
    equals = " = "
    NOocc = " AND DECISION = \"no\""
    YESocc = " AND DECISION = \"yes\""
    yesOcc = []
    noOcc = []
    totalOcc = []
    gains = {}
    """
    colData contais the necessary values to calculate the gain of each column
    Ex: colData = {
    "temperature": {
                    "hot": [yes, no, total, entropy], 
                    "mild":[yes, no, total, entropy]}, 
    "humidity":{
                "high":[yes, no, total, entropy], 
                "normal": [yes, no, total, entropy]},
    ...
                 }
    """
    colData = {}
    # Get the entrophy of the decision column
    # print(count + column + equals + "\"" + columnValue + "\"")
    totalq = count + column + equals + "\"" + columnValue + "\""
    cursor.execute(totalq)
    totald = cursor.fetchone()
    totald = int(str(totald).replace("(", "").replace(",", "").replace(")", ""))
    rows = totald
    # print("Number of rows:",totald)
    yesq = count + column + equals + "\"" + columnValue + "\"" + YESocc
    cursor.execute(yesq)
    yesd = cursor.fetchone()
    yesd = int(str(yesd).replace("(", "").replace(",", "").replace(")", ""))
    # print("Number of yes occurences:",yesd)
    noq = count + column + equals + "\"" + columnValue + "\"" + NOocc
    cursor.execute(noq)
    nod = cursor.fetchone()
    nod = int(str(nod).replace("(", "").replace(",", "").replace(")", ""))
    # print("Number of no occurences:",nod)

    decisionEntropy = entropy(yesd, nod, totald)
    # print("Decision entropy when %s = %s: %.3f" %(column, columnValue, decisionEntropy))

    for col in table:
        if not (col == column):
            gains.__setitem__(col, list())
            colData.__setitem__(col, dict())

    for c in table:
        if c in colData:
            for reg in table[c]:
                colData[c][reg] = list()

    for c in table:
        if c in colData:
            l = []
            for reg in table[c]:
                # print(count + c + equals + "\"" + reg +"\"" + " and " + column + equals + "\""  + columnValue + "\"")
                e = 0
                yesq = count + c + equals + "\"" + reg + "\"" + YESocc + " and " + column + equals + "\"" + columnValue + "\""
                noq = count + c + equals + "\"" + reg + "\"" + NOocc + " and " + column + equals + "\"" + columnValue + "\""
                totalq = count + c + equals + "\"" + reg + "\"" + " and " + column + equals + "\"" + columnValue + "\""
                cursor.execute(yesq)
                yesd = cursor.fetchone()
                yesd = int(str(yesd).replace("(", "").replace(",", "").replace(")", ""))
                l.append(yesd)
                cursor.execute(noq)
                nod = cursor.fetchone()
                nod = int(str(nod).replace("(", "").replace(",", "").replace(")", ""))
                l.append(nod)
                cursor.execute(totalq)
                totald = cursor.fetchone()
                totald = int(str(totald).replace("(", "").replace(",", "").replace(")", ""))
                l.append(totald)
                # Calculate the entropy for each registry in a determined column
                e = entropy(yesd, nod, totald) if totald != 0 and yesd != 0 and nod != 0 else float(0)
                l.append(format(e, ".3f"))
                colData[c][reg] = l.copy()
                """At this point we have already saved the number of yes, no, total occurences and entropy  for every registry in
                    the columns that conform the new subset
                    Now we have to obtain the gain for every column and get the highest one"""
                l.clear()

    # Calculate gain for every column
    for column in colData:
        aux = 0
        for reg in colData[column]:

            yesg, nog, totalg, entg = colData[column][reg]
            if entg == 0:
                aux += 0
            else:
                aux += (-1) * (float((int(totalg) / rows) * float(entg)))
        gain = decisionEntropy + aux
        gains[column] = gain

    # Send the column name as key and the highest value as the dict value
    NODE = {}
    node = max(gains.values())
    print(gains)
    keyNode = None
    for key in gains:
        if gains[key] == node:
            keyNode = key

    NODE.__setitem__(columnValue, node)
    print("Key Node for " + columnValue + ": " + keyNode)
    return keyNode


def getBrachesDecision(valsRootNode, leftBranch, rightBranch, table):
    # print(valsRootNode)
    print("left branch: ", end='')
    print(leftBranch)
    print("right brach: ", end='')
    print(rightBranch)

    queryLeft = "select distinct decision from tennis where "
    queryRight = "select distinct decision from tennis where "

    for k in table:
        if k == "outlook":
            for val in table[k]:
                if val == "sunny":
                    queryLeft += k + " = " + "\"" + val + "\"" + " and " + leftBranch + " = "
                elif val == "rain":
                    queryRight += k + " = " + "\"" + val + "\"" + " and " + rightBranch + " = "

    left = []
    right = []
    for val in table[leftBranch]:
        left.append(queryLeft + "\"" + val + "\"")

    for val in table[rightBranch]:
        right.append(queryRight + "\"" + val + "\"")

    print(left)
    print(right)

    leftD = {leftBranch: {"high": None, "normal": None}}
    rightD = {rightBranch: {"weak": None, "strong": None}}

    cursor.execute(left[0])
    d = str(cursor.fetchone()).replace("(", "").replace(",", "").replace(")", "")
    # print(d)
    leftD[leftBranch]["high"] = d
    cursor.execute(left[1])
    d = str(cursor.fetchone()).replace("(", "").replace(",", "").replace(")", "")
    # print(d)
    leftD[leftBranch]["normal"] = d

    cursor.execute(right[0])
    d = str(cursor.fetchone()).replace("(", "").replace(",", "").replace(")", "")
    rightD[rightBranch]["weak"] = d
    cursor.execute(right[1])
    d = str(cursor.fetchone()).replace("(", "").replace(",", "").replace(")", "")
    rightD[rightBranch]["strong"] = d

    branchesDecisions = []
    branchesDecisions.append(dict(leftD))
    branchesDecisions.append(dict(rightD))

    return branchesDecisions


if __name__ == '__main__':
    main()