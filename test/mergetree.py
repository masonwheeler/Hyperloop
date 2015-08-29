"""
Original Developer: Jonathan Ward
Purpose of Module: To provide data structure used for merging discrete elements
Last Modified: 8/13/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added MasterTree Class
"""

# Standard Modules:
import collections

# Our Modules:
import config


class MergeTree:
    """
    Stores the results of recursively applied binary operations on a list.

    If the binary operation fails on a pair of elements "left" and "right",
    update the elements, alternating between "left" and "right".
    If "left" and "right" cannot be updated, then update the subelements from
    which "left" and right" came, then regenerate "left" and "right".
    """
    right = None  # For storing the right child node
    left = None  # For storing the left child node
    data = None  # For storing the data internal to the node
    children_merger = None  # Function combines children's data into node data
    data_updater = None  # Function expands the data exposed by the node
    child_to_update = "left"  # State variable storing which child to update next
    is_right_exhausted = False  # State varible storing whether right child exhausted
    is_left_exhausted = False  # State variable storing whether left child exhausted

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

        if self.child_to_update == "left":
            is_left_updated = self.left.update_data()
            if is_left_updated:
                if not self.is_right_exhausted:
                    # If the right child is not exahusted, update it next
                    self.child_to_update = "right"
                return True
            else:
                # Since the left child could not be updated, label it exhausted
                self.is_left_exhausted = True
                if self.is_right_exhausted:
                    # If the right is also exhausted, then record failure
                    return False
                else:
                    # If the right is not yet exhausted, update right
                    self.child_to_update = "right"
                    return self.update_children()

        if self.child_to_update == "right":
            is_right_updated = self.right.update_data()
            if is_right_updated:
                if not self.is_left_exhausted:
                    # If the left child is not exhausted, update it next
                    self.child_to_update = "left"
                return True
            else:
                # Since the left child could not be updated, label it exhausted
                self.is_right_exhausted = True
                if self.is_left_exhausted:
                    # If the left is also exhausted, then record failure
                    return False
                else:
                    # If the left is not yet exhausted, update left
                    self.child_to_update = "left"
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
            is_data_updated = self.data_updater(self.data)
            if is_data_updated:
                return True
            else:
                any_children_updated = self.update_children()
                if any_children_updated:
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
        merge_result = self.children_merger(self.left.data, self.right.data)
        while merge_result == None:
            any_children_updated = self.update_children()
            if any_children_updated:
                merge_result = self.children_merger(self.left.data,
                                                    self.right.data)
            else:
                raise ValueError("Tried all potential merges without success.")
        return merge_result

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


class MasterTree:

    def objects_to_leaves(self, objects, data_updater):
        """Takes list of objects and initializes a list of MergeTrees."""
        leaves_list = [MergeTree(None, None, each_object, None, data_updater)
                       for each_object in objects]
        leaves = collections.deque(leaves_list)
        return leaves

    def merge_branchlayer(self, branch_layer, children_merger, data_updater):
        """Creates next layer of MergeTrees."""
        # Use Deque for performance, it has O(1) pops and appends on both
        # sides.
        next_branch_layer = collections.deque()
        while len(branch_layer) > 1:
            # Take first two branches and merge them
            left_branch = branch_layer.popleft()
            right_branch = branch_layer.popleft()
            data = None
            merged_branch = MergeTree(left_branch, right_branch, data,
                                      children_merger, data_updater)
            next_branch_layer.append(merged_branch)
        if len(branch_layer) == 1:
            # Take last branch and merge it with the result of the previous
            # merge
            right_branch = branch_layer.popleft()
            left_branch = next_branch_layer.pop()
            data = None
            merged_branch = MergeTree(left_branch, right_branch, data,
                                      children_merger, data_updater)
            next_branch_layer.append(merged_branch)
        return next_branch_layer

    def merge_all_objects(self, objects, children_merger, data_updater):
        """Recursively merges objects until list is completely merged."""
        branch_layer = self.objects_to_leaves(objects, data_updater)
        while len(branch_layer) > 1:
            #config.HOLDER += 1
            #print("On layer " + str(config.HOLDER))
            branch_layer = self.merge_branchlayer(branch_layer, children_merger,
                                                  data_updater)
        merged_objects = branch_layer[0]
        return merged_objects

    def __init__(self, objects_to_merge, children_merger, data_updater):
        root_merge_tree = self.merge_all_objects(objects_to_merge, children_merger,
                                                 data_updater)
        self.root = root_merge_tree.data

"""
#Testing Purposes
class Number:
    value = None
    times_updated = 0
    max_updates = 0
    
    def __init__(self, value, max_updates):
        self.value = value
        self.max_updates = max_updates

    def update_value(self):
        if self.times_updated < self.max_updates:
            print("updating value")
            print("original value: " + str(self.value))
            self.value -= 1
            print("new value: " + str(self.value))
            self.times_updated += 1
            print("times updated: " + str(self.times_updated))
            return True
        else:
            print("max updates reached")
            return False

    @staticmethod
    def merge_two_numbers(number_a, number_b):
        merged_value = number_a.value + number_b.value
        return merged_value

def numbers_merger(number_a, number_b):
    merged_value = Number.merge_two_numbers(number_a, number_b)
    if merged_value < 10:
        merged_number = Number(merged_value, number_a.max_updates)
        return merged_number
    else:
        return None

def number_updater(number):   
    is_number_updated = number.update_value()
    return is_number_updated


max_updates = 3
numbers = [Number(value, max_updates) for value in range(6)]
root_number = MasterTree(numbers, numbers_merger, number_updater).root
print("root value is: " + str(root_number.value))
"""
