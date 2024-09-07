from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent, Message, FSInputFile, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from loguru import logger

from src.article import Article
from src.database import Database
from src.models import Concept, Info
from src.notion import NotionAPI
from src.states import SetConfig, SetTemplate, SetProject, GetArticle
from src.storage import ConfigFile, TemplateFile


router = Router()


@router.errors()
async def errors_handler(event: ErrorEvent):
    await event.update.message.answer("Произошла ошибка")
    with logger.catch():
        raise event.exception

@router.message(Command("get_config"))
async def cmd_get_config(message: Message, bot: Bot):
    config_file = ConfigFile()
    file = FSInputFile(config_file.path)
    await bot.send_document(
        chat_id=message.chat.id,
        document=file
    )


@router.message(StateFilter(None), Command("set_config"))
async def cmd_set_config(message: Message, state: FSMContext):
    await message.answer("Отправьте файл с настройками")
    await state.set_state(SetConfig.waiting_config_file)


@router.message(StateFilter(SetConfig.waiting_config_file))
async def handle_config_file(message: Message, state: FSMContext, bot: Bot):

    if message.document and message.document.file_name == "config.yml":
        config_file = ConfigFile()
        await bot.download(
            file=message.document.file_id,
            destination=config_file.path
        )
        await message.reply("Настройки успешно установлены")
    else:
        await message.reply("Настройки не установлены")

    await state.set_state(None)


@router.message(Command("get_template"))
async def cmd_get_template(message: Message, bot: Bot):
    template_file = TemplateFile()
    file = FSInputFile(template_file.path)
    await bot.send_document(
        chat_id=message.chat.id,
        document=file
    )


@router.message(StateFilter(None), Command("set_template"))
async def cmd_set_template(message: Message, state: FSMContext):
    await message.answer("Отправьте файл с шаблоном")
    await state.set_state(SetTemplate.waiting_template_file)


@router.message(StateFilter(SetTemplate.waiting_template_file))
async def handle_template_file(message: Message, state: FSMContext, bot: Bot):

    if message.document and message.document.file_name == "template.html":
        template_file = TemplateFile()
        await bot.download(
            file=message.document.file_id,
            destination=template_file.path
        )
        await message.reply("Шаблон успешно установлен")
    else:
        await message.reply("Шаблон не установлен")

    await state.set_state(None)


@router.message(StateFilter(None), Command("set_project"))
async def cmd_set_project(message: Message, state: FSMContext):
    config_file = ConfigFile()
    project_list = config_file.project_list
    kb = [
        [KeyboardButton(text=project_name)]
        for project_name in project_list
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Укажите проект", reply_markup=keyboard)
    await state.set_state(SetProject.waiting_project_name)


@router.message(StateFilter(SetProject.waiting_project_name))
async def handle_project_name(message: Message, state: FSMContext):

    project_name = message.text

    config_file = ConfigFile()
    project_list = config_file.project_list

    if project_name not in project_list:
        await message.answer("Проект отсутствует в настройках", reply_markup=ReplyKeyboardRemove())
        await state.set_state(None)
        return

    config_file.current_project = project_name
    await message.answer("Проект успешно установлен", reply_markup=ReplyKeyboardRemove())
    await state.set_state(None)


@router.message(Command("sync"))
async def cmd_sync(message: Message):

    config_file = ConfigFile()
    notion_token = config_file.notion_token
    current_project = config_file.current_project
    concept_dbs = config_file.concept_dbs
    info_dbs = config_file.info_dbs

    notion_api = NotionAPI(notion_token)
    concept_rows = []
    for concept_db in concept_dbs:
        rows = notion_api.get_db_rows(concept_db)
        concept_rows.extend(rows)
    info_rows = []
    for info_db in info_dbs:
        rows = notion_api.get_db_rows(info_db)
        info_rows.extend(rows)

    concepts = [Concept.from_notion_db_row(row) for row in concept_rows]
    infos = [Info.from_notion_db_row(row) for row in info_rows]

    db = Database.instance(current_project)
    db.sync(concepts, infos)

    await message.answer("Данные успешно синхронизированы")


@router.message(StateFilter(None), Command("info"))
async def cmd_info(message: Message, state: FSMContext):
    await message.answer("Напишите название концепта")
    await state.set_state(GetArticle.waiting_concept_name)


@router.message(StateFilter(GetArticle.waiting_concept_name))
async def handle_concept_name(message: Message, state: FSMContext, bot: Bot):

    concept_name = message.text.strip()

    config_file = ConfigFile()
    current_project = config_file.current_project

    db = Database.instance(current_project)
    concept = db.get_concept_by_name(concept_name)

    if not concept:
        await message.answer("Концепт не найден")
        await state.set_state(None)
        return

    info_list = db.get_info_by_concept(concept_id=concept.id)
    article = Article(concept, info_list)
    article.render()

    file = FSInputFile(article.path)
    await bot.send_document(
        chat_id=message.chat.id,
        document=file
    )
    await state.set_state(None)

    article.delete()
