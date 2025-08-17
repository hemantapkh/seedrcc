# Data Models

This library uses data models to represent both the authentication token and the data returned from the Seedr API.

## The Token Object

The `Token` object is a central piece of the client, holding the authentication credentials for your session. It's designed to be a simple, immutable data container that can be easily serialized and deserialized.

::: seedrcc.token.Token
    options:
      show_root_heading: true
      show_source: false
      show_bases: false
      filters: ["!^_"]

## API Response Models

All data returned from the Seedr API is parsed into clean, easy-to-use data models. These models provide type-hinted attributes for all documented API fields, making it easy to work with the responses in a structured and predictable way.

### Accessing Raw Data

All API response models provide a `.get_raw()` method to access the original, unmodified dictionary from the server.

```python
# This example assumes you have a 'client' instance from a previous example
settings = client.get_settings()

# Access a typed attribute
print(settings.account.username)

# Access the raw, underlying dictionary
raw_data = settings.get_raw()
print(raw_data["account"]["username"])
```

### Models Reference

::: seedrcc.models
    options:
      show_root_heading: true
      show_source: false
      show_bases: false
