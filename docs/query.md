# query-dsl

A domain-specific language (DSL) for `GET` queries and a medium between REST and GraphQL.

**Use if you need:**

- cacheable `GET`-based queries (like REST)
- to filter and order records and select fields (like GraphQL)
- something trivial to implement
- highly readable queries
- something secure and unlikely to overload a server with a bad query

**Don't use if you need:**

- to filter on graph structures or any non-hierarchical data (consider GraphQL)
- other needs query-dsl doesn't cover (consider GraphQL)
- you don't need to filter records (consider plain REST)
- the server is not Python (**implementations in other languages is planned**)

For each set of filters and selects, there is a single query string, which can be cached.
This is done by deliberately restricting flexibility in how the queries are written.
(This includes requiring conjunctive normal form and a specific order of filters.)

### Example

No percent-encoding needed!

```text
GET https://site.io/cart?filter(count(lt)10|user.name(eq)john)&filter(price>30)&select=price,user.name
                         │            │    │    │             │                 │
                       filter         │    │    │             │                 │ 
                                     less  │    │             │                 │
                                           OR   │             │                 │
                                               subkey         │               select
                                                             AND                                
```

```text
GET https://site.io/data/product?filter(name(regex)table.*)&filter(length(gt)height)&order=price,count
                                               │                          │          │
                                             regex                   compare keys    │
                                                                                    sort
```

### Extras

- image transformations (crop, scale, flip, and rotate)
  e.g., `?crop=0,0x50,50&rotate=270&scale=0.5&quality=50&subsampling=0`
- easy handling of JSON data
- other goodies

## 🍁 Contributing

[New issues](https://github.com/dmyersturnbull/query-dsl/issues) and pull requests are welcome.
Please refer to the [contributing guide](https://github.com/dmyersturnbull/realized/blob/main/CONTRIBUTING.md)
and [security policy](https://github.com/dmyersturnbull/realized/blob/main/SECURITY.md).
Generated with tyrannosaurus: `tyrannosaurus new`
