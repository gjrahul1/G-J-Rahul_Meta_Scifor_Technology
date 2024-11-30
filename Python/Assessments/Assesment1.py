import numpy as np

#Defining Lists
lst = [1,24,25,12,91]
lst1 = [1,2,3]
lst2 = [1,2,4,5,6]

# Find sum of list elements 
def lstsum():
    print(np.sum(lst))

lstsum()

# Largest element in a list 
def largestElement():
    res = lst[0]
    for element in lst:
        if element > res:
            res = element
    return res

print(largestElement())

# Remove Duplicates in a list 
def duplicates():
    new_lst = np.unique(lst)
    print(new_lst)

duplicates()

# Check if all elements in a list are unique 
def uniques(lst):
    new_lst = np.unique(lst)
    if len(new_lst) == len(lst):
        return True
    else: 
        return False
    
print(uniques([2,32,4,5]))
print(uniques([2,32,23,5,2]))

# Program to reverse list 
def reversed():
    return lst[::-1]

print(reversed())

# Count no of odd n even numbers in a list 
def oddorEven():

    count_even = 0
    count_odd = 0

    for element in lst:
        if element%2==0:
            count_even=count_even+1
        else: 
            count_odd+=1
    
    return count_even, count_odd

print(oddorEven())

# Check if a list is subset of another list 
def subset():
    set1 = set(lst1)
    set2 = set(lst2)
    return set1.issubset(set2)
    
print(subset())

#  Max diff btw two consecutive elements in a list 
def maxdeff():
    max_ele = max(lst2)
    min_ele = min(lst2)

    ans = abs(max_ele-min_ele)

    return ans

print(maxdeff())

# Merge Multiple dictionaries 
def my_dict():

    dict1 = {1:'a',2:'b'}

    dict2 = {3:'c',4:'d'}

    dict1.update(dict2)

    return dict1

print(my_dict())

# Find words frequency in a sentence
def maxCount():
    print(len("A Python dictionary is a data structure that stores the value in key: value pairs.".split()))

maxCount()