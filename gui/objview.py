import tkinter
import tkinter.ttk

class ObjectViewer(tkinter.Frame):
    """
    Visualizes a object by creating a `tkinter.ttk.TreeView` object by creating sub-directories
    and attributes inside it recursively. Note that, this is made to work with deserialized data
    into a Python `dict`, `list`, `tuple`, `any` object (e.g. `typing.NamedTuple`'s data would
    just be represented as a string not as a tree).
    """
    def __init__(self, master= None, src_dict= {}):
        super().__init__(master)

        dict_tree = tkinter.ttk.Treeview(self)
        dict_tree['columns'] = ('val', 'type')

        dict_tree.heading('#0', text= 'Key')
        dict_tree.heading('val', text= 'Value')
        dict_tree.heading('type', text= 'Type')

        # Transfer the visualization offloading to the actual
        # recursive function to insert trees.
        self.insert(dict_tree, '', src_dict)

        dict_tree.pack(expand=True, fill= 'both')
        self.pack(expand=True, fill='both', side='left')

    def insert(self, tree_root, parent, val):
        if type(val) == dict:
            for (k,v) in val.items():
                if type(v) == dict:
                    # If the value itself is a python a dict then
                    # call the function itself and iterate the dict.
                    subdir = tree_root.insert(parent, 'end', text= k)
                    self.insert(tree_root, subdir, v)
                else:
                    if type(v) == list or type(v) == tuple:
                        # If dict's value is a tuple or dict the offload the process to
                        # the array inserter.
                        subdir = tree_root.insert(parent, 'end', text= k, values= ('', type(v).__name__))
                        self.inset_arr(tree_root, subdir, v)
                    else:
                        # If the dict's value is single then insert with its 
                        # correspoding key and type.
                        tree_root.insert(parent, 'end', text= k, values= (v, type(v).__name__))
        
        # If the type is a Python list or tuple offload it
        # to the recursive array inserter for insertion.
        elif type(val) == tuple or type(val) == list:
            self.inset_arr(tree_root, parent, val)

        else:
            # If the thing is a single value object then insert
            # it without no property at all.
            tree_root.insert(parent, 'end', values= (val, type(val).__name__))

    def inset_arr(self, tree_root, parent, arr):
        for (i, v) in enumerate(arr):
            # If the type is a nested array call the function itself
            # and recusrively insert until a single value object/dict reaches.
            if type(v) == list or type(v) == tuple:
                subdir = tree_root.insert(parent, 'end', text= f'({i})', values=('', type(v).__name__))
                self.inset_arr(tree_root, subdir, v)
            else:
                # If the thing is a single value object or Python dict
                # then offload the insertion to the main inserter.
                self.insert(tree_root, parent, v)