# RailPulse Table Structure

This document describes the seven core tables used to import and analyze the SNCB GTFS Static data.

- `PK`: Primary key
- `FK`: Foreign key
- `PK, FK`: The column is simultaneously part of a primary key and a foreign key
- A key containing multiple columns is a composite primary key
- `TEXT`: Character data, identifiers, dates, or GTFS times
- `INTEGER`: A whole number or a coded value
- `REAL`: A decimal number
- `NULL allowed`: The source can contain an empty value; import it as SQL `NULL`

GTFS identifiers must use `TEXT`, even when part of an identifier looks numeric. For example, `route_id` contains values such as `gr:nmbssncb:1005`. GTFS times also use `TEXT` because a service continuing after midnight can have a value such as `25:10:00`.

## agencies

Source: `agency.txt`

```text
(PK) agency_id (TEXT) - example: nmbssncb
agency_name (TEXT) - example: NMBS/SNCB
agency_url (TEXT) - example: http://www.belgiantrain.be/
agency_timezone (TEXT) - example: Europe/Brussels
agency_lang (TEXT) - example: fr
agency_phone (TEXT, NULL allowed)
agency_fare_url (TEXT, NULL allowed)
```

One agency can operate many routes.

## routes

Source: `routes.txt`

```text
(PK) route_id (TEXT) - example: gr:nmbssncb:1005
(FK) agency_id (TEXT) (agencies.agency_id) - example: nmbssncb
route_short_name (TEXT) - examples: IC, L, S
route_long_name (TEXT) - example: Bruxelles-Midi -- Genk
route_desc (TEXT, NULL allowed)
route_type (INTEGER) - GTFS transport type; see the coded values below
route_url (TEXT, NULL allowed)
route_color (TEXT, NULL allowed) - six-character hexadecimal color without #
route_text_color (TEXT, NULL allowed) - six-character hexadecimal color without #
```

One route can contain many trips.

GTFS route types relevant to the base specification:

- `0`: Tram or light rail.
- `1`: Subway or metro.
- `2`: Rail.
- `3`: Bus.
- `4`: Ferry.
- `5`: Cable tram.
- `6`: Aerial lift.
- `7`: Funicular.
- `11`: Trolleybus.
- `12`: Monorail.

The SNCB feed may contain both rail services and replacement bus services, so `route_type` should not be restricted to `2`.

## services

Source: `calendar.txt`

```text
(PK) service_id (TEXT) - example: gc:nmbssncb:000070
monday (INTEGER) - 0 or 1
tuesday (INTEGER) - 0 or 1
wednesday (INTEGER) - 0 or 1
thursday (INTEGER) - 0 or 1
friday (INTEGER) - 0 or 1
saturday (INTEGER) - 0 or 1
sunday (INTEGER) - 0 or 1
start_date (TEXT) - source format: YYYYMMDD; database format: YYYY-MM-DD
end_date (TEXT) - source format: YYYYMMDD; database format: YYYY-MM-DD
```

One service can apply to many trips and can have many service exceptions.

## service_exceptions

Source: `calendar_dates.txt`

Composite primary key: `service_id + exception_date`

```text
(PK, FK) service_id (TEXT) (services.service_id)
(PK) exception_date (TEXT) - source format: YYYYMMDD; database format: YYYY-MM-DD
exception_type (INTEGER) - allowed values: 1 or 2
```

The source field `date` is renamed to `exception_date` in the database for clarity. A service can have only one exception on a particular date.

GTFS exception types:

- `1`: Service was added for the specified date.
- `2`: Service was removed for the specified date.

## stops

Source: `stops.txt`

```text
(PK) stop_id (TEXT) - example: gs:nmbssncb:8813003_1
(FK) parent_station (TEXT, NULL allowed) (stops.stop_id) - example: gs:nmbssncb:S8813003
stop_code (TEXT, NULL allowed)
stop_name (TEXT) - example: Bruxelles-Central
stop_desc (TEXT, NULL allowed)
stop_lat (REAL) - WGS84 latitude from -90.0 through 90.0
stop_lon (REAL) - WGS84 longitude from -180.0 through 180.0
location_type (INTEGER) - GTFS location classification; see the coded values below
platform_code (TEXT, NULL allowed) - use TEXT because platform labels need not be numeric
stop_url (TEXT, NULL allowed)
wheelchair_boarding (INTEGER, NULL allowed) - GTFS coded value: 0, 1, or 2
zone_id (TEXT, NULL allowed)
```

