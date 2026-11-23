"""URL-safe demo fixtures shared by the frontend pages.

The field names intentionally mirror the backend ORM models so templates keep
working after the real data layer replaces this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


def _in_days(days: int, hour: int, minute: int = 0) -> datetime:
    base = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    return base + timedelta(days=days)


@dataclass(frozen=True)
class DemoUser:
    id: str
    name: str
    email: str
    role: str

    @property
    def first_name(self) -> str:
        return self.name.split(" ")[0]

    @property
    def initials(self) -> str:
        parts = [part for part in self.name.split(" ") if part]
        return "".join(part[0] for part in parts[:2]).upper()


@dataclass(frozen=True)
class DemoEvent:
    id: str
    title: str
    category: str
    description: str
    organizer: str
    location: str
    city: str
    start_at: datetime
    end_at: datetime
    registration_open_at: datetime
    registration_close_at: datetime
    checkin_open_at: datetime
    checkin_close_at: datetime
    capacity: int
    registered_count: int
    status: str
    accent: str

    @property
    def date_short(self) -> str:
        return self.start_at.strftime("%a, %d %b")

    @property
    def date_long(self) -> str:
        return self.start_at.strftime("%A, %d %B %Y")

    @property
    def time_short(self) -> str:
        return self.start_at.strftime("%H:%M")

    @property
    def initial(self) -> str:
        return self.title[:1].upper()

    @property
    def capacity_pct(self) -> int:
        if self.capacity <= 0:
            return 0
        return min(100, round(self.registered_count / self.capacity * 100))

    @property
    def spots_left(self) -> int:
        return max(0, self.capacity - self.registered_count)

    @property
    def is_sold_out(self) -> bool:
        return self.spots_left == 0

    @property
    def is_registration_open(self) -> bool:
        now = datetime.now()
        return (
            not self.is_sold_out and self.registration_open_at <= now <= self.registration_close_at
        )

    @property
    def schedule(self) -> list[tuple[str, datetime]]:
        """Key timestamps already stored on the event, in reading order."""

        return [
            ("Registration opens", self.registration_open_at),
            ("Registration closes", self.registration_close_at),
            ("Doors open", self.checkin_open_at),
            ("Show starts", self.start_at),
            ("Ends", self.end_at),
        ]

    @property
    def url(self) -> str:
        return f"/events/{self.id}"


@dataclass(frozen=True)
class DemoTicket:
    id: str
    code: str
    event_id: str
    user_id: str
    status: str
    issued_at: datetime
    used_at: datetime | None
    seat: str

    @property
    def short_code(self) -> str:
        return self.code[-8:].upper()


@dataclass(frozen=True)
class DemoCheckinLog:
    id: str
    participant: str
    event_title: str
    result: str
    reason: str
    created_at: datetime
    operator: str


def demo_events() -> list[DemoEvent]:
    return [
        DemoEvent(
            id="evt-senja-kala",
            title="Senja Kala — Album Release Night",
            category="Concert",
            description=(
                "A one-night album release with a full band, a string quartet, "
                "and an all-analog light show. Doors open an hour before the first set."
            ),
            location="Graha Cakrawala",
            city="Malang",
            organizer="Senja Kala Collective",
            start_at=_in_days(18, 19, 30),
            end_at=_in_days(18, 23, 0),
            registration_open_at=_in_days(-6, 9),
            registration_close_at=_in_days(17, 23, 59),
            checkin_open_at=_in_days(18, 18, 30),
            checkin_close_at=_in_days(18, 21, 30),
            capacity=900,
            registered_count=742,
            status="SELLING FAST",
            accent="#C93A24",
        ),
        DemoEvent(
            id="evt-ruang-reka",
            title="Ruang Reka: Design & Technology Forum",
            category="Conference",
            description=(
                "A working forum on product design, type, and the craft of building "
                "useful things. Six talks, two workshops, one long lunch."
            ),
            location="Auditorium FTT",
            city="Malang",
            organizer="Ruang Reka Studio",
            start_at=_in_days(32, 9, 0),
            end_at=_in_days(32, 17, 0),
            registration_open_at=_in_days(-2, 9),
            registration_close_at=_in_days(30, 23, 59),
            checkin_open_at=_in_days(32, 8, 0),
            checkin_close_at=_in_days(32, 10, 0),
            capacity=240,
            registered_count=198,
            status="ON SALE",
            accent="#245C4A",
        ),
        DemoEvent(
            id="evt-nada-timur",
            title="Nada Timur Festival 2026",
            category="Festival",
            description=(
                "Three stages of contemporary Indonesian music by the water. "
                "Gates close at 22:00 and re-entry is not permitted."
            ),
            location="Pelabuhan Tanjung Perak",
            city="Surabaya",
            organizer="Nada Timur Foundation",
            start_at=_in_days(46, 15, 0),
            end_at=_in_days(46, 23, 0),
            registration_open_at=_in_days(-10, 9),
            registration_close_at=_in_days(44, 23, 59),
            checkin_open_at=_in_days(46, 14, 0),
            checkin_close_at=_in_days(46, 21, 0),
            capacity=4200,
            registered_count=3110,
            status="ON SALE",
            accent="#7A4A12",
        ),
        DemoEvent(
            id="evt-malam-puisi",
            title="Malam Puisi: Suara dari Tepi",
            category="Reading",
            description=(
                "An evening of readings and new music from writers across the "
                "archipelago, hosted in the old theatre hall."
            ),
            location="Taman Budaya",
            city="Yogyakarta",
            organizer="Taman Budaya Yogyakarta",
            start_at=_in_days(9, 19, 0),
            end_at=_in_days(9, 21, 30),
            registration_open_at=_in_days(-14, 9),
            registration_close_at=_in_days(8, 23, 59),
            checkin_open_at=_in_days(9, 18, 0),
            checkin_close_at=_in_days(9, 20, 0),
            capacity=160,
            registered_count=160,
            status="SOLD OUT",
            accent="#34486B",
        ),
        DemoEvent(
            id="evt-filharmoni",
            title="Konser Filharmoni Nusantara",
            category="Orchestra",
            description=(
                "The Nusantara Philharmonic performs works by contemporary "
                "Indonesian composers, with a pre-concert talk at 19:00."
            ),
            location="Aula Simfonia",
            city="Jakarta",
            organizer="Nusantara Philharmonic",
            start_at=_in_days(61, 20, 0),
            end_at=_in_days(61, 22, 30),
            registration_open_at=_in_days(-3, 9),
            registration_close_at=_in_days(59, 23, 59),
            checkin_open_at=_in_days(61, 19, 0),
            checkin_close_at=_in_days(61, 21, 0),
            capacity=680,
            registered_count=544,
            status="ON SALE",
            accent="#6B3350",
        ),
        DemoEvent(
            id="evt-pasar-kreatif",
            title="Pasar Kreatif Minggu Pagi",
            category="Market",
            description=(
                "A Sunday morning market for ceramics, small press books, and slow "
                "food. Free entry, no ticket required."
            ),
            location="Alun-Alun Merdeka",
            city="Malang",
            organizer="Alun-Alun Kolektif",
            start_at=_in_days(4, 7, 0),
            end_at=_in_days(4, 12, 0),
            registration_open_at=_in_days(-1, 9),
            registration_close_at=_in_days(3, 23, 59),
            checkin_open_at=_in_days(4, 7, 0),
            checkin_close_at=_in_days(4, 12, 0),
            capacity=300,
            registered_count=120,
            status="FREE ENTRY",
            accent="#4C5B32",
        ),
    ]


def demo_users() -> list[DemoUser]:
    return [
        DemoUser(
            id="usr-participant",
            name="Alya Prameswari",
            email="alya@example.com",
            role="participant",
        ),
        DemoUser(
            id="usr-operator",
            name="Bagas Wirawan",
            email="operator@smartticket.test",
            role="operator",
        ),
        DemoUser(
            id="usr-admin",
            name="Rani Kusuma",
            email="admin@smartticket.test",
            role="admin",
        ),
    ]


def demo_tickets() -> list[DemoTicket]:
    now = datetime.now()
    return [
        DemoTicket(
            id="tkt-senja-kala",
            code="ST-2026-4F8K-91QD",
            event_id="evt-senja-kala",
            user_id="usr-participant",
            status="ACTIVE",
            issued_at=now - timedelta(days=4),
            used_at=None,
            seat="GA · Section B",
        ),
        DemoTicket(
            id="tkt-ruang-reka",
            code="ST-2026-7M2P-38VX",
            event_id="evt-ruang-reka",
            user_id="usr-participant",
            status="ACTIVE",
            issued_at=now - timedelta(days=2),
            used_at=None,
            seat="Row C · 12",
        ),
        DemoTicket(
            id="tkt-nada-timur",
            code="ST-2026-1T9A-64HN",
            event_id="evt-nada-timur",
            user_id="usr-participant",
            status="USED",
            issued_at=now - timedelta(days=20),
            used_at=now - timedelta(days=17, hours=3),
            seat="GA · Gate 4",
        ),
    ]


def demo_checkin_logs() -> list[DemoCheckinLog]:
    now = datetime.now()
    return [
        DemoCheckinLog(
            "log-01",
            "Alya Prameswari",
            "Senja Kala — Album Release Night",
            "GRANTED",
            "Face matched · distance 0.412",
            now - timedelta(minutes=2),
            "Bagas Wirawan",
        ),
        DemoCheckinLog(
            "log-02",
            "Dimas Ardhana",
            "Senja Kala — Album Release Night",
            "DENIED",
            "Face distance above threshold",
            now - timedelta(minutes=5),
            "Bagas Wirawan",
        ),
        DemoCheckinLog(
            "log-03",
            "Nadia Salsabila",
            "Senja Kala — Album Release Night",
            "GRANTED",
            "Face matched · distance 0.388",
            now - timedelta(minutes=7),
            "Bagas Wirawan",
        ),
        DemoCheckinLog(
            "log-04",
            "Raka Pratama",
            "Senja Kala — Album Release Night",
            "DENIED",
            "Ticket already used",
            now - timedelta(minutes=9),
            "Bagas Wirawan",
        ),
        DemoCheckinLog(
            "log-05",
            "Intan Maharani",
            "Senja Kala — Album Release Night",
            "GRANTED",
            "Face matched · distance 0.451",
            now - timedelta(minutes=12),
            "Bagas Wirawan",
        ),
    ]
