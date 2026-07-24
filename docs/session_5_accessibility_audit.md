# Session 5 — Accessibility Audit

## Question

Calculate the ratio and percentage of scheduled trips per route that explicitly guarantee:

- wheelchair accessibility; or
- bicycle storage through `bikes_allowed`.

Identify the routes with the lowest passenger-amenity availability.

## Relevant data

The analysis uses:

- `trips.route_id`
- `trips.trip_id`
- `trips.wheelchair_accessible`
- `trips.bikes_allowed`
- `routes.route_id`
- `routes.route_short_name`
- `routes.route_long_name`

The tables are connected through:

```text
trips.route_id → routes.route_id
```

## Initial data inspection

The distinct bicycle values in `trips` are:

| `bikes_allowed` | Number of trips | Interpretation |
|---|---:|---|
| `1` | 123,051 | At least one bicycle can explicitly be accommodated |
| `NULL` | 11,758 | No bicycle information is supplied |

There are no trips with `bikes_allowed = 2`, which would explicitly indicate that bicycles are not permitted.

The distinct wheelchair values are:

| `wheelchair_accessible` | Number of trips | Interpretation |
|---|---:|---|
| `NULL` | 134,809 | No wheelchair-accessibility information is supplied |

## Correct interpretation of missing values

According to the official GTFS Schedule reference:

- `bikes_allowed = 1` means the vehicle used for the trip can accommodate at least one bicycle.
- `bikes_allowed = 2` means bicycles are not allowed.
- `bikes_allowed = 0` or an empty value means that no bicycle information is available.
- `wheelchair_accessible = 1` means the vehicle can accommodate at least one wheelchair user.
- `wheelchair_accessible = 2` means wheelchair users cannot be accommodated.
- `wheelchair_accessible = 0` or an empty value means that no accessibility information is available.

Source: [Official GTFS Schedule reference](https://gtfs.org/documentation/schedule/reference/)

A `NULL` value must therefore be treated as **unknown**, not as an explicit absence of the amenity.

## Bicycle analysis

The coach noted that SNCB trains have bicycle wagons or bicycle accommodation. This can produce a result in which all identifiable train trips with supplied bicycle information score 100%.

The bicycle audit must not remove `NULL` values before calculating a route's total number of trips. Doing so leaves only `bikes_allowed = 1` records and automatically produces 100% for every remaining group.

At the same time, treating every `NULL` value as “bicycles not allowed” would also be incorrect. A lower percentage calculated from unknown records measures the completeness of the GTFS information, not necessarily the real availability of bicycle storage.

The route-level analysis should therefore distinguish between:

1. total scheduled trips;
2. trips explicitly marked with `bikes_allowed = 1`;
3. trips where bicycle information is unknown;
4. trips explicitly marked with `bikes_allowed = 2`, if any exist.

For the supplied data, the last group contains no records.

## Possible replacement-bus explanation

SNCB uses replacement buses during planned works and disruptions. SNCB states that only folding bicycles may be taken aboard replacement buses because of space and safety constraints.

Source: [SNCB replacement-bus FAQ](https://www.belgiantrain.be/fr/support/faq/faq-routes-schedules/faq-bus)

The exploratory SQL found that 10,714 trip identifiers contain a `BBUS` marker. All 10,714 belong to routes whose `route_short_name` is `BUS`, and all have missing bicycle information.

Another 1,044 trips do not contain `BBUS`, but also belong to routes labelled `BUS` and have missing bicycle information. Therefore, `route_short_name = 'BUS'` is a more complete classifier for bus services than parsing the internal `trip_id`.

The final distribution is:

| Service type | `bikes_allowed` | Number of trips |
|---|---:|---:|
| Train service | `1` | 123,051 |
| Bus service | `NULL` | 11,758 |

This establishes a complete separation in the supplied data: every train trip explicitly accommodates at least one bicycle, while every bus trip has an unknown bicycle status.

The GTFS specification does not define the SNCB-specific `BBUS` identifier. The combination of the `BBUS` pattern, the explicit `BUS` route label, and SNCB's published replacement-bus information makes the replacement-bus interpretation strongly supported, but the identifier itself was not found in the public GTFS documentation.

The following conclusion must not be made without further evidence:

> Every trip with `bikes_allowed IS NULL` is a replacement bus.

The missing value itself only proves that the static GTFS feed supplies no bicycle information for that trip.

More detail is recorded in:

```text
docs/replacement_bus_hypothesis.md
```

## Wheelchair-accessibility conclusion

All 134,809 scheduled trips have:

```text
wheelchair_accessible IS NULL
```

It is therefore impossible to compare wheelchair accessibility between routes using this dataset.

The correct conclusion is:

> The supplied GTFS data contains no explicit wheelchair-accessibility information for any scheduled trip. Consequently, the analysis cannot determine which trips or routes are wheelchair accessible, and it cannot produce a meaningful route-level wheelchair ranking.

The following statement would be incorrect:

> Zero percent of SNCB trips are wheelchair accessible.

The data reports an unknown status, not confirmed inaccessibility. This is a data-completeness limitation and not evidence about the accessibility of SNCB vehicles in practice.

## Final Session 5 conclusion

The final SQL groups the 134,809 scheduled trips into 1,801 routes and calculates, for every route:

- total scheduled trips;
- trips explicitly guaranteeing bicycle accommodation;
- trips with unknown bicycle information;
- trips explicitly guaranteeing wheelchair accessibility;
- trips with unknown wheelchair information;
- the ratio and percentage of trips explicitly guaranteeing wheelchair accessibility **or** bicycle accommodation.

The analysis reaches different conclusions for each service and feature:

| Service and feature | Final conclusion |
|---|---|
| Train bicycle accommodation | Confirmed for all 123,051 scheduled train trips |
| Bus bicycle accommodation | Unknown in the GTFS data for all 11,758 scheduled bus trips |
| Train wheelchair accessibility | Unknown |
| Bus wheelchair accessibility | Unknown |

All train routes score 100% for the combined explicit amenity guarantee because every train trip has `bikes_allowed = 1`. This confirms accommodation for at least one bicycle; it does not necessarily prove the presence of a dedicated bicycle wagon.

Bus routes score 0% for an **explicitly documented** combined guarantee because both relevant GTFS fields are missing. This must not be interpreted as proof that bus services provide neither amenity. It means that the supplied GTFS records do not explicitly document them.

Wheelchair accessibility cannot be compared between routes because `wheelchair_accessible` is `NULL` for all 134,809 trips. A zero explicit-guarantee count represents missing information, not confirmed inaccessibility.

Consequently, there is no uniquely lowest train route: all train routes are tied at 100%. The lowest documented scores belong to bus routes, which are tied at 0% because their amenity status is unknown.

## Saved SQL

The completed query is available in:

```text
sql/analysis/05_accessibility_audit.sql
```
