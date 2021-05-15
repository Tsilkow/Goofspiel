from sage.all import matrix, vector, QQ, show, InteractiveLPProblem

gameResults = {}

def signum(a, b):
    if   a > b: return 1
    elif b > a: return -1
    else:       return 0

def popAndPass(inputList, toPop):
    result = inputList.copy()
    result.pop(toPop)
    return result;

def getGameResults(rewards, cards1, cards2):
    if len(rewards) == 1: return rewards[0] * signum(cards1[0], cards2[0])
    elif gameResults.has_key([rewards, cards1, cards2]): return gameResults[[rewards, cards1, cards2]]
    elif gameResults.has_key([rewards, cards2, cards1]): return gameResults[[rewards, cards1, cards2]] * (-1)
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
    show(P)
    P.run_simplex_method()
    print(P.optimal_solution())
    print(P.objective_value(P.optimal_solution()))
    return P.objective_value(P.optimal_solution())

a = createPayoffMatrix([12, 13], 1, [2, 4], [1, 3])
print(a)
solveNash(a)
