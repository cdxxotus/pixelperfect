import time
import traceback

def expecto_patronum(func, *args, **kwargs):
    print("Expecto Patronum: Summoning a helper service to assist with the task.")

    # Analyze argument types
    print("Analyzing argument types:")
    for i, arg in enumerate(args):
        print(f"Arg {i}: Type: {type(arg)}, Value: {arg}")
    for key, value in kwargs.items():
        print(f"Kwarg {key}: Type: {type(value)}, Value: {value}")

    start_time = time.time()
    try:
        # Call the original function
        result = func(*args, **kwargs)

        # Analyze return value
        print("Analyzing return value:")
        print(f"Type: {type(result)}, Value: {result}")

        return result
    except Exception as e:
        # Handle and log exceptions
        print("An error occurred:")
        print(traceback.format_exc())
        raise e
    finally:
        # Measure and print execution time
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time:.4f} seconds")
