from sage.all import matrix, vector, RR, QQ, show, InteractiveLPProblem, MixedIntegerLinearProgram
import sys
import bisect

N = 3 # liczba kart w każdym kolorze tj: liczba kart w talii nagrod
if len(sys.argv) > 1: N = int(sys.argv[1])

gameResults = []

# Pomocnicza funkcja do określenia znaku liczby
def signum(a, b):
    if   a > b: return 1
    elif b > a: return -1
    else:       return 0

# Funkcja kodujaca liste do haszowalnego stringa
def listToIndex(inputList):
    result = ''
    for i in inputList:
        result = result.join(str(i))
    return result

# Pomocnicza funkcja kopiujaca liste poza jednym elementem
def popAndPass(inputList, toPop):
    result = inputList.copy()
    result.pop(toPop)
    return result;

# Pomocnicza funkcja kopiujaca liste z dodatkowym (i posortowanym) elementem
def addAndPass(inputList, toAdd):
    result = inputList.copy()
    bisect.insort(result, toAdd)
    return result

# Funkcja poszukujaca i zwracajaca rezultat danej konfiguracji; jeśli taki nie jest policzony, zwracany jest falsz
def getGameResults(rewards, cards1, cards2):
    if len(rewards) == 1: return rewards[0] * signum(cards1[0], cards2[0])
    elif cards1 == cards2:
        return 0
    elif listToIndex([rewards, cards1, cards2]) in gameResults[len(rewards)]:
        return gameResults[len(rewards)][listToIndex([rewards, cards1, cards2])]
    elif listToIndex([rewards, cards2, cards1]) in gameResults[len(rewards)]:
        return gameResults[len(rewards)][listToIndex([rewards, cards2, cards1])] * (-1)
    else:
        exit("!ERROR! Did not find ", rewards, " ", cards1, " ", cards2, " state in result dictionary!")

# Funkcja tworzaca matryce wyplat dla danej konfiguracji i wybranej nagrody
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
    

# Funkcja odnajdujaca rownowage Nasha
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
    P.run_simplex_method()
    
    return [P.objective_value(P.optimal_solution()), P.optimal_solution()[:-2]]

#def newSolveNash(payoffMatrix):
#    solution = []
#    lp = MixedIntegerLinearProgram(maximization=True)
#
#    x = lp.new_variable()
#
#    lp.set_objective(x[len(payoffMatrix)])
#
#    for r in range(len(payoffMatrix)):
#        lp.add_constraint(sum(x[i] * payoffMatrix[i][r] for i in range(len(payoffMatrix))) -
#                          x[len(payoffMatrix)] >= 0)
#    lp.add_constraint(sum(x[i] for i in range(len(payoffMatrix))) == 1)
#
#    lp.solve()
#    
#    for i in range(len(payoffMatrix)):
#        solution.append(lp.get_values(x)[i])
#
#    return [lp.solve(), solution]

# Funkcja rozwiazujaca konkretna konfiguracje gry - pod warunkiem że konfiguracje mniejszych dlugości sa rozwiazane
def solveGame(rewards, cards1, cards2):
    if listToIndex([rewards, cards1, cards2]) not in gameResults[len(rewards)]:
        if len(rewards) > 1:
            result = []
            for r in range(len(rewards)):
                payoffMatrix = createPayoffMatrix(rewards, r, cards1, cards2)
                result.append(solveNash(payoffMatrix)[0])
                gameResults[len(rewards)][listToIndex([rewards, cards1, cards2])] = 1/len(rewards) * sum(result)

# Funkcja wywolujaca rozwiazywanie pojedynczych konfiguracji w odpowiedniej kolejności
def solveGamesRecursively(maxSize):
    currSize = [] # [[rewards, cards1, cards2], [...], ...]
    nextSize = [[[], [], []]] # [[rewards, cards1, cards2], [...], ...]

    for size in range(maxSize):
        #print(len(nextSize))
        gameResults.append({}) # dodawanie tablicy ze slownikiem gier talii dlugości size
        if len(gameResults) >= 3: gameResults[-3] = {} # usuwanie zbednego slownika
        currSize = nextSize
        nextSize = []

        for game in currSize:
            if listToIndex(game) not in gameResults[len(game[0])]:
                #print(game)
                for i in range(1, maxSize+1):
                    if i not in game[0]:
                        for j in range(1, maxSize+1):
                            if j not in game[1]:
                                for k in range(1, maxSize+1):
                                    if k not in game[2]:
                                        temp = [addAndPass(game[0], i),
                                                addAndPass(game[1], j),
                                                addAndPass(game[2], k)]
                                        if temp not in nextSize \
                                           and [temp[0], temp[1], temp[2]] not in nextSize \
                                           and temp[1] != temp[2]:
                                            nextSize.append(temp)

            if size >= 2:
                solveGame(game[0], game[1], game[2])

    final = [i+1 for i in range(maxSize)]
    showMatrix(final, final, final)

# Funkcja tworzaca finalna matryce
def showMatrix(rewards, cards1, cards2):
    result = []
    for r in range(len(rewards)):
        payoffMatrix = createPayoffMatrix(rewards, r, cards1, cards2)
        result.append(solveNash(payoffMatrix)[1])

    decimal_result = []
    for r in range(len(result)):
        decimal_result.append([])
        for c in range(len(result[r])):
            decimal_result[-1].append("%.4f" % RR(result[c][r]))

    for c in decimal_result:
        print(c)
    return decimal_result

solveGamesRecursively(N)
