from trueskill import Rating
import trueskill
from trueskill import TrueSkill
import math

BETA = 8.333/2
cdf = TrueSkill().cdf
def win_probability(a, b):                                                      
    deltaMu = sum([x.mu for x in a]) - sum([x.mu for x in b])                   
    sumSigma = sum([x.sigma ** 2 for x in a]) + sum([x.sigma ** 2 for x in b])  
    playerCount = len(a) + len(b)                                               
    denominator = math.sqrt(playerCount * (BETA * BETA) + sumSigma)             
    return cdf(deltaMu / denominator)  