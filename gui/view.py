import tkinter
import tkinter.ttk

class ObjectViewer(tkinter.Frame):
    """
    Visualizes a object by creating a `tkinter.ttk.TreeView` object by creating sub-directories
    and attributes inside it recursively. Arrays are notated with `(n)` (where `n` is the index).
    """
    def __init__(self, master= None):
        super().__init__(master)
        self.pack(expand=True, fill='both', side='left')

    def insert_props(self, tree_root, parent, props: dict):
        for (k,v) in props.items():
            if type(v) == dict:
                subdir = tree_root.insert(parent, 'end', text= k)
                self.insert_props(tree_root, subdir, v)
            else:
                if type(v) == list or type(v) == tuple:
                    subdir = tree_root.insert(parent, 'end', text= k, values= ('', type(v).__name__))
                    self.inset_arr(tree_root, subdir, v)
                else:
                    tree_root.insert(parent, 'end', text= k, values= (v, type(v).__name__))

    def inset_arr(self, tree_root, parent, arr):
        for (i, v) in enumerate(arr):
            if type(v) == list or type(v) == tuple:
                subdir = tree_root.insert(parent, 'end', text= f'({i})', values=('', type(v).__name__))
                self.inset_arr(tree_root, subdir, v)
            else:
                tree_root.insert(parent, 'end', text= f'({i})', values= (v, type(v).__name__))

    def display_info(self, config: dict):
        dict_tree = tkinter.ttk.Treeview(self)
        dict_tree['columns'] = ('val', 'type')

        dict_tree.heading('#0', text= 'Key')
        dict_tree.heading('val', text= 'Value')
        dict_tree.heading('type', text= 'Type')

        self.insert_props(dict_tree, '', config)
        dict_tree.pack(expand=True, fill= 'both')