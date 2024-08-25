from dirs import DATA
from src.utils.text_file import TextFile
from src.utils.yaml_file import YAMLFile


class ConfigFile(YAMLFile):

    def __init__(self):
        super(ConfigFile, self).__init__(DATA / "config.yml")

    @property
    def notion_token(self) -> str:
        result = self.read() or {}
        result = result.get("notion_token", "")
        return result

    @property
    def current_project(self) -> str:
        result = self.read() or {}
        result = result.get("current_project", "")
        return result

    @current_project.setter
    def current_project(self, value: str) -> None:
        data = self.read() or {}
        data["current_project"] = value
        self.write(data)

    @property
    def project_list(self) -> list[str]:
        result = self.read() or {}
        result = result.get("projects", {})
        result = list(result.keys())
        return result

    @property
    def concept_dbs(self) -> list[str]:
        result = self.read() or {}
        result = result.get("projects", {})
        result = result.get(self.current_project, {})
        result = result.get("concept_dbs", [])
        return result

    @property
    def info_dbs(self) -> list[str]:
        result = self.read() or {}
        result = result.get("projects", {})
        result = result.get(self.current_project, {})
        result = result.get("info_dbs", [])
        return result


class TemplateFile(TextFile):

    def __init__(self):
        super(TemplateFile, self).__init__(DATA / "template.html")
