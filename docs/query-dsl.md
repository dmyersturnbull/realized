# Query DSL

## Idea

I wanted to sketch out what a query language over HTTP `GET` for filtering records from REST-like resources
would look like as an alternative to GraphQL.

### Goals

- Queries must be URI-safe. _They must not require percent encoding._ †
- It must be easier to use and easier to implement than GraphQL.
- It must fit naturally into `GET` parameters.
- It must support normalization to cache keys.
- It must support standard comparison operators, including `=`, `<`, and `>`, as well as regex matching.
- It must support the standard logical operators `&` and `|`.
- It must understand missing values, e.g., through a `NULL` type.

### Non-goals

- It does not need to be as flexible as GraphQL.
- It need not allow selecting which fields are returned (only which records).


### † URI safety

The characters `-`, `~`, `.`, `_`, `=`, `?`, `/`, `!`, `$`, `+`, `'`, `(`, `)`, `*`, `+`, and `,`
do not require percent encoding when used in a URI _query_
according to [RFC 3986](https://datatracker.ietf.org/doc/html/rfc3986).

!!! bug "`urlencode`"

    Many `urlencode` implementations will encode these characters regardless.

!!! note "Note 1"

    This is because the 1994 [RFC 1738](https://datatracker.ietf.org/doc/html/rfc1738) for URLS,
    which RFC 3986 obsoletes, had this language:

    > Thus, only alphanumerics, the special characters "$-_.+!*'(),",
      and reserved characters used for their reserved purposes may be used unencoded within a URL.

    RFC 3986 instead says:

    > If data for a URI component would conflict with a reserved character’s purpose as a delimiter,
      then the conflicting data must be percent-encoded before the URI is formed.

    `urlencode` implementations are not smart enough to understand this.
    Smart URI `urlencode` implementations could be introduced under new names such as `uriencode`
    without breaking backwards compatibility.
    I don’t know why that hasn’t happened.

!!! note "Note 2"

    Technically, RFC 3986 splits reserved characters into two sets, `gen-delims` and `sub-delims`:

    ```abnf
       gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"
       sub-delims  = "!" / "$" / "&" / "'" / "(" / ")" / "*" / "+" / "," / ";" / "="
       unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
    ```

    It then specificially forbids using `gen-delims` anywhere outside of their reserved meanings,
    but also says about query strings:

    > The characters slash ("/") and question mark ("?") may represent data within the query component.
      Beware that some older, erroneous implementations may not handle such data correctly [...]

    So, the full set of allowed characters in URI queries is

    ```abnf
    unreserved / sub-delims / "/" / "?"`.
    ```

!!! note "Note 3"

    Ok, fine. RFC 3986 also says:

    > [RFC 3986] excludes portions of RFC 1738 that defined the specific syntax of individual URI schemes;
      those portions will be updated as separate documents.

    The HTTP-specific part of RFC 1738 states (where `(<searchpart>` means `query`):

    > Within the <path> and <searchpart> components, "/", ";", "?" are reserved.
      The "/" character may be used within HTTP to designate a hierarchical structure.

    So there is no HTTP-specific ban on our `sub-delims`.

## Grammar

**Conventions:**

- Lexer rules are in uppercase.
- Lexer fragments start with `_`.
- "Basal" lexer rules (to be interpreted before anything else) start and end with `_`.
  (In any real implementation, this would be performed beforehand.)

```ebnf title="EBNF notation"
query
   = [ filter { "&" filter } ]
   ;
filter
   = "filter" "(" condition { "|" condition } ")"
   ;
condition
   = key EQ_VERB ( STR | FLOAT | BOOL | NULL )
   | key STR_VERB STR
   | key FLOAT_VERB FLOAT
key
   = _NORMAL_CHAR { _NORMAL_CHAR | _HYPEN }
   ;
STR
   = "'" { _CHAR | _OCTET_ } "'"
   ;
EQ_VERB
   = "(eq)" | "(neq)"
   ;
STR_VERB
   = "(regex)"
   ;
FLOAT_VERB
   = "(lt)" | "(gt)"
   ;
FLOAT
   = [_HYPEN] {DIGIT}-
   | [_HYPEN] {DIGIT}- "." {DIGIT}-
   ;
NULL
   = "null"
   ;
BOOL
   = "true"
   | "false"
   ;
_CHAR
   = _NORMAL_CHAR | _SPECIAL
   ;
_HYPHEN
   = "-"
   ;
_NORMAL_CHAR
   = _DIGIT | _UPPERCASE | _LOWERCASE | "_" | "." | "~"
   ;
_SPECIAL
   = "=" | "!" | "$" | "+" | "(" | ")" | "*" | "+" | "," | "/" | "?"
   ;
_DIGIT
   = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
   ;
_UPPERCASE
   = "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M"
   | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"
   ;
_LOWERCASE
   = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m"
   | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
   ;
_OCTET_
   = "%" _HEX_ _HEX_
   ;
_HEX_
   = DIGIT
   | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H"
   ;
```

Note that `.` in keys is meant for hierarchical access;
`null` is the value if any node along the path is not present.
Although reserved characters are technically allowed in keys, they should not be used.

Also note that the grammar restricts queries to conjunctive normal form!

## Example

```http
GET https://things.tld/food?filter=(type(eq)fruit|grams(lt)5.0|grams(gt)20.0)&filter(name(full-match)'.+?apple') HTTP/3
Content-Type: text/json
```

A few things to note:

- The same set of keys is not permitted in separate disjunctive clauses.
  For example, `filter(size(lt)5)&filter(size(eq)5)` and `filter(a(eq)1|b(eq)2)` not allowed.
- Regex strings are left as-is.
  This causes the only cases of (linguistic) semantic equivalence between nonidentical normalized queries.

## Normalization

The server normalizes this to a cache key by normalizing:

1. Split clauses by `&` and sort them.
2. Within each clause, split by `|` and sort them.
3. Trailing zeros are stripped off of decimal values.

The example above results in the cache key

```text
food?filter(grams(gt)20|grams(lt)5|type(eq)fruit)&filter(name(regex)'.+?apple')
```

## Selecting

`&select=key1,key2`

## Sorting

- `&sort=key1.subkey,key2,-key3`, where `-` means descending

Look for `&sort=`, split by `,`, and use:

```regexp
(?P<descending>-?)(?P<key>[_.~A-Za-z0-9][-_.~A-Za-z0-9]+)
```

## Pagination

`&offset=10&limit=40`
