from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger(), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    avatar_url: Mapped[str] = mapped_column(Text)

    profile: Mapped[list["ProfileModel"]] = relationship(
        "ProfileModel", back_populates="user", lazy="selectin"
    )
    team_members: Mapped[list["TeamMemberModel"]] = relationship(
        "TeamMemberModel", back_populates="user", lazy="noload"
    )


class ProfileModel(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    about: Mapped[str] = mapped_column(Text)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="profiles", lazy="joined")
    profile_skills: Mapped[list["ProfileSkillModel"]] = relationship(
        "ProfileSkillModel", back_populates="profile", lazy="selectin"
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


class SkillModel(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True)

    profile_skills: Mapped[list["ProfileSkillModel"]] = relationship(
        "ProfileSkillModel", back_populates="skill", lazy="noload"
    )


class OrganizerModel(Base):
    __tablename__ = "organizers"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(128), unique=True)
    password_hash: Mapped[str] = mapped_column(String(64))

    hackathons: Mapped[list["HackathonModel"]] = relationship(
        "HackathonModel", back_populates="organizer", lazy="selectin"
    )


class HackathonModel(Base):
    __tablename__ = "hackathons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)

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


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), index=True)
    is_completed: Mapped[bool] = mapped_column(Boolean)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"), index=True)

    hackathon: Mapped["HackathonModel"] = relationship(
        "HackathonModel", back_populates="teams", lazy="joined"
    )
    team_members: Mapped[list["TeamMemberModel"]] = relationship(
        "TeamMemberModel", back_populates="team", lazy="selectin"
    )


class TeamMemberModel(Base):
    __tablename__ = "team_members"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    team: Mapped["TeamModel"] = relationship(
        "TeamModel", back_populates="team_members", lazy="joined"
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="team_members", lazy="joined"
    )
