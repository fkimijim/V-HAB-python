import uuid
from abc import ABC


class Base(ABC):
    """
    Base class for all objects in V-HAB.
    Provides common functionality such as UUID generation, metadata,
    and debug logging.
    """

    # Static debugger instance (shared across all instances)
    o_debug = None  # Placeholder for a debugging/logging system

    def __init__(self):
        """
        Constructor for the Base class.
        Initializes common properties like UUID, metadata, and class name.
        """
        # Avoid re-initialization if already initialized
        if hasattr(self, "s_uuid") and self.s_uuid:
            return

        # Generating the Universally Unique Identifier (UUID)
        self.s_uuid = str(uuid.uuid4())

        # Class name
        self.s_entity = self.__class__.__name__

        # URL for identification in logging
        self.s_url = f"/{self.s_entity.replace('.', '/')}/{self.s_uuid}"

        # Adding this object to the debug logger
        if Base.o_debug:
            Base.o_debug.add(self)

    def out(self, *args):
        """
        Outputs debug/log info.
        Args:
            args: Variable-length arguments for log level, verbosity, message, etc.
        """
        if not Base.o_debug or Base.o_debug.b_off:
            return

        # Parse arguments
        i_level, i_verbosity, s_identifier, s_message, c_params = self._parse_out_args(*args)

        # Pass to the debugger
        Base.o_debug.output(self, i_level, i_verbosity, s_identifier, s_message, c_params)

    def throw(self, s_ident, s_msg, *args):
        """
        Raises an error with additional context.
        Args:
            s_ident (str): Identifier for the error.
            s_msg (str): Error message.
            *args: Additional arguments for formatting.
        """
        raise ValueError(f"{self.s_url.replace('/', ':')}:{s_ident}: {s_msg % args}")

    def warn(self, s_ident, s_msg, *args):
        """
        Issues a warning with additional context.
        Args:
            s_ident (str): Identifier for the warning.
            s_msg (str): Warning message.
            *args: Additional arguments for formatting.
        """
        print(f"WARNING: {self.s_url.replace('/', ':')}:{s_ident}: {s_msg % args}")

    @staticmethod
    def flush():
        """
        Flushes all debug logs.
        """
        if Base.o_debug:
            Base.o_debug.flush()

    def _parse_out_args(self, *args):
        """
        Parses the arguments provided to the out method.
        Returns:
            tuple: Parsed log level, verbosity, identifier, message, and parameters.
        """
        # Default values
        i_level = 1
        i_verbosity = 1
        s_identifier = ""
        s_message = ""
        c_params = []

        args_iter = iter(args)

        # Parse log level and verbosity
        first_arg = next(args_iter, None)
        if isinstance(first_arg, int):
            i_level = first_arg
            second_arg = next(args_iter, None)
            if isinstance(second_arg, int):
                i_verbosity = second_arg
            else:
                s_message = second_arg if isinstance(second_arg, str) else ""

        # Parse identifier and message
        while s_message == "":
            next_arg = next(args_iter, None)
            if isinstance(next_arg, str):
                if s_identifier == "":
                    s_identifier = next_arg
                else:
                    s_message = next_arg

        # Parse parameters
        c_params = list(args_iter)

        return i_level, i_verbosity, s_identifier, s_message, c_params
