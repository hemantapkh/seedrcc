# Exceptions

This page contains the reference for all custom exceptions.

## Handling Errors

All exceptions raised by `seedrcc` inherit from the base exception `seedrcc.exceptions.SeedrError`. This allows you to catch all errors from the library with a single `try...except` block, while still being able to handle specific error types differently.

Here is a example of how you can handle various exceptions:

```python
import seedrcc

try:
    # This operation might fail for various reasons
    client.add_torrent("some-magnet-link")

except seedrcc.exceptions.APIError as e:
    # Handle specific API errors (e.g., invalid magnet)
    print(f"An API error occurred: {e}")
    print(f"Error Type: {e.error_type}, Code: {e.code}")

except seedrcc.exceptions.AuthenticationError as e:
    # Handle authentication failures (e.g., invalid token)
    print(f"An authentication error occurred: {e}")

except seedrcc.exceptions.SeedrError as e:
    # Catch any other library-specific errors
    print(f"An unexpected error occurred with seedrcc: {e}")
```

## Exception Reference

::: seedrcc.exceptions
    options:
      show_root_heading: true
      show_source: true
      show_bases: true
