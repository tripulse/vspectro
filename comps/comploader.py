class ImmutableComponent(Exception):
    def __init__(self, name: str):
        super().__init__(f"{name} component is not mutable, it's immutable.")

class ComponentNotFound(Exception):
    def __init__(self, name: str):
        super().__init__(f"{name} component isn't registered or deleted!")

class ComponentExists(Exception):
    def __init__(self, name: str):
        super().__init__(f"{name} component already exists in database")

class ComponentContext:
    """
    An abstraction to manual component management. It can register, access,
    delete, modify components internally. Components come in two variants
    as mutable or immutable.

    Every component regardless of their type can be registered and acessed.
    
    - Mutable components can delete or modify.
    - Immutable components inherit the common traits of a component.
    """
    _components = {}

    def __init__(self):
        pass

    def register(self, name: str, ref, mutable: bool= False):
        """
        Registers a component to the database along with its refrence and
        mutability and name of it to register.
        """
        try:
            if self._components[name]:
                raise ComponentExists(name)
        except KeyError: pass

        self._components[name] = {'mut': mutable, 'ref': ref}


    def modify(self, name: str, ref):
        """
        Modifies the component's reference based on its name (works if the
        component is mutable).
        """
        try: self._components[name]
        except KeyError: raise ComponentNotFound(name)
        
        if self._components[name]['mut'] is False:
            raise ImmutableComponent(name)
        
        self._components[name]['ref'] = ref

    def access(self, name: str):
        """Access a component registered before with a arbitary name."""
        try: self._components[name]
        except KeyError: raise ComponentNotFound(name)
        return self._components[name]['ref']

    def delete(self, name: str):
        """Deletes the component registered before with a arbitary name. Note that, if you delete the component
        then you won't be able to get it back unless it gets registered again."""
        try: self._components[name]
        except: raise ComponentNotFound(name)
        
        if self._components[name]['mut'] is False:
            raise ImmutableComponent(name)

        # Delete the key and its value from the heap storage.
        # The garbage collector would it for us.
        del self._components[name]
