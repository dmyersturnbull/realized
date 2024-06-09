# Realized

[![Version status](https://img.shields.io/pypi/status/realized?label=status)](https://pypi.org/project/realized)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build (Actions)](https://img.shields.io/github/workflow/status/dmyersturnbull/realized/Build%20&%20test?label=Tests)](https://github.com/dmyersturnbull/realized/actions)

Canonical, human-readable string representations for datetimes, durations, intervals, microplates, and more.

Prescribes a unique, unambiguous, human-readable, easily typed, and easily parsed representation for any single entity.
It builds on existing standards, restricting as needed to get unique representations.

- UTC instant: `2022-09-01T00:22:56Z` (RFC 3339 subset)
- instant with offset: `2022-09-01T00:22:56-02:00` (RFC 3339 subset)
- instant with IANA zone: `2022-09-01T00:22:56-02:00 [America/Los_Angeles]` (commonplace)
- duration: `P365DT59M59.5S` (ISO 8601 subset)
- interval: `2022-09-01T00:22:56+00:00--2022-09-01T00:22:56+00:00` (ISO 8601 subset)
- repeating interval: `R5/2022-09-01T00:22:56Z+00:00--2022-09-01T00:22:56+00:00` (ISO 8601 subset)
- repeating event: `R5/P365D` (like ISO 8601)
- repeating period: `R5/P30D--P60D` (like ISO 8601)
- microplate well: `A01` (commonplace)
- microplate well set: `A01-A12`, `A01-H01`, `A01*D3`, `A01...B6`, `A01,B02,C03` (custom)
- image coordinates: `(0,0)x(5,5)` (where 0,0 is top left)
- dimensioned value: `9.80665 m/s^2` ([Pint](https://pypi.org/project/Pint/) subset)

```python
from realized import SECOND, InstantUtc, Well8x12, WellSet8x12

dt = InstantUtc[SECOND].from_str("2022-09-01T00:22:56Z")
Well8x12.from_index(1).as_str  # A01
WellSet8x12.from_str("A01-A03").wells  # A01, A02, A03
```

## Durations

Uses a restricted subset of ISO 8601 periods.
Forbids years, months, and weeks. Always requires `T` for time (e.g. `PT1H` rather than `P1H`).

```python
from realized import Duration

duration = Duration.from_seconds(55)
print(duration.to_str)  # PT1S
```

### Extra format: hour:minute:second

Input:

```regexp
^\d{2,}:(?:[12]\d|\d):(?:[12]\d|\d)(?:\.\d{1,9})?$
```

## Dimensioned values

Quantity with unit (SI plus a few).

## UTC instant

Input: RFC 3339 with a `Z`.

### With offset

Input: RFC 3339 with a UTC offset.
Uses `-` for minus, and forbids negative UTC (`-00:00`).

### With city

Offset plus IANA timezone in square brackets.
Uses `-` for minus, and forbids negative UTC (`-00:00`).

## Intervals (UTC, with offset, or with city)

Represent a start and end time.
In general, end − start != duration !
NTP sync events, Daylight Saving Time start/end, or the user got on a plane.

One of the above, separated by a `--`.
For example: `2022-02-26T22:55:46.22562-08:00--2022-02-26T22:55:46.22562-08:00`

## Repeat interval

ISO 8601 repeating interval.

Repeats 4 times, for 5 total intervals:
`R4/2022-02-26T22:55:46-08:00--2023-02-26T22:55:46-08:00`

## Repeat event

Happens every 30 sec:
`R4/PT30S`

## Repeat duration

Happens every 30 sec and lasts for 2 sec, starting at 28 sec:
`R4/PT28S--PT30S`

## Microplate wells

Normalized:

```regexp
^[A-Z]{1,2}\d{1,3}$
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

## Microplate well sets

Normalization procedure:

TODO

Operators:

- Range in a single row: `A02-A12`
- Range in a single column: `A01-G01`
- Rectangular block: `A02*G11`
- Read like a book: `A01...C04`
- Pick and choose: `A01,C04`
- Comma-separated: `A01,C01`

## 🍁 Contributing

[New issues](https://github.com/dmyersturnbull/realized/issues) and pull requests are welcome.
Please refer to the [contributing guide](https://github.com/dmyersturnbull/realized/blob/main/CONTRIBUTING.md)
and [security policy](https://github.com/dmyersturnbull/realized/blob/main/SECURITY.md).
Generated with tyrannosaurus: `tyrannosaurus new`
