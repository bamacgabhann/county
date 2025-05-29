from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Table,
    Time,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    object_session,
    relationship,
)


class Base(DeclarativeBase):
    pass


team_club_association = Table(
    "team_club_association",
    Base.metadata,
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
    Column("club_id", ForeignKey("clubs.id"), primary_key=True),
)

player_team_association = Table(
    "player_team_association",
    Base.metadata,
    Column("player_id", ForeignKey("players.id"), primary_key=True),
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
)


class Club(Base):
    __tablename__ = "clubs"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ainm: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    referees: Mapped[Optional[List["Referee"]]] = relationship(back_populates="club")
    venues: Mapped[Optional[List["Venue"]]] = relationship(back_populates="club")
    players: Mapped[Optional[List["Player"]]] = relationship(back_populates="club")
    teams: Mapped[Optional[List["Team"]]] = relationship(
        secondary=team_club_association, back_populates="clubs"
    )

    def __str__(self):
        if self.ainm:
            return f"Club {self.id}: {self.name} / {self.ainm}"
        else:
            return f"Club {self.id}: {self.name}"


class Referee(Base):
    __tablename__ = "referees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    club_id = mapped_column(ForeignKey("clubs.id"), nullable=False)
    club: Mapped["Club"] = relationship(back_populates="referees")
    matches: Mapped[Optional[List["Match"]]] = relationship(back_populates="referee")

    def __str__(self):
        return f"Referee {self.id}: {self.name} (club_name={self.club})"


class Venue(Base):
    __tablename__ = "venues"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    club_id = mapped_column(ForeignKey("clubs.id"), nullable=True)
    club: Mapped["Club"] = relationship(back_populates="venues")
    matches: Mapped[Optional[List["Match"]]] = relationship(back_populates="venue")


class Player(Base):
    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # Name in English
    ainm: Mapped[str] = mapped_column(String, nullable=False)  # Ainm as Gaeilge
    club_id = mapped_column(ForeignKey("clubs.id"), nullable=False)
    club: Mapped["Club"] = relationship(back_populates="players")
    teams: Mapped[Optional[List["Team"]]] = relationship(
        secondary=player_team_association, back_populates="players"
    )
    matches: Mapped[Optional[List["PlayerParticipation"]]] = relationship(
        back_populates="player"
    )


class Competition(Base):
    __tablename__ = "competitions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    divisions: Mapped[Optional[List["Division"]]] = relationship(
        back_populates="competition"
    )
    groups: Mapped[Optional[List["Group"]]] = relationship(back_populates="competition")
    teams: Mapped[Optional[List["Team"]]] = relationship(back_populates="competition")
    matches: Mapped[Optional[List["Match"]]] = relationship(
        back_populates="competition"
    )


class Division(Base):
    __tablename__ = "divisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    competition_id = mapped_column(ForeignKey("competitions.id"), nullable=False)
    competition: Mapped["Competition"] = relationship(back_populates="divisions")
    groups: Mapped[Optional[List["Group"]]] = relationship(back_populates="division")
    teams: Mapped[Optional[List["Team"]]] = relationship(back_populates="division")
    matches: Mapped[Optional[List["Match"]]] = relationship(back_populates="division")


class Group(Base):
    __tablename__ = "groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    competition_id = mapped_column(ForeignKey("competitions.id"), nullable=False)
    division_id = mapped_column(ForeignKey("divisions.id"), nullable=False)
    competition: Mapped["Competition"] = relationship(back_populates="groups")
    division: Mapped["Division"] = relationship(back_populates="groups")
    teams: Mapped[Optional[List["Team"]]] = relationship(back_populates="group")
    matches: Mapped[Optional[List["Match"]]] = relationship(back_populates="group")


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    competition_id = mapped_column(ForeignKey("competitions.id"), nullable=False)
    division_id = mapped_column(ForeignKey("divisions.id"), nullable=False)
    group_id = mapped_column(ForeignKey("groups.id"), nullable=False)
    played: Mapped[int] = mapped_column(Integer, default=0)
    won: Mapped[int] = mapped_column(Integer, default=0)
    drawn: Mapped[int] = mapped_column(Integer, default=0)
    lost: Mapped[int] = mapped_column(Integer, default=0)
    goals_for: Mapped[int] = mapped_column(Integer, default=0)
    points_for: Mapped[int] = mapped_column(Integer, default=0)
    goals_against: Mapped[int] = mapped_column(Integer, default=0)
    points_against: Mapped[int] = mapped_column(Integer, default=0)
    goals_for_x_wo: Mapped[int] = mapped_column(Integer, default=0)
    points_for_x_wo: Mapped[int] = mapped_column(Integer, default=0)
    goals_against_x_wo: Mapped[int] = mapped_column(Integer, default=0)
    points_against_x_wo: Mapped[int] = mapped_column(Integer, default=0)
    league_rank: Mapped[int] = mapped_column(Integer, default=0)
    fielded_all: Mapped[bool] = mapped_column(Boolean, default=True)
    clubs: Mapped[List["Club"]] = relationship(
        secondary=team_club_association, back_populates="teams"
    )
    competition: Mapped["Competition"] = relationship(back_populates="teams")
    division: Mapped["Division"] = relationship(back_populates="teams")
    group: Mapped["Group"] = relationship(back_populates="teams")
    players: Mapped[Optional[List["Player"]]] = relationship(
        secondary=player_team_association, back_populates="teams"
    )
    home_matches: Mapped[Optional[List["Match"]]] = relationship(
        "Match", foreign_keys="Match.home_team_id", back_populates="home_team"
    )
    away_matches: Mapped[Optional[List["Match"]]] = relationship(
        "Match", foreign_keys="Match.away_team_id", back_populates="away_team"
    )

    @hybrid_property
    def scores_for(self):
        if self.competition_id > 2:
            return self.goals_for + self.points_for
        else:
            return self.goals_for * 3 + self.points_for

    @hybrid_property
    def scores_against(self):
        if self.competition_id > 2:
            return self.goals_against + self.points_against
        else:
            return self.goals_against * 3 + self.points_against

    @hybrid_property
    def scoring_difference(self):
        return self.scores_for - self.scores_against

    @hybrid_property
    def scores_for_x_wo(self):
        if self.competition_id > 2:
            return self.goals_for_x_wo + self.points_for_x_wo
        else:
            return self.goals_for_x_wo * 3 + self.points_for_x_wo

    @hybrid_property
    def scores_against_x_wo(self):
        if self.competition_id > 2:
            return self.goals_against_x_wo + self.points_against_x_wo
        else:
            return self.goals_against_x_wo * 3 + self.points_against_x_wo

    @hybrid_property
    def scoring_difference_x_wo(self):
        if self.competition_id > 2:
            return -self.scores_against_x_wo
        else:
            return self.scores_for_x_wo - self.scores_against_x_wo

    @hybrid_property
    def league_points(self):
        return (self.won * 2) + self.drawn


