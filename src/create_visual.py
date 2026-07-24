import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "railpulse.db"
SQL_DIRECTORY = PROJECT_ROOT / "sql" / "analysis"
OUTPUT_DIRECTORY = PROJECT_ROOT / "docs" / "visual"


def execute_sql_file(connection, filename):
    """Execute a saved SQL analysis file and return all rows."""

    sql_path = SQL_DIRECTORY / filename
    sql = sql_path.read_text(encoding="utf-8")

    return connection.execute(sql).fetchall()


def save_figure(filename):
    """Save the current Matplotlib figure."""

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIRECTORY / filename

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close()

    print(f"Saved: {output_path}")


def add_bar_labels(axis):
    """Display values above vertical bars."""

    for container in axis.containers:
        axis.bar_label(
            container,
            fmt="%.0f",
            padding=3,
            fontsize=8,
        )
def create_peak_hour_chart(connection):
    """Visualize the busiest scheduled departure hour."""

    rows = execute_sql_file(
        connection,
        "01_peak_hour.sql",
    )

    hours = [f"{row[0]:02d}:00" for row in rows]
    departures = [row[1] for row in rows]

    figure, axis = plt.subplots(figsize=(7, 5))

    axis.bar(
        hours,
        departures,
        color="#016AB3",
        width=0.5,
    )

    axis.set_title("Top 3 Scheduled Departure Hours")
    axis.set_xlabel("Clock hour")
    axis.set_ylabel("Scheduled departures")
    axis.grid(axis="y", alpha=0.25)

    add_bar_labels(axis)
    save_figure("01_peak_hour.png")

def create_platform_chart(connection):
    """Visualize the busiest Bruxelles-Central platforms."""

    rows = execute_sql_file(
        connection,
        "02_platform_bottlenecks.sql",
    )

    scheduled_visits = [row[0] for row in rows]
    platforms = [f"Platform {row[1]}" for row in rows]

    figure, axis = plt.subplots(figsize=(8, 5))

    bars = axis.bar(
        platforms,
        scheduled_visits,
        color=["#016AB3", "#4A90C2", "#8ABADD"],
    )

    axis.set_title(
        "Top 3 Busiest Platforms at Bruxelles-Central"
    )
    axis.set_xlabel("Platform")
    axis.set_ylabel("Scheduled visits")
    axis.grid(axis="y", alpha=0.25)

    axis.bar_label(
        bars,
        fmt="%.0f",
        padding=3,
    )

    save_figure("02_platform_bottlenecks.png")

def create_destination_chart(connection):
    """Visualize the most frequent morning destinations."""

    rows = execute_sql_file(
        connection,
        "03_morning_destinations.sql",
    )

    destinations = [row[0] for row in rows]
    morning_trips = [row[1] for row in rows]

    figure, axis = plt.subplots(figsize=(9, 5))

    bars = axis.bar(
        destinations,
        morning_trips,
        color=["#016AB3", "#4A90C2", "#8ABADD"],
    )

    axis.set_title(
        "Top 3 Morning Terminal Destinations"
    )
    axis.set_xlabel("Trip headsign")
    axis.set_ylabel("Morning trips")
    axis.grid(axis="y", alpha=0.25)

    axis.bar_label(
        bars,
        fmt="%.0f",
        padding=3,
    )

    save_figure("03_morning_destinations.png")

def create_service_frequency_chart(connection):
    """Visualize active-service frequency categories."""

    rows = execute_sql_file(
        connection,
        "04_service_frequency.sql",
    )

    categories = [row[0] for row in rows]
    service_counts = [row[1] for row in rows]
    percentages = [row[2] for row in rows]

    figure, axis = plt.subplots(figsize=(9, 5))

    bars = axis.bar(
        categories,
        percentages,
        color=["#4A90C2", "#F5A623", "#2E8B57"],
    )

    axis.set_title(
        "Active Services by Weekly Frequency"
    )
    axis.set_xlabel("Frequency category")
    axis.set_ylabel("Percentage of active services")
    axis.set_ylim(0, max(percentages) + 10)
    axis.grid(axis="y", alpha=0.25)

    labels = [
        f"{percentage:.2f}%\n({count:,} services)"
        for percentage, count
        in zip(percentages, service_counts)
    ]

    axis.bar_label(
        bars,
        labels=labels,
        padding=3,
    )

    save_figure("04_service_frequency.png")
def create_accessibility_chart(connection):
    """Compare documented and unknown amenity information."""

    query = """
    WITH trip_features AS (
        SELECT
            CASE
                WHEN routes.route_short_name = 'BUS'
                    THEN 'Bus service'
                ELSE 'Train service'
            END AS service_type,
            trips.bikes_allowed,
            trips.wheelchair_accessible
        FROM trips
        JOIN routes
            ON routes.route_id = trips.route_id
    )

    SELECT
        service_type,

        SUM(
            CASE
                WHEN bikes_allowed = 1 THEN 1
                ELSE 0
            END
        ) AS bike_confirmed,

        SUM(
            CASE
                WHEN bikes_allowed IS NULL THEN 1
                ELSE 0
            END
        ) AS bike_unknown,

        SUM(
            CASE
                WHEN wheelchair_accessible = 1 THEN 1
                ELSE 0
            END
        ) AS wheelchair_confirmed,

        SUM(
            CASE
                WHEN wheelchair_accessible IS NULL THEN 1
                ELSE 0
            END
        ) AS wheelchair_unknown

    FROM trip_features
    GROUP BY service_type
    ORDER BY service_type;
    """

    rows = connection.execute(query).fetchall()

    service_types = [row[0] for row in rows]

    bike_confirmed = [row[1] for row in rows]
    bike_unknown = [row[2] for row in rows]

    wheelchair_confirmed = [row[3] for row in rows]
    wheelchair_unknown = [row[4] for row in rows]

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(13, 5),
    )

    # Bicycle information
    axes[0].bar(
        service_types,
        bike_confirmed,
        label="Explicitly confirmed",
        color="#2E8B57",
    )

    axes[0].bar(
        service_types,
        bike_unknown,
        bottom=bike_confirmed,
        label="Unknown",
        color="#B8B8B8",
    )

    axes[0].set_title("Bicycle Information")
    axes[0].set_ylabel("Scheduled trips")
    axes[0].legend()
    axes[0].grid(axis="y", alpha=0.25)

    # Wheelchair information
    axes[1].bar(
        service_types,
        wheelchair_confirmed,
        label="Explicitly confirmed",
        color="#016AB3",
    )

    axes[1].bar(
        service_types,
        wheelchair_unknown,
        bottom=wheelchair_confirmed,
        label="Unknown",
        color="#B8B8B8",
    )

    axes[1].set_title("Wheelchair Information")
    axes[1].set_ylabel("Scheduled trips")
    axes[1].legend()
    axes[1].grid(axis="y", alpha=0.25)

    figure.suptitle(
        "Passenger Amenity Information in GTFS"
    )

    save_figure("05_accessibility_audit.png")

def main():
    """Create all five RailPulse visualizations."""

    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        create_peak_hour_chart(connection)
        create_platform_chart(connection)
        create_destination_chart(connection)
        create_service_frequency_chart(connection)
        create_accessibility_chart(connection)

    print("All visualizations created successfully.")


if __name__ == "__main__":
    main()
