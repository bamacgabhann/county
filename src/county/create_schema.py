from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class Club(Base):
    __tablename__ = "clubs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    fullname: Mapped[str] = mapped_column(String, nullable=False)
    ainm = Column(String)
    location = Column(Geometry("POINT"))  # Geospatial data

    def __init__(self, name, fullname, ainm=None, location=None):
        self.name = name
        self.fullname = fullname
        self.ainm = ainm
        self.location = location

    def __repr__(self):
        return (
            f"Club {self.id}: {self.name} (fullname={self.fullname}, ainm={self.ainm})"
        )

    def __str__(self):
        return (
            f"Club {self.id}: {self.name} (fullname={self.fullname}, ainm={self.ainm})"
        )

    def __eq__(self, other):
        if not isinstance(other, Club):
            return False
        return (
            self.name == other.name
            and self.fullname == other.fullname
            and self.ainm == other.ainm
            and self.location == other.location
        )

    def update(self, name=None, fullname=None, ainm=None, location=None):
        if name:
            self.name = name
        if fullname:
            self.fullname = fullname
        if ainm:
            self.ainm = ainm
        if location:
            self.location = location


class Referees(Base):
    __tablename__ = "referees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    club_name = mapped_column(String, ForeignKey("clubs.name"), nullable=False)
    club = relationship("Club", backref="referees")

    def __init__(self, name, club_name):
        self.name = name
        self.club_name = club_name

    def __repr__(self):
        return f"Referee {self.id}: {self.name} (club_name={self.club_name})"

    def __str__(self):
        return f"Referee {self.id}: {self.name} (club_name={self.club_name})"

    def __eq__(self, other):
        if not isinstance(other, Referees):
            return False
        return self.name == other.name and self.club_name == other.club_name

    def update(self, name=None, club_name=None):
        if name:
            self.name = name
        if club_name:
            self.club_name = club_name


class Venues(Base):
    __tablename__ = "venues"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    club_name = mapped_column(String, ForeignKey("clubs.name"), nullable=False)
    location = Column(Geometry("POINT"))


class Grades(Base):
    __tablename__ = "grades"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    abbr: Mapped[str] = Column(String, nullable=False)


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)  # Name in English
    ainm: Mapped[str] = Column(String, nullable=False)  # Ainm as Gaeilge
    club_name = Column(String, ForeignKey("clubs.name"), nullable=False)
    club = relationship("Club", backref="players")


class Competition(Base):
    __tablename__ = "competitions"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    grade = Column(
        String, nullable=False
    )  # Under 14, Under 16, Minor, Junior, Intermediate, Senior


class Division(Base):
    __tablename__ = "divisions"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    competition = relationship("Competition")


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String, nullable=False)
    club_name = Column(String, ForeignKey("clubs.name"))
    division_id = Column(Integer, ForeignKey("divisions.id"))
    club = relationship("Club")
    division = relationship("Division")


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = Column(Integer, primary_key=True)
    ref: Mapped[str] = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    home_goals = Column(Integer)
    home_points = Column(Integer)
    away_goals = Column(Integer)
    away_points = Column(Integer)
    location = Column(Geometry("POINT"), nullable=False)  # Geospatial data
    grade = Column(String, nullable=False)  # Grade of the match
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    division_id = Column(Integer, ForeignKey("divisions.id"), nullable=False)
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    competition = relationship("Competition")
    division = relationship("Division")


# Association table for many-to-many relationship between players and competitions, including team
player_competition_association = Table(
    "player_competition",
    Base.metadata,
    Column("player_id", Integer, ForeignKey("players.id")),
    Column("competition_id", Integer, ForeignKey("competitions.id")),
    Column("team_id", Integer, ForeignKey("teams.id")),
    Column("grade_id", Integer, ForeignKey("grade.id")),
)


class PlayerParticipation(Base):
    __tablename__ = "player_participation"
    id: Mapped[int] = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    is_substitute = Column(Boolean, default=False)
    match = relationship("Match")
    player = relationship("Player")
    team = relationship("Team")


# Create the database
engine = create_engine(
    "postgresql://your_username:your_password@localhost/your_database"
)
Base.metadata.create_all(engine)
