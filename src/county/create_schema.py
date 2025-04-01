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
from sqlalchemy.orm import relationship

Base = declarative_base()


class Club(Base):
    __tablename__ = "clubs"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(Geometry("POINT"), nullable=False)  # Geospatial data


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Name in English
    ainm = Column(String, nullable=False)  # Ainm as Gaeilge
    age = Column(
        Integer, nullable=False
    )  # Age in years on the qualifying date if <18, else 18
    grade = Column(String, nullable=False)  # Junior, Intermediate, Senior
    club_name = Column(String, ForeignKey("clubs.name"), nullable=False)
    club = relationship("Club", backref="players")


class Competition(Base):
    __tablename__ = "competitions"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    grade = Column(
        String, nullable=False
    )  # Under 14, Under 16, Minor, Junior, Intermediate, Senior


class Division(Base):
    __tablename__ = "divisions"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    competition = relationship("Competition")


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    club_name = Column(String, ForeignKey("clubs.name"))
    division_id = Column(Integer, ForeignKey("divisions.id"))
    club = relationship("Club")
    division = relationship("Division")


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
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
)


class PlayerParticipation(Base):
    __tablename__ = "player_participation"
    id = Column(Integer, primary_key=True)
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
