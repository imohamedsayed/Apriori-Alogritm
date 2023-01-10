import numpy as np
from itertools import combinations,chain

def getTransactions(path,order): #function to get the transactions
    transactions = [] 
    with open(path,'r') as fid: #opening the file 
        for lines in fid: #looping throw lines of transactions
            line = list(lines.strip().split(', ')) #get the items of the # transaction
            # remove repetition of one item in one row 
            _t = list(np.unique(line))
            # items are sorted according to their positions in the order list
            _t.sort(key = lambda x : order.index(x))
            #append the transaction into the transactions list
            transactions.append(_t)
    return transactions


order = ['I' + str(i) for i in range(1,6)]

transactions = getTransactions('./data.txt',order=order)

def count_frequency(item,transactions):
    count = 0
    for i in range(len(transactions)):
        if set(item).issubset(set(transactions[i])):
            count +=1
    return count


def join_two_items(item1,item2,order):
    #making sure that items are sorted according to their positions in the order list
    item1.sort(key = lambda x : order.index(x))
    item2.sort(key = lambda x : order.index(x))
    
    # all items within sorted item set are the same except the last one ,
    # and the last one (the one belonging to the second item set) must be greater than
    # the last one in the first item set. (join criteria)
    
    for i in range(len(item1) - 1):
        if item1[i] != item2[i]:
            return []
    
    if order.index(item1[-1]) < order.index(item2[-1]):
        return item1 + [item2[-1]]
 
    return []
 
 
 
def join_itemsets(itemSet,order):
    C = []
    for i in range(len(itemSet)):
        for j in range(i+1, len(itemSet)):
            item = join_two_items(itemSet[i],itemSet[j],order)
            if len(item) > 0:
                C.append(item)
    return C
    
def getFrequent(itemSets,transactions,min_support,unFrequent):
    L = []
    supp_count = []
    new_unFrequent = []
    transactions_num = len(transactions)
    k = len(unFrequent.keys())
    
    for s in range(len(itemSets)):
        discarded_before = False
        if k>0:
            for item in unFrequent[k]:
                if set(item).issubset(set(itemSets[s])):
                    discarded_before = True
                    break 
        if not discarded_before:
            count = count_frequency(itemSets[s],transactions) # get the frequency of the item set
            
            if count / transactions_num >= min_support: #if itemSet is frequent
                L.append(itemSets[s]) 
                supp_count.append(count)
            else : 
                new_unFrequent.append(itemSets[s])
                
    return L, supp_count , new_unFrequent


def print_table(T,supp_count):
    print("Itemset | Frequency")
    for k in range(len(T)):
        print("{} : {}".format(T[k],supp_count[k]))
    print("\n\n")



c = {}
L = {}

min_support = 2/9 #for example

itemSet_size = 1 #first iteration , we candidate one item in the first iteration so the size is 1

discarded = {itemSet_size:[]} #this will contains the unFrequent items in each iteration 

c.update({itemSet_size : [[f] for f in order]}) #first pruning we candidate all items from I1 -> I5

supp_count_L={} #the support count for each item set

f, sup, new_discarded = getFrequent(c[itemSet_size],transactions,min_support,discarded)

discarded.update({itemSet_size:new_discarded})
L.update({itemSet_size:f})
supp_count_L.update({itemSet_size:sup})

print("L1 : ")
print_table(L[1],supp_count_L[1])



#--------- The Main Loop Of The Algorithm --------------------#

k = itemSet_size +1
convergence = False

while not convergence :
    
    c.update({k : join_itemsets(L[k-1] , order) })
    
    print("Table C{}:  \n".format(k))
    print_table(c[k],[count_frequency(item,transactions) for item in c[k]]) 
    
    f, sup, new_discarded = getFrequent(c[k],transactions,min_support,discarded)
    L.update({k:f})
    supp_count_L.update({k:sup})
    discarded.update({k:new_discarded})
    
    if len(L[k])==0:
        convergence = True
    else:
        print("Table L{}".format(k))
        print_table(L[k],supp_count_L[k])

    k+=1
    


#---------- Association Rule Mining -----------------------#

def powerset(s):
    return list(chain.from_iterable(combinations(s,r) for r in range(1,len(s)+1)))

def write_rules(X,X_S,conf,sup_x,num_transactions):
    out_rule = ""
    out_rule +="Frequent Itemset : {}\n".format(X) 
    out_rule += "        Rule: {} => {}\n".format(list(S),list(X_S))
    out_rule += "        Confidence : {0:2.3f}\n".format(conf)
    out_rule += "        Support : {0:2.3f}\n".format(sup_x / num_transactions)
    return out_rule

assoc_rule_str = ""
min_confidence = 0.3

for i in range(1,len(L)):
    for j in range(len(L[i])):
        s = list(powerset(set(L[i][j])))
        s.pop() # we dont need the last subset which contains all the items 
        for z in s:
            S= set(z)
            X = set(L[i][j])
            X_S = set(X-S)
            sup_x = count_frequency(X , transactions)
            sup_x_s = count_frequency(X_S,transactions)
            conf = sup_x/ count_frequency(S,transactions)
            if conf >= min_confidence and sup_x >= min_support:
                assoc_rule_str += write_rules(X,X_S,conf,sup_x,len(transactions))
                
    
print(assoc_rule_str)