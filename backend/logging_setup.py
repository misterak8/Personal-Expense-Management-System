import logging
from functools import wraps

# Function to set up and return a logger object.
# - name: Name of the logger (usually __name__ of the module).
# - log_file: File where logs will be written (default: 'server.log').
# - level: Logging level (default: DEBUG).

def setup_logger(name, log_file='server.log', level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

# Decorator factory to log function calls with their arguments.
# - logger: Logger object to use for logging.
def log_function_call(logger):
    # The actual decorator
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Format positional and keyword arguments for logging
            formatted_args = []
            for arg in args:
                if isinstance(arg, str):
                    formatted_args.append(f"'{arg}'")
                else:
                    formatted_args.append(str(arg))

            for k, v in kwargs.items():
                if isinstance(v, str):
                    formatted_args.append(f"{k}='{v}'")
                else:
                    formatted_args.append(f"{k}={v}")

            # Log the function name and arguments
            logger.info(
                f"{func.__name__} called with {', '.join(formatted_args)}"
            )
            # Call the original function
            return func(*args, **kwargs)

        return wrapper

    return decorator
