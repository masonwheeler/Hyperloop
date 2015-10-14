"""
Original Developer: Jonathan Ward
Purpose of Module: To provide data structure used for merging discrete elements
Last Modified: 8/13/15
Last Modified By: Jonathan Ward
Last Modification Purpose: Added MasterTree Class
"""

#pylint: disable=R0913

# Standard Modules:
import collections

class MergeTree(object):
    """
    Stores the results of recursively applied binary operations on a list.

    If the binary operation fails on a pair of elements "left" and "right",
    update the elements, alternating between "left" and "right".
    If "left" and "right" cannot be updated, then update the subelements from
    which "left" and right" came, then regenerate "left" and "right".
    """

    def update_left_child(self, children_merger, data_updater):
        """Attempts to update the left child node
        """
        is_left_updated = self.left.update_data(children_merger, data_updater)
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
                return self.update_children(children_merger, data_updater)

    def update_right_child(self, children_merger, data_updater):
        """Attempts to update the right child node
        """
        is_right_updated = self.right.update_data(children_merger, data_updater)
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
                return self.update_children(children_merger, data_updater)

    def update_children(self, children_merger, data_updater):
        """
        Updates child nodes by alternating between right and left nodes.

        If the child nodes do not exist or do not have data, return False.
        If one of the child nodes is sucessfully updated, the function
        returns True, otherwise the function returns False.
        """
        if self.left == None or self.right == None:
            return False
        if self.left.data == None or self.right.data == None:
            return False

        if self.child_to_update == "left":
            self.update_left_child(children_merger, data_updater)

        if self.child_to_update == "right":
            self.update_right_child(children_merger, data_updater)

    def update_data(self, children_merger, data_updater):
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
            is_data_updated = data_updater(self.data)
            if is_data_updated:
                return True
            else:
                any_children_updated = self.update_children(children_merger,
                                                            data_updater)
                if any_children_updated:
                    self.data = self.merge_children(children_merger,
                                                    data_updater)
                    return True
                else:
                    return False

    def merge_children(self, children_merger, data_updater):
        """
        Merges Node's children, and updates until merge result is valid.

        If all of the children and subchildren are completely updated,
        without getting a valid result, then error is raised.
        Note that this case should not actually occur.
        """
        merge_result = children_merger(self.left.data, self.right.data)
        while merge_result == None:
            any_children_updated = self.update_children(children_merger,
                                                        data_updater)
            if any_children_updated:
                merge_result = children_merger(self.left.data,
                                               self.right.data)
            else:
                raise ValueError("Tried all potential merges without success.")
        return merge_result

    def get_data(self, init_data, children_merger, data_updater):
        """Builds the node's data either from its children or initial data
        """
        if init_data == None:
            if self.left == None or self.right == None:
                raise ValueError("Unitialized node lacks children.")
            if self.left.data == None or self.right.data == None:
                raise ValueError("Unitialized node's children lack data.")
            data = self.merge_children(children_merger, data_updater)
        else:
            data = init_data
        return data

    def __init__(self, left, right, init_data, children_merger, data_updater):
        self.is_right_exhausted = False
        self.is_left_exhausted = False
        self.child_to_update = "left"
        self.left = left
        self.right = right
        self.data = self.get_data(init_data, children_merger, data_updater)


class MasterTree(object):
    """Wrapper class which merges all objects
    """

    MAX_LAYER_DEPTH = 2

    @staticmethod
    def objects_to_leaves(objects, data_updater):
        """Takes list of objects and initializes a list of MergeTrees."""
        leaves_list = [MergeTree(None, None, each_object, None, data_updater)
                       for each_object in objects]
        leaves = collections.deque(leaves_list)
        return leaves

    @staticmethod
    def merge_branch_layer(branch_layer, children_merger, data_updater):
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
    
    ##@profile
    def merge_all_objects(self, objects, children_merger, data_updater):
        """Recursively merges objects until list is completely merged."""
        branch_layers = []
        new_branch_layer = MasterTree.objects_to_leaves(objects, data_updater)
        branch_layers.append(new_branch_layer)
        layer_index = 0
        while len(new_branch_layer) > 1:
            last_branch_layer = branch_layers[-1]
            new_branch_layer = MasterTree.merge_branch_layer(last_branch_layer,
                                        children_merger, data_updater)
            branch_layers.append(new_branch_layer)
            layer_index += 1 
        top_branch_layer = branch_layers[-1]
        merged_objects = top_branch_layer[0]
        return merged_objects

    def __init__(self, objects_to_merge, children_merger, data_updater):
        root_merge_tree = self.merge_all_objects(objects_to_merge,
                                          children_merger, data_updater)
        self.root = root_merge_tree.data
