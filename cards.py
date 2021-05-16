from sage.all import matrix, vector, RR, QQ, show, InteractiveLPProblem
import sys
import bisect

gameResults = {}

def signum(a, b):
    if   a > b: return 1
    elif b > a: return -1
    else:       return 0

def listToString(inputList):
    result = ''
    for i in inputList:
        result = result.join(str(i))
    return result

def popAndPass(inputList, toPop):
    result = inputList.copy()
    result.pop(toPop)
    return result;

def addAndPass(inputList, toAdd):
    result = inputList.copy()
    bisect.insort(result, toAdd)
    return result

def getGameResults(rewards, cards1, cards2):
    if len(rewards) == 1: return rewards[0] * signum(cards1[0], cards2[0])
    elif cards1 == cards2:
        return 0
    elif listToString([rewards, cards1, cards2]) in gameResults:
        return gameResults[listToString([rewards, cards1, cards2])]
    elif listToString([rewards, cards2, cards1]) in gameResults:
        return gameResults[listToString([rewards, cards2, cards1])] * (-1)
    else:
        print("!ERROR! Did not find ", rewards, " ", cards1, " ", cards2, " state in result dictionary!")
        exit("0")
        
#def getGameResults(rewards, cards1, cards2):
#    a = getGameResultsP(rewards, cards1, cards2)
#    print(rewards, cards1, cards2, a)
#    return a

def createPayoffMatrix(rewards, rewardIndex, cards1, cards2):
    result = []
    for c1 in range(len(cards1)):
        result.append([])
        for c2 in range(len(cards2)):
            result[-1].append(rewards[rewardIndex] * signum(cards1[c1], cards2[c2]) +
                              getGameResults(popAndPass(rewards, rewardIndex),
                                             popAndPass(cards1, c1),
                                             popAndPass(cards2, c2)))
    return result
    

def solveNash(payoffMatrix):
    
    mb = [0 for i in range(len(payoffMatrix))]
    mb.append(1)
    mc = [0 for i in range(len(payoffMatrix[0]))]
    mc.append(1)

    vt = ['>=' for i in range(len(payoffMatrix))]
    vt.append('')
    ct = ['>=' for i in range(len(payoffMatrix[0]))]
    ct.append('==')

    ag = [1 for i in range(len(payoffMatrix))]
    ag.append(0)
    A = matrix(QQ, payoffMatrix).transpose().augment(vector(QQ, [-1 for i in range(len(payoffMatrix[0]))])).stack(vector(QQ, ag))
    b = vector(QQ, mb)
    c = vector(QQ, mc)
    
    P = InteractiveLPProblem(A, b, c, variable_type=vt, constraint_type=ct)
    P = P.standard_form()
    #show(P)
    P.run_simplex_method()
    #print(P.optimal_solution())
    #print(P.objective_value(P.optimal_solution()))
    return [P.objective_value(P.optimal_solution()), P.optimal_solution()]

#a = createPayoffMatrix([12, 13], 1, [2, 4], [1, 3])
#print(a)
#solveNash(a)

def solveGame(rewards, cards1, cards2):
    if listToString([rewards, cards1, cards2]) not in gameResults:
        if len(rewards) > 1:
            result = []
            for r in range(len(rewards)):
                payoffMatrix = createPayoffMatrix(rewards, r, cards1, cards2)
                result.append(solveNash(payoffMatrix)[0])
                gameResults[listToString([rewards, cards1, cards2])] = 1/len(rewards) * sum(result)

def showMatrix(rewards, cards1, cards2):
    result = []
    for r in range(len(rewards)):
        payoffMatrix = createPayoffMatrix(rewards, r, cards1, cards2)
        result.append(solveNash(payoffMatrix)[1][:-2])

    decimal_result = []
    for r in range(len(result)):
        decimal_result.append([])
        for c in range(len(result[r])):
            decimal_result[-1].append("%.2f" % RR(result[r][c]))
            
    print(decimal_result)
    return decimal_result

def solveGamesRecursively(maxSize):
    currSize = [] # [[rewards, cards1, cards2], [...], ...]
    nextSize = [[[], [], []]] # [[rewards, cards1, cards2], [...], ...]

    for size in range(maxSize):
        print(len(nextSize))
        currSize = nextSize
        nextSize = []

        for game in currSize:
            if listToString(game) not in gameResults:
                print(game)
                for i in range(1, maxSize+1):
                    if i not in game[0]:
                        for j in range(1, maxSize+1):
                            if j not in game[1]:
                                for k in range(1, maxSize+1):
                                    if k not in game[2]:
                                        temp = [addAndPass(game[0], i),
                                                addAndPass(game[1] , j),
                                                addAndPass(game[2],  k)]
                                        if temp not in nextSize \
                                           and [temp[0], temp[2], temp[1]] not in nextSize \
                                           and temp[1] != temp[2]:
                                            nextSize.append(temp)

            if size >= 2:
                solveGame(game[0], game[1], game[2])

    final = [[i+1 for i in range(maxSize)], [i+1 for i in range(maxSize)], [i+1 for i in range(maxSize)]]
    showMatrix(final[0], final[1], final[2])

maxSize = 3
if len(sys.argv) > 1: maxSize = int(sys.argv[1])
solveGamesRecursively(maxSize)
