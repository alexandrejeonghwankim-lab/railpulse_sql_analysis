PRAGMA foreign_keys = ON;

-- Source: agency.txt
CREATE TABLE IF NOT EXISTS agencies (
    agency_id       TEXT NOT NULL,
    agency_lang     TEXT,
    agency_name     TEXT NOT NULL,
    agency_timezone TEXT NOT NULL,
    agency_url      TEXT NOT NULL,
    agency_phone    TEXT,
    agency_fare_url TEXT,

    PRIMARY KEY (agency_id)
);

-- Source: routes.txt
CREATE TABLE IF NOT EXISTS routes (
    route_id         TEXT NOT NULL,
    agency_id        TEXT NOT NULL,
    route_short_name TEXT NOT NULL,
    route_long_name  TEXT NOT NULL,
    route_desc       TEXT,
    route_type       INTEGER NOT NULL,
    route_url        TEXT,
    route_color      TEXT,
    route_text_color TEXT,

    PRIMARY KEY (route_id),

    FOREIGN KEY (agency_id)
        REFERENCES agencies (agency_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

-- Source: calendar.txt
CREATE TABLE IF NOT EXISTS services (
    service_id TEXT NOT NULL,
    monday     INTEGER NOT NULL CHECK (monday IN (0, 1)),
    tuesday    INTEGER NOT NULL CHECK (tuesday IN (0, 1)),
    wednesday  INTEGER NOT NULL CHECK (wednesday IN (0, 1)),
    thursday   INTEGER NOT NULL CHECK (thursday IN (0, 1)),
    friday     INTEGER NOT NULL CHECK (friday IN (0, 1)),
    saturday   INTEGER NOT NULL CHECK (saturday IN (0, 1)),
    sunday     INTEGER NOT NULL CHECK (sunday IN (0, 1)),
    start_date TEXT NOT NULL,
    end_date   TEXT NOT NULL,

    PRIMARY KEY (service_id)
);

-- Source: calendar_dates.txt
-- Composite primary key: service_id + exception_date
CREATE TABLE IF NOT EXISTS service_exceptions (
    service_id     TEXT NOT NULL,
    exception_date TEXT NOT NULL,
    exception_type INTEGER NOT NULL CHECK (exception_type IN (1, 2)),

    PRIMARY KEY (service_id, exception_date),

    FOREIGN KEY (service_id)
        REFERENCES services (service_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

-- Source: stops.txt
CREATE TABLE IF NOT EXISTS stops (
    stop_id              TEXT NOT NULL,
    parent_station       TEXT,
    stop_code            TEXT,
    stop_name            TEXT NOT NULL,
    stop_desc            TEXT,
    stop_lat             REAL NOT NULL
                             CHECK (stop_lat BETWEEN -90.0 AND 90.0),
    stop_lon             REAL NOT NULL
                             CHECK (stop_lon BETWEEN -180.0 AND 180.0),
    location_type        INTEGER NOT NULL DEFAULT 0
                             CHECK (location_type IN (0, 1, 2, 3, 4)),
    platform_code        TEXT,
    stop_url             TEXT,
    wheelchair_boarding  INTEGER
                             CHECK (
                                 wheelchair_boarding IS NULL
                                 OR wheelchair_boarding IN (0, 1, 2)
                             ),
    zone_id              TEXT,

    PRIMARY KEY (stop_id),

    FOREIGN KEY (parent_station)
        REFERENCES stops (stop_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

-- Source: trips.txt
CREATE TABLE IF NOT EXISTS trips (
    trip_id                 TEXT NOT NULL,
    route_id                TEXT NOT NULL,
    service_id              TEXT NOT NULL,
    trip_headsign           TEXT,
    trip_short_name         TEXT,
    direction_id            INTEGER
                                CHECK (
                                    direction_id IS NULL
                                    OR direction_id IN (0, 1)
                                ),
    block_id                TEXT,
    shape_id                TEXT,
    wheelchair_accessible   INTEGER
                                CHECK (
                                    wheelchair_accessible IS NULL
                                    OR wheelchair_accessible IN (0, 1, 2)
                                ),
    bikes_allowed           INTEGER
                                CHECK (
                                    bikes_allowed IS NULL
                                    OR bikes_allowed IN (0, 1, 2)
                                ),

    PRIMARY KEY (trip_id),

    FOREIGN KEY (route_id)
        REFERENCES routes (route_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,

    FOREIGN KEY (service_id)
        REFERENCES services (service_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

-- Source: stop_times.txt
-- Composite primary key: trip_id + stop_sequence
CREATE TABLE IF NOT EXISTS stop_times (
    trip_id             TEXT NOT NULL,
    stop_sequence       INTEGER NOT NULL CHECK (stop_sequence >= 0),
    stop_id             TEXT NOT NULL,
    arrival_time        TEXT NOT NULL,
    departure_time      TEXT NOT NULL,
    stop_headsign       TEXT,
    pickup_type         INTEGER NOT NULL CHECK (pickup_type IN (0, 1, 2, 3)),
    drop_off_type       INTEGER NOT NULL CHECK (drop_off_type IN (0, 1, 2, 3)),
    shape_dist_traveled REAL
                            CHECK (
                                shape_dist_traveled IS NULL
                                OR shape_dist_traveled >= 0
                            ),

    PRIMARY KEY (trip_id, stop_sequence),

    FOREIGN KEY (trip_id)
        REFERENCES trips (trip_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,

    FOREIGN KEY (stop_id)
        REFERENCES stops (stop_id)
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
);

-- Indexes for foreign-key joins and required analytical queries.
-- Primary-key indexes are created automatically by SQLite.
CREATE INDEX IF NOT EXISTS idx_routes_agency_id
    ON routes (agency_id);

CREATE INDEX IF NOT EXISTS idx_trips_route_id
    ON trips (route_id);

CREATE INDEX IF NOT EXISTS idx_trips_service_id
    ON trips (service_id);

CREATE INDEX IF NOT EXISTS idx_stops_parent_platform
    ON stops (parent_station, platform_code);

CREATE INDEX IF NOT EXISTS idx_stop_times_stop_id
    ON stop_times (stop_id);

CREATE INDEX IF NOT EXISTS idx_stop_times_departure_time
    ON stop_times (departure_time);

CREATE INDEX IF NOT EXISTS idx_service_exceptions_date
    ON service_exceptions (exception_date);
