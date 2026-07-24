# Replacement buses and missing bicycle information

## Observation

The `trips` table contains:

- 123,051 trips with `bikes_allowed = 1`
- 11,758 trips with `bikes_allowed IS NULL`
- no trips with `bikes_allowed = 2`

All 134,809 trips have a `NULL` value for `wheelchair_accessible`.

## Confirmed interpretation

According to the official GTFS Schedule reference:

- `bikes_allowed = 1` means the vehicle used for the trip can accommodate at least one bicycle.
- `bikes_allowed = 2` means bicycles are not allowed.
- `bikes_allowed = 0` or an empty value means that no bicycle information is available for the trip.

Therefore, a `NULL` value must be interpreted as **unknown or not supplied**, not as evidence that bicycles are forbidden.

The same principle applies to `wheelchair_accessible`: an empty value means that the feed provides no accessibility information. It does not prove that the trip is inaccessible.

Source: [Official GTFS Schedule reference](https://gtfs.org/documentation/schedule/reference/)

## Replacement-bus hypothesis

SNCB uses replacement buses during planned works and network disruptions. SNCB states that passengers may take folding bicycles onto these buses, while ordinary bicycles are not accepted because of space and safety constraints.

Source: [SNCB replacement-bus FAQ](https://www.belgiantrain.be/fr/support/faq/faq-routes-schedules/faq-bus)

It is therefore plausible that replacement-bus services contribute to trips without an explicit bicycle guarantee. However, the `bikes_allowed` column alone cannot prove this relationship.

In particular, the following conclusion would be incorrect:

> `bikes_allowed IS NULL` means that the trip is operated by a replacement bus.

A missing value only shows that bicycle information was not supplied in the static GTFS record.

## How the hypothesis could be tested

Future analysis could try to identify replacement-bus trips using:

1. `routes.route_type = 3`, if SNCB records replacement services as bus routes.
2. Route or trip descriptions that mention replacement buses.
3. Distinctive route, trip, or block identifiers.
4. GTFS Realtime service alerts or other operational data.

After identifying likely replacement-bus trips, their `bikes_allowed` distribution could be compared with the distribution for rail trips.

## Project conclusion

For the current accessibility audit, routes should be ranked using only trips that explicitly guarantee bicycle accommodation through `bikes_allowed = 1`. Missing values should remain classified as unknown.

The possibility that replacement buses contribute to missing bicycle information is a reasonable hypothesis and project limitation, but it should not be presented as a confirmed cause.
