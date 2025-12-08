from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from db import crud
from db.models import InviteStatusEnum, InviteTypeEnum

router = Router()


def invite_keyboard(invite_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Принять", callback_data=f"accept_invite:{invite_id}"),
                InlineKeyboardButton(text="Отклонить", callback_data=f"decline_invite:{invite_id}"),
            ]
        ]
    )


# Отправить приглашение участнику в команду (от капитана/участника команды)
async def send_team_invite(
    team_id: int, participant_id: int, db_session: AsyncSession
) -> tuple[bool, str]:
    existing = await crud.get_invite(db_session, team_id, participant_id, InviteTypeEnum.INVITE)
    if existing and existing.status == InviteStatusEnum.PENDING:
        return False, "Участнику уже отправлено приглашение."

    await crud.create_invite(db_session, team_id, participant_id, InviteTypeEnum.INVITE)
    await crud.create_invite(db_session, team_id, participant_id, InviteTypeEnum.INVITE)

    team = await crud.get_team_by_id(db_session, team_id)
    participant = await crud.get_participant_by_id(db_session, participant_id)

    from bot import bot

    await bot.send_message(
        participant.profile.user.telegram_id,
        f"Вы приглащшены в команду {team.name}",
        reply_markup=invite_keyboard,
    )
    return True, "Приглашение отправлено."


# Отправить заявку на вступление в команду (от участника)
async def send_join_request(
    team_id: int, participant_id: int, db_session: AsyncSession
) -> tuple[bool, str]:
    existing = await crud.get_invite(db_session, team_id, participant_id, InviteTypeEnum.REQUEST)
    if existing and existing.status == InviteStatusEnum.PENDING:
        return False, "Вы уже отправили заявку в эту команду."

    await crud.create_invite(db_session, team_id, participant_id, InviteTypeEnum.REQUEST)

    creator = await crud.get_team_creator(db_session, team_id)
    team = await crud.get_team_by_id(db_session, team_id)
    participant = await crud.get_participant_by_id(db_session, participant_id)
    from bot import bot

    await bot.send_message(
        creator.telegram_id,
        f"К вам в {team.name} хочет {participant.profile.user.name}",
        reply_markup=invite_keyboard,
    )
    return True, "Заявка отправлена."


# принять приглашение или заявку
@router.callback_query(lambda c: c.data.startswith("accept_invite:"))
async def accept_invite_callback(callback: CallbackQuery, db_session: AsyncSession):
    invite_id = int(callback.data.split(":")[1])
    invite = await crud.get_invite_by_id(db_session, invite_id)
    if not invite or invite.status != InviteStatusEnum.PENDING:
        await callback.answer("Приглашение не найдено или уже обработано.", show_alert=True)
        return
    await crud.update_invite_status(db_session, invite_id, InviteStatusEnum.ACCEPTED)

    await callback.answer("Приглашение принято!")
    await callback.message.edit_reply_markup(reply_markup=None)

    await crud.add_participant_to_team(db_session, invite.team_id, invite.participant_id)


# отклонить приглашение или заявку
@router.callback_query(lambda c: c.data.startswith("decline_invite:"))
async def decline_invite_callback(callback: CallbackQuery, db_session: AsyncSession):
    invite_id = int(callback.data.split(":")[1])
    invite = await crud.get_invite_by_id(db_session, invite_id)
    if not invite or invite.status != InviteStatusEnum.PENDING:
        await callback.answer("Приглашение не найдено или уже обработано.", show_alert=True)
        return
    await crud.update_invite_status(db_session, invite_id, InviteStatusEnum.REJECTED)
    await callback.answer("Приглашение отклонено.")
    await callback.message.edit_reply_markup(reply_markup=None)
