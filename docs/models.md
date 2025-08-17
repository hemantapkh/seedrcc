# Data Models

All data returned from the Seedr API is parsed into clean, easy-to-use data models. These models provide type-hinted attributes for all documented API fields, making it easy to work with the responses in a structured and predictable way.

## Accessing Raw Data

All data models provide a `.raw()` method to access the original, unmodified dictionary from the server.

```python
# This example assumes you have a 'client' instance from a previous example
settings = client.get_settings()

# Access a typed attribute
print(settings.account.username)

# Access the raw, underlying dictionary
raw_data = settings.raw()
print(raw_data["account"]["username"]) 
```

## Models Reference

::: seedrcc.models
    options:
      show_root_heading: true
      show_source: false
      show_bases: false
