from aiogram.fsm.state import State, StatesGroup


class SetConfig(StatesGroup):
    waiting_config_file = State()


class SetTemplate(StatesGroup):
    waiting_template_file = State()


class SetProject(StatesGroup):
    waiting_project_name = State()


class GetArticle(StatesGroup):
    waiting_concept_name = State()
