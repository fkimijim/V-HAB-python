from abc import ABC, abstractmethod

class Sys(ABC):
    """
    Abstract base class representing a generic system object in V-HAB.
    """

    def __init__(self, parent, name):
        """
        Constructor for the Sys object.

        Args:
            parent (Sys): Parent system object.
            name (str): Name of this system.
        """
        self.sName = name
        self.oParent = None
        self.oRoot = None
        self.toChildren = {}  # Dictionary to hold child systems
        self.csChildren = []  # List to hold names of child systems
        self.iChildren = 0    # Number of child systems

        # Set the parent system
        if parent is not None:
            self.set_parent(parent)

    def set_parent(self, parent):
        """
        Sets the parent system and updates the hierarchy.

        Args:
            parent (Sys): Parent system object.

        Raises:
            ValueError: If the parent object is not a Sys instance.
        """
        if not isinstance(parent, Sys):
            raise ValueError("Parent object must inherit from 'Sys'!")

        # If changing parent, remove from old parent first
        if self.oParent is not None:
            self.oParent.remove_child(self)

        self.oParent = parent
        parent.add_child(self)

        # Set the root system from the parent
        self.oRoot = parent.oRoot

    def add_child(self, child):
        """
        Adds a child system to this system.

        Args:
            child (Sys): Child system object.

        Raises:
            ValueError: If the child object is not a Sys instance or has a different parent.
        """
        if not isinstance(child, Sys):
            raise ValueError("Child object must inherit from 'Sys'!")
        if child.oParent != self:
            raise ValueError("Child object must have its oParent attribute set to this system!")

        # Check for duplicate names
        if child.sName in self.toChildren:
            if self.toChildren[child.sName] == child:
                return  # Child already exists
            else:
                raise ValueError(f"A different child with the name '{child.sName}' already exists.")

        # Add the child to the dictionary and update the name list
        self.toChildren[child.sName] = child
        self.csChildren.append(child.sName)
        self.iChildren += 1

    def remove_child(self, child):
        """
        Removes a child system from this system.

        Args:
            child (Sys): Child system object.

        Raises:
            ValueError: If the child object is not in this system or has a non-empty parent.
        """
        if not isinstance(child, Sys):
            raise ValueError("Child object must inherit from 'Sys'!")
        if child.sName not in self.toChildren:
            raise ValueError("Object is not a child of this system.")
        if child.oParent is not None:
            raise ValueError("Child object must have an empty oParent to be removed.")

        # Remove the child
        del self.toChildren[child.sName]
        self.csChildren.remove(child.sName)
        self.iChildren -= 1

    def get_child(self, index):
        """
        Retrieves a child system by name or position.

        Args:
            index (str or int): Name or index of the child system.

        Returns:
            Sys: The requested child system, or None if not found.
        """
        if isinstance(index, str):
            return self.toChildren.get(index, None)
        elif isinstance(index, int):
            if 0 <= index < len(self.csChildren):
                return self.toChildren[self.csChildren[index]]
        return None

    def is_child(self, index):
        """
        Checks if the given object or name is a child of this system.

        Args:
            index (str or Sys): Name or object to check.

        Returns:
            bool: True if the object or name is a child, False otherwise.
        """
        if isinstance(index, Sys):
            return index.sName in self.toChildren and self.toChildren[index.sName] == index
        elif isinstance(index, str):
            return index in self.toChildren
        return False
