import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import URLInputFile, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import ClientResponseError
from loguru import logger

from api.unsplash import get_random_image
from api.freesound import get_sound
from config import telegram_bot_token, repository_url

bot = Bot(token=telegram_bot_token, default = DefaultBotProperties(parse_mode=ParseMode.HTML))
dispatcher = Dispatcher()


class BotStates(StatesGroup):
    Menu = State()
    ImageInput = State()
    ImageResult = State()
    AudioInput = State()
    AudioResult = State()


@dispatcher.message(Command("audio"))
@dispatcher.message(BotStates.AudioInput)
async def process_audio_query(message: types.Message, state: FSMContext, command: CommandObject = None):
    await state.set_state(BotStates.AudioResult)
    query = message.text.strip()
    if command:
        query = command.args
        if not query:
            await message.answer(
                "Для поиска звука используйте команду следующим образом:\n\n<b>/audio [ваш запрос]</b>")
            return
    try:
        sound, sound_name = await get_sound(query)
        audio_file = BufferedInputFile(sound, filename=sound_name)
        await message.answer_audio(audio_file, caption=f"🎵 Найден звук по запросу: <b>{query}</b>")
    except Exception as exception:
        logger.error(f"Ошибка поиска аудио: {exception}")
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="🔙 Вернуться в меню", callback_data="back"))
        await message.answer(
            "❗️ <b>Звук по данному запросу не найден.</b>\nПопробуйте еще раз или вернитесь в главное меню.",
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML)


@dispatcher.message(Command("image"))
@dispatcher.message(BotStates.ImageInput)
async def process_image_query(message: types.Message, state: FSMContext, command: CommandObject = None):
    await state.set_state(BotStates.ImageResult)
    query = message.text.strip()
    if command:
        query = command.args
        if not query:
            await message.answer(
                "Для поиска изображения используйте команду следующим образом:\n\n<b>/image [ваш запрос]</b>",
                parse_mode=ParseMode.HTML)
            return
    try:
        image_url, image_id = await get_random_image(query)
        image = URLInputFile(image_url, filename=image_id)
        await message.answer_photo(photo=image, caption=f"🖼 Найдено изображение по запросу: <b>{query}</b>")
    except Exception as exception:
        logger.error(f"Ошибка поиска изображения: {exception}")
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="🔙 Вернуться в меню", callback_data="back"))
        await message.answer(
            "❗️ <b>Изображение по данному запросу не найдено.</b>\nПопробуйте еще раз или вернитесь в главное меню.",
            reply_markup=builder.as_markup())


@dispatcher.callback_query(F.data == "get_audio_input")
async def get_audio_input(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BotStates.AudioInput)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back"))
    await callback.message.answer("🎤 Введите поисковый запрос для звука:", reply_markup=builder.as_markup())
    await callback.message.delete()


@dispatcher.callback_query(F.data == "get_image_input")
async def get_image_input(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BotStates.ImageInput)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back"))
    await callback.message.answer("🖼 Введите поисковый запрос для изображения:", reply_markup=builder.as_markup())
    await callback.message.delete()


@dispatcher.message(Command("start"))
@dispatcher.callback_query(F.data == "back")
async def cmd_start(event: types.Message, state: FSMContext):
    if isinstance(event, types.CallbackQuery):
        await event.message.delete()
        answer_target = event.message
    elif isinstance(event, types.Message):
        answer_target = event
    else:
        raise ValueError("Недопустимое событие")

    await state.set_state(BotStates.Menu)
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🖼 Поиск изображения", callback_data="get_image_input"),
        types.InlineKeyboardButton(text="🎵 Поиск звука", callback_data="get_audio_input")
    )
    builder.row(
        types.InlineKeyboardButton(text="🔗 Репозиторий", url=repository_url)
    )
    await answer_target.answer("Привет! 👋\n\nВыберите, что хотите сделать:", reply_markup=builder.as_markup())


async def main():
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
