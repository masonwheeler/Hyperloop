"""
Original Developer: Jonathan Ward
Purpose of Module: To provide data structure used for merging discrete elements
Last Modified: 7/30/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added functions and classes for testing purposes
"""

import collections

import config

class MergeTree:
    """
    Stores the results of recursively applied binary operations on a list.

    If the binary operation fails on a pair of elements "left" and "right",
    update the elements, alternating between "left" and "right".
    If "left" and "right" cannot be updated, then update the subelements from
    which "left" and right" came, then regenerate "left" and "right".
    """
    right = None #For storing the right child node
    left = None #For storing the left child node
    data = None #For storing the data internal to the node
    children_merger = None #Function combines children's data into node data
    data_updater = None #Function expands the data exposed by the node
    childToUpdate = "left" #State variable storing which child to update next
    isRightExhausted = False #State varible storing whether right child exhausted
    isLeftExhausted = False #State variable storing whether left child exhausted

    def update_children(self):
        """
        Updates child nodes by alternating between right and left nodes.
        
        If the child nodes do not exist or do not have data, return False.
        If one of the child nodes is sucessfully updated, the function 
        returns True, otherwise the function returns False.        
        """
        if (self.left == None or self.right == None):
            return False
        if (self.left.data == None or self.right.data == None):
            return False

        if self.childToUpdate == "left":
            isLeftUpdated = self.left.update_data()
            if isLeftUpdated:
                if not self.isRightExhausted:                          
                    #If the right child is not exahusted, update it next
                    self.childToUpdate = "right"
                return True
            else:
                #Since the left child could not be updated, label it exhausted
                self.isLeftExhausted = True
                if self.isRightExhausted:
                    #If the right is also exhausted, then record failure
                    return False
                else:
                    #If the right is not yet exhausted, update right
                    self.childToUpdate = "right"
                    return self.update_children()

        if self.childToUpdate == "right":
            isRightUpdated = self.right.update_data()
            if isRightUpdated:
                if not self.isLeftExhausted:
                    #If the left child is not exhausted, update it next
                    self.childToUpdate = "left"
                return True
            else:
                #Since the left child could not be updated, label it exhausted
                self.isRightExhausted = True
                if self.isLeftExhausted:
                    #If the left is also exhausted, then record failure
                    return False
                else:
                    #If the left is not yet exhausted, update left
                    self.childToUpdate = "left"
                    return self.update_children()

    def update_data(self):
        """ 
        Updates the data associated with a node.

        If the node's data is successfully updated, return True,
        otherwise return False.
        If the node's data cannot be updated, update the node's children,
        then merge the updated children to get new data for the node.
        If the node's children cannot be updated, record failure.        
        """
        if self.data == None:
            return False  
        else:
            isDataUpdated = self.data_updater(self.data)
            if isDataUpdated:
                return True
            else:
                anyChildrenUpdated = self.update_children()
                if anyChildrenUpdated:
                    self.data = self.merge_children()
                    return True
                else:
                    return False
                
    def merge_children(self):
        """
        Merges Node's children, and updates until merge result is valid.

        If all of the children and subchildren are completely updated, 
        without getting a valid result, then error is raised.
        Note that this case should not actually occur.
        """
        mergeResult = self.children_merger(self.left.data, self.right.data)
        while mergeResult == None:
            anyChildrenUpdated = self.update_children()
            if anyChildrenUpdated:
                mergeResult = self.children_merger(self.left.data,
                                                   self.right.data)
            else:
                raise ValueError("Tried all potential merges without success.")       
        return mergeResult

    def get_data(self, data):
        if data == None:
            if (self.left == None or self.right == None):
                raise ValueError("Unitialized node lacks children.")
            if (self.left.data == None or self.right.data == None):
                raise ValueError("Unitialized node's children lack data.")
            self.data = self.merge_children()
        else:
            self.data = data

    def __init__(self, left, right, data, children_merger, data_updater):
        self.left = left
        self.right = right             
        self.children_merger = children_merger
        self.data_updater = data_updater         
        self.get_data(data)


def objects_to_leaves(objects, data_updater):  
    """Takes list of objects and initializes a list of MergeTrees.""" 
    leavesList = [MergeTree(None, None, eachObject, None, data_updater)
                  for eachObject in objects]
    leaves = collections.deque(leavesList)
    return leaves

def merge_branchlayer(branchLayer, children_merger, data_updater):
    """Creates next layer of MergeTrees."""
    #Use Deque for performance, it has O(1) pops and appends on both sides.
    nextBranchLayer = collections.deque()
    while len(branchLayer) > 1:
        #Take first two branches and merge them
        leftBranch = branchLayer.popleft()
        rightBranch = branchLayer.popleft()
        data = None
        mergedBranch = MergeTree(leftBranch, rightBranch, data, children_merger,
                                                                data_updater)
        nextBranchLayer.append(mergedBranch)
    if len(branchLayer) == 1:
        #Take last branch and merge it with the result of the previous merge
        rightBranch = branchLayer.popleft()
        leftBranch = nextBranchLayer.pop()
        data = None
        mergedBranch = MergeTree(leftBranch, rightBranch, data, children_merger,
                                                                data_updater)
        nextBranchLayer.append(mergedBranch)
    return nextBranchLayer
       
def merge_allobjects(objects, children_merger, data_updater):
    """Recursively merges objects until list is completely merged."""
    branchLayer = objects_to_leaves(objects, data_updater) 
    while len(branchLayer) > 1:
        config.holder += 1
        print("On layer " + str(config.holder))
        branchLayer = merge_branchlayer(branchLayer, children_merger,
                                                     data_updater)
    mergedObjects = branchLayer[0]
    return mergedObjects


#Testing Purposes
"""
class Number:
    value = None
    timesUpdated = 0
    maxUpdates = 0
    
    def __init__(self, value, maxUpdates):
        self.value = value
        self.maxUpdates = maxUpdates

    def update_value(self):
        if self.timesUpdated < self.maxUpdates:
            print("updating value")
            print("original value: " + str(self.value))
            self.value -= 1
            print("new value: " + str(self.value))
            self.timesUpdated += 1
            print("times updated: " + str(self.timesUpdated))
            return True
        else:
            print("max updates reached")
            return False


def numbers_merger(numberA, numberB):
    mergedValue = numberA.value + numberB.value
    if mergedValue < 10:
        mergedNumber = Number(mergedValue, numberA.maxUpdates)
        return mergedNumber
    else:
        return None

def number_updater(number):   
    isNumberUpdated = number.update_value()
    return isNumberUpdated

maxUpdates = 3
numbers = [Number(value, maxUpdates) for value in range(7)]
merged = merge_objects(numbers, numbers_merger, number_updater)
print("root value is: " + str(merged.data.value))
"""
