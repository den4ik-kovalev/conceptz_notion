from jinja2 import Template

from dirs import TEMP
from src.models import Concept, Info
from src.storage import TemplateFile
from src.utils.text_file import TextFile


class Article(TextFile):

    def __init__(self, concept: Concept, info_list: list[Info]) -> None:
        super(Article, self).__init__(TEMP / f"{concept.name}.html", auto_create=False)
        self.concept = concept
        self.info_list = info_list

    def render(self):
        template_html = TemplateFile().read()
        template = Template(template_html)
        rendered_html = template.render(concept=self.concept, info_list=self.info_list)
        self.write(rendered_html)