`parent_station` is a self-referencing foreign key. It connects a platform or boarding stop to its main station. It can be empty for main station records.

GTFS location types:

- `0` or an empty source value: Stop or platform.
- `1`: Station.
- `2`: Station entrance or exit.
- `3`: Generic node within a station.
- `4`: Specific boarding area on a platform.

Empty `location_type` source values are normalized to `0` during ingestion.

GTFS wheelchair boarding values:

- `0` or `NULL`: No accessibility information.
- `1`: Some vehicles at this stop can board a rider in a wheelchair.
- `2`: Wheelchair boarding is not possible at this stop.

## trips

Source: `trips.txt`

```text
(PK) trip_id (TEXT) - example: gt:nmbssncb:BBUS__:049::8882206:8882107:2:1729:20260620
(FK) route_id (TEXT) (routes.route_id)
(FK) service_id (TEXT) (services.service_id)
trip_headsign (TEXT, NULL allowed) - passenger-facing destination text, for example: La Louviere-Centre
trip_short_name (TEXT, NULL allowed) - passenger-facing trip identifier, such as a train number
direction_id (INTEGER, NULL allowed) - GTFS coded value: 0 or 1
block_id (TEXT, NULL allowed) - keep as TEXT even if current values look numeric
shape_id (TEXT, NULL allowed)
wheelchair_accessible (INTEGER, NULL allowed) - GTFS coded value: 0, 1, or 2
bikes_allowed (INTEGER, NULL allowed) - GTFS coded value: 0, 1, or 2
```

Each trip belongs to one route and one service. A trip can contain many stop-time records.

GTFS wheelchair accessibility values:

- `0` or `NULL`: No accessibility information.
- `1`: The vehicle can accommodate at least one rider in a wheelchair.
- `2`: Riders in wheelchairs cannot be accommodated on this trip.

GTFS bicycle values:

- `0` or `NULL`: No bicycle information.
- `1`: The vehicle can accommodate at least one bicycle.
- `2`: Bicycles are not allowed on this trip.

## stop_times

Source: `stop_times.txt`

Composite primary key: `trip_id + stop_sequence`

```text
(PK, FK) trip_id (TEXT) (trips.trip_id)
(PK) stop_sequence (INTEGER) - non-negative position of the stop within the trip
(FK) stop_id (TEXT) (stops.stop_id)
arrival_time (TEXT) - GTFS HH:MM:SS; hours can be greater than 23
departure_time (TEXT) - GTFS HH:MM:SS; hours can be greater than 23
stop_headsign (TEXT, NULL allowed)
pickup_type (INTEGER) - GTFS coded value, normally 0-3
drop_off_type (INTEGER) - GTFS coded value, normally 0-3
shape_dist_traveled (REAL, NULL allowed) - non-negative distance along the route shape
```

The composite key identifies the position of one stop within one trip. The same `stop_sequence` value can appear in different trips, but the combination of `trip_id` and `stop_sequence` must be unique.

GTFS pickup and drop-off values:

- `0` or an empty source value: Regularly scheduled pickup or drop-off.
- `1`: No pickup or drop-off is available.
- `2`: The rider must contact the agency to arrange pickup or drop-off.
- `3`: The rider must coordinate with the driver to arrange pickup or drop-off.

## Relationships

```text
agencies 1 ----- many routes
routes   1 ----- many trips
services 1 ----- many trips
services 1 ----- many service_exceptions
trips    1 ----- many stop_times
stops    1 ----- many stop_times
stops    1 ----- many child stops (through parent_station)
```

## Files not required for the core analysis

The following source files are not required to answer the five mandatory project questions and are excluded from the initial schema:

- `feed_info.txt`
- `transfers.txt`
- `translations.txt`

They can be added later if the project uses feed metadata, transfers, or multilingual labels.

## Important conversion rules

- Import empty CSV values as SQL `NULL`, not as an empty string or zero.
- Keep all GTFS ID fields as `TEXT`.
- Keep `arrival_time` and `departure_time` as `TEXT` to preserve values after midnight.
- Store weekday flags and coded GTFS values as `INTEGER`.
- Store latitude, longitude, and travelled distance as `REAL`.
- Convert GTFS dates from `YYYYMMDD` to ISO `YYYY-MM-DD` during ingestion so SQLite date operations can use them consistently.
- A missing accessibility value means "unknown," not "not accessible."
