# Realized

[![Version status](https://img.shields.io/pypi/status/realized?label=status)](https://pypi.org/project/realized)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build (Actions)](https://img.shields.io/github/workflow/status/dmyersturnbull/realized/Build%20&%20test?label=Tests)](https://github.com/dmyersturnbull/realized/actions)

_Realized_ is a collection of human-readable string serializations for common entities.
It builds on existing standards, restricting as needed to get unambiguous representations.
JSON- and NTFS filename-safe.

Done. Decisions made. This is how you represent things.

Each representation is a dataclass equipped with a `normalize()` method, along with some obviously named extras.

```python
UtcInstant("2022-09-01T00:22:56-02:00").normalize()  # "2022-09-01T00:20:56Z"
UtcInstant("2022-09-01T00:22:56:02:00").compact()  # NTFS-safe; "2022-09-01T002056Z"
UtcInstant("2022-09-01T00:22:56:02:00").squish()  # "20220901T002056Z"
UtcInstant(datetime(2022, 9, 1, 0, 22, 56).astimezone())
OffsetInstant("2022-09-01T00:22:56-02:00").normalize()  # "2022-09-01T00:22:56-02:00"
ZonedInstant("2022-09-01T00:22:56-08:00 [America/Los_Angeles]").normalize()
Duration("P80S").normalize()  # "PT1M20S"
Duration("P1Y")  # error! inexact duration
Duration("P80.5S").total_seconds()  # 80.5
2 * Duration("P3S") - Duration("1S")  # Duration("P5S")
Duration("P5S") - Duration("3S")  # Duration("P2S")
Recurring("PT1H (n=2)").normalize()  # "PT1H (n=2)" (2 times total)
UtcInstant("2022-09-01T00:00:00Z") + Duration("P5S")  # hey look! math!
HmsDuration("00:20:30.100").to_duration()  # "PT20M30.1S"
UnitDuration("5 millisecond").to_duration()  # "PT0.005S"
Time("5.2 nanosecond").normalize()  # "5.2 ns"
Length("1 inch").normalize()  # "25.4 mm" thanks to pint
Uncertain("3.14+/-0.1").normalize()  # "3.14±0.1"  thanks to uncertainties
Well8x12("A01")  # microwell plates
WellRange8x12("C01-C11; C12; A01-A12").normalize()  # "A01-A12;C01-C12
Json('{"b": "1", "a" "2"}').normalize()  # '{"a":"2","b":"1"}'
```

## Durations

These represent an amount of time _taken_, generally computed as the difference between two times from the same
monotonic clock. For example:

```python
import time
from realized import Duration

t0 = time.monotonic()
time.sleep(1)
delta = time.monotonic() - t0

duration = Duration.from_seconds(delta)
print(duration.iso8601)  # PT1S
```

### restricted subset of ISO 8601 periods

Forbids years, months, and weeks. Always require `T` for time (e.g. `PT1H` rather than `P1H`).

Input:

```regexp
^P(\d+D)??T(\dH)??(\d+M)??(\d+(?:[.,]\d{3,9})?S)??$
```

Normalized:

```regexp
^P(\d+D)??T((?:[12]\d|\d)H)??((?:[12]\d|\d)M)??((?:[12]\d|\d)(?:\.\d{3,9})?S)??$
```

Normalization procedure:

1. Omit zero nodes: `P1W0DT8H` ⟶ `P1W8D`
2. Full stop, not comma: `PT0,5S` ⟶ `PT0.5S`
3. Don't go over: `PT70M` ⟶ `PT1H10M`
4. Fractional only for seconds: `P0.5D` ⟶ `PT12H`

### hour:minute:second

Input:

```regexp
^\d{2,}:(?:[12]\d|\d):(?:[12]\d|\d)(?:\.\d{0,9})?$
```

Normalized:

```regexp
^\d{2,}:(?:[12]\d|\d):(?:[12]\d|\d)(?:\.\d{1,9})?$
```

### Quantity with units

Input:

```regexp
^[\d\s]+(?:\.[\d\s]+)?\[?(day|hour|hr|minute|min|second|millisecond|microsecond|nanosecond|sec|s|ms|µs|ns)\]?$
```

Normalized:

```regexp
^\d+(?:\.\d+)? (day|hour|minute|s|ms|µs|ns)$
```

Examples:

- `1.5 [hr]`
- `2 [nanosecond]`

## Dimensioned values

### Quantity with unit (SI plus a few)

## Datetimes

### UTC

Input:
Most of ISO 8601

Normalized:

```regexp
^\d{4}-\d{2}-\d{2}T\d{2}:?\d{2}:?\d{2}\.\d{3,9}Z$
```

Normalized (condensed form):

```regexp
^\d{8}T\d{6}\.\d{3,9}Z$
```

### With offset

Normalized:

```regexp
^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,9}[+−]\d{2}:\d{2}$
```

### With offset and IANA timezone

Input:

```regexp
^\d{4}-?\d{2}-?\d{2}[T_]\d{2}:?\d{2}:?\d{2}\.\d{3,9}[+−]\d{2}:\d{2}\s*\[[A-Z]+/[A-Za-z_]+\]$
```

Normalized:

```regexp
^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}[+−]\d{2}:\d{2} \[[A-Z]+/[A-Za-z_]+\]$
```

## Intervals

Represent a start and end time.
In general, end − start != duration !
NTP sync events, Daylight Saving Time start/end, or the user got on a plane.

One of the above, separated by a `--`.
For example: `2022-02-26T22:55:46.22562−08:00--2022-02-26T22:55:46.22562−08:00`

## Repeating periods (_experimental_)

- `PT30S--PT30.2S (n=5)`
- `00:00:30--00:00:30.2 (n=5)`
- `30[s]--3.2[s] (n=5)`

## Microplate wells

Normalized:

```regexp
^[A-Z]{1,2}\d{1,2}$
```

Normalization procedure:

- Balk if the number of digits doesn't match (e.g. `H1` instead of `H01`)

- 6-well: rows `A` to `B` and columns `1` to `3`; e.g. `B3`
- 12-well: rows `A` to `C` and columns `1` to `4`; e.g. `C4`
- 24-well: rows `A` to `D` and columns `1` to `6`; e.g. `D6`
- 48-well: rows `A` to `F` and columns `1` to `8`; e.g. `F8`
- 96-well: rows `A` to `H` and columns `01` to `12`; e.g. `H12`
- 384-well: rows `A` to `P` and columns `01` to `24`; e.g. `B24`
- 1536-well: rows `AA` to `BF` and columns `01` to `48`; e.g. `BF48`
- 3456-well: rows `AA` to `BV` and columns `01` to `72`; e.g. `BV72`

## Microplate well range

```
<row>   ::= [A-Z]{[A-Z]}
<col>   ::= <digit>{<digit>}
<point> ::= <row><col>
<op>    ::= '-'|'*'|'..'
<range> ::= <point> [<op> <point>]
<multi> ::= <range> {',' <range>}
```

Normalization procedure:

1. Replace >2 consecutive cells with ranges: `A01,A02,A03` ⟶ `A01-A03` and `A01,B02,C01` ⟶ `A01-C01`
2. Replace adjacent ranges: `A01-A10,B01-B10` ⟶ `A01*B10` and `A01-D01,A02-D02` ⟶ `A01*D02`
3. Replace adjacent blocks: `A01*C12,D01,F12` ⟶ `A01*F12`

Operators:

- Range in a single row: `A02-A12`
- Range in a single column: `A01-G01`
- Rectangular block: `A02\*G11
- Read like a book: `A01..C04`
- Pick and choose: `A01,C04`
- Comma-separated ranges: `A01-A12;C01-C12;G10..H12`
- All the above: `A01;A04;B01*H11;A01-H01`

## Other

- file formats: use media types
- codecs: HTML `<video />` element `codecs` value that Chrome accepts
- hash function names lowercase, without `-`: `crc32`, `md5` `sha1`, `sha256`, `sha512`, `sha3-224`, `sha3-256`,
  `sha3-384`, `sha3-512`, `shake128-<n>`, `shake256-<n>`, `blake2`, `blake2b`, `blake3`
- Always encode hash digests as base64
- UTF: `utf-8`, `utf-16`, `utf-32`
- Data types: `^([<>][?hHiIlLqQnNfdsp][1248]?)|utf-8|utf-16|utf-32$`
  per [Python struct](https://docs.python.org/3.11/library/struct.html#format-character)
- Turn literally everything into base64 and stuff those bytes into JSON
- Use CommonMark plus extensions everywhere :)

## 🍁 Contributing

[New issues](https://github.com/dmyersturnbull/realized/issues) and pull requests are welcome.
Please refer to the [contributing guide](https://github.com/dmyersturnbull/realized/blob/main/CONTRIBUTING.md)
and [security policy](https://github.com/dmyersturnbull/realized/blob/main/SECURITY.md).
Generated with tyrannosaurus: `tyrannosaurus new tyrannosaurus`
