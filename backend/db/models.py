from enum import Enum as PyEnum

from sqlalchemy import BigInteger, Boolean, Date, Enum as PQEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger(), unique=True, index=True)
    telegram_username: Mapped[str] = mapped_column(String(), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    avatar_url: Mapped[str] = mapped_column(Text)

    profiles: Mapped[list["ProfileModel"]] = relationship(
        "ProfileModel", back_populates="user", lazy="selectin"
    )
    team_members: Mapped[list["TeamMemberModel"]] = relationship(
        "TeamMemberModel", back_populates="user", lazy="noload"
    )


class RoleType(PyEnum):
    backend = "backend"
    frontend = "frontend"
    mobile = "mobile"
    ml = "ml"
    product = "product"
    designer = "designer"


class ProfileModel(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[RoleType] = mapped_column(
        PQEnum(RoleType, create_type=True),
        nullable=False,
    )
    about: Mapped[str] = mapped_column(String(512))

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profiles", lazy="joined")
    profile_skills: Mapped[list["ProfileSkillModel"]] = relationship(
        "ProfileSkillModel", back_populates="profile", lazy="selectin"
    )
    participants: Mapped[list["ParticipantsModel"]] = relationship(
        "ParticipantsModel", back_populates="profile", lazy="selectin"
    )


class ProfileSkillModel(Base):
    __tablename__ = "profile_skills"

    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), primary_key=True, index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True, index=True)

    profile: Mapped["ProfileModel"] = relationship(
        "ProfileModel", back_populates="profile_skills", lazy="joined"
    )
    skill: Mapped["SkillModel"] = relationship(
        "SkillModel", back_populates="profile_skills", lazy="joined"
    )


class SkillType(PyEnum):
    hard = "hard"
    soft = "soft"


class SkillModel(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True)
    type: Mapped[SkillType] = mapped_column(
        PQEnum(SkillType, create_type=True),
        nullable=False,
    )

    profile_skills: Mapped[list["ProfileSkillModel"]] = relationship(
        "ProfileSkillModel", back_populates="skill", lazy="noload"
    )


class OrganizerModel(Base):
    __tablename__ = "organizers"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(128), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))

    hackathons: Mapped[list["HackathonModel"]] = relationship(
        "HackathonModel", back_populates="organizer", lazy="selectin"
    )


class HackathonModel(Base):
    __tablename__ = "hackathons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    photo_url: Mapped[str] = mapped_column(Text, nullable=True)

    start_date: Mapped["Date"] = mapped_column(Date)
    end_date: Mapped["Date"] = mapped_column(Date)

    tags: Mapped[str] = mapped_column(Text)

    max_teams: Mapped[int] = mapped_column(Integer)
    min_team_size: Mapped[int] = mapped_column(Integer)
    max_team_size: Mapped[int] = mapped_column(Integer)

    organizer_id: Mapped[int] = mapped_column(ForeignKey("organizers.id"), index=True)

    organizer: Mapped["OrganizerModel"] = relationship(
        "OrganizerModel", back_populates="hackathons", lazy="joined"
    )
    teams: Mapped[list["TeamModel"]] = relationship(
        "TeamModel", back_populates="hackathon", lazy="selectin"
    )
    participants: Mapped[list["ParticipantsModel"]] = relationship(
        "ParticipantsModel", back_populates="hackathon", lazy="selectin"
    )


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), index=True)
    name: Mapped[str] = mapped_column(String(32), index=True)
    about: Mapped[str] = mapped_column(String(512))
    is_completed: Mapped[bool] = mapped_column(Boolean)
    # по-хорошему сюда надо наебашить approved, чтобы организатор мог принимать или нет команды

    hackathon: Mapped["HackathonModel"] = relationship(
        "HackathonModel", back_populates="teams", lazy="joined"
    )
    team_members: Mapped[list["TeamMemberModel"]] = relationship(
        "TeamMemberModel", back_populates="team", lazy="selectin"
    )
    invites: Mapped[list["InviteModel"]] = relationship(
        "InviteModel", back_populates="team", lazy="selectin"
    )


class TeamMemberModel(Base):
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    role: Mapped[RoleType] = mapped_column(
        PQEnum(RoleType, create_type=True),
        nullable=True,
    )

    team: Mapped["TeamModel"] = relationship(
        "TeamModel", back_populates="team_members", lazy="joined"
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="team_members", lazy="joined"
    )


class ParticipantsModel(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), index=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), index=True)

    hackathon: Mapped["HackathonModel"] = relationship(
        "HackathonModel", back_populates="participants", lazy="joined"
    )
    profile: Mapped["ProfileModel"] = relationship(
        "ProfileModel", back_populates="participants", lazy="joined"
    )
    invites: Mapped[list["InviteModel"]] = relationship(
        "InviteModel", back_populates="participant", lazy="selectin"
    )


class InviteStatusEnum(PyEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class InviteTypeEnum(PyEnum):
    INVITE = "INVITE"
    REQUEST = "REQUEST"


class InviteModel(Base):
    __tablename__ = "invites"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id"), index=True)
    type: Mapped[InviteTypeEnum] = mapped_column(
        PQEnum(InviteTypeEnum, create_type=True), nullable=False
    )
    status: Mapped[InviteStatusEnum] = mapped_column(
        PQEnum(InviteStatusEnum, create_type=True),
        nullable=False,
    )

    team: Mapped["TeamModel"] = relationship("TeamModel", back_populates="invites", lazy="joined")
    participant: Mapped["ParticipantsModel"] = relationship(
        "ParticipantsModel", back_populates="invites", lazy="joined"
    )