class Criteria(Base):
    __tablename__ = "criteria"
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    sql_query: Mapped[str] = mapped_column(String, nullable=False)


class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    home_team_id = mapped_column(ForeignKey("teams.id"), nullable=True)
    away_team_id = mapped_column(ForeignKey("teams.id"), nullable=True)
    venue_id = mapped_column(ForeignKey("venues.id"), nullable=True)
    competition_id = mapped_column(ForeignKey("competitions.id"), nullable=False)
    division_id = mapped_column(ForeignKey("divisions.id"), nullable=False)
    group_id = mapped_column(ForeignKey("groups.id"), nullable=True)
    stage: Mapped[str] = mapped_column(String, nullable=False)
    round: Mapped[str] = mapped_column(String, nullable=False)
    match_no: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[Date] = mapped_column(Date, nullable=True)
    time: Mapped[Time] = mapped_column(Time, nullable=True)  # Time of the match
    referee_id = mapped_column(ForeignKey("referees.id"), nullable=True)
    home_team_criteria_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("criteria.id"), nullable=True
    )
    away_team_criteria_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("criteria.id"), nullable=True
    )
    home_goals: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    home_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_goals: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_points: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    walkover: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    winner_id = mapped_column(ForeignKey("teams.id"), nullable=True)
    home_team: Mapped[Optional["Team"]] = relationship(
        "Team", foreign_keys=[home_team_id], back_populates="home_matches"
    )
    away_team: Mapped[Optional["Team"]] = relationship(
        "Team", foreign_keys=[away_team_id], back_populates="away_matches"
    )
    venue: Mapped[Optional["Venue"]] = relationship("Venue", back_populates="matches")
    referee: Mapped[Optional["Referee"]] = relationship(
        "Referee", back_populates="matches"
    )
    competition: Mapped["Competition"] = relationship(
        "Competition", back_populates="matches"
    )
    division: Mapped["Division"] = relationship("Division", back_populates="matches")
    group: Mapped[Optional["Group"]] = relationship("Group", back_populates="matches")
    players: Mapped[Optional[List["PlayerParticipation"]]] = relationship(
        back_populates="match"
    )
    home_team_criteria: Mapped[Optional["Criteria"]] = relationship(
        foreign_keys=[home_team_criteria_id]
    )
    away_team_criteria: Mapped[Optional["Criteria"]] = relationship(
        foreign_keys=[away_team_criteria_id]
    )

    @hybrid_property
    def home_players_started(self):
        session = object_session(self)
        if session is None:
            raise RuntimeError("Match object must be associated with a session")
        return (
            session.query(PlayerParticipation)
            .filter_by(match_id=self.id, team_id=self.home_team_id, started=True)
            .all()
        )

    @hybrid_property
    def home_players_substitute(self):
        session = object_session(self)
        if session is None:
            raise RuntimeError("Match object must be associated with a session")
        return (
            session.query(PlayerParticipation)
            .filter_by(match_id=self.id, team_id=self.home_team_id, started=False)
            .all()
        )

    @hybrid_property
    def away_players_started(self):
        session = object_session(self)
        if session is None:
            raise RuntimeError("Match object must be associated with a session")
        return (
            session.query(PlayerParticipation)
            .filter_by(match_id=self.id, team_id=self.away_team_id, started=True)
            .all()
        )

    @hybrid_property
    def away_players_substitute(self):
        session = object_session(self)
        if session is None:
            raise RuntimeError("Match object must be associated with a session")
        return (
            session.query(PlayerParticipation)
            .filter_by(match_id=self.id, team_id=self.away_team_id, started=False)
            .all()
        )


class PlayerParticipation(Base):
    __tablename__ = "player_participation"
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    started: Mapped[bool] = mapped_column(Boolean, default=False)
    player: Mapped["Player"] = relationship("Player", back_populates="matches")
    match: Mapped["Match"] = relationship("Match", back_populates="players")


# Create the database
# engine = create_engine(
#    "postgresql://your_username:your_password@localhost/your_database"
# )
