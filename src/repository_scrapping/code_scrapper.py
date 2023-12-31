from snippet_management.snippet_storage import SnippetStorage
from snippet_management.code_snippet import CodeSnippet
from snippet_management.snippet_extract import SnippetExtract
from tree_sitter_logic.languages import FileExtension, LanguageNodes
from tree_sitter_logic.tree_sitter_util import (
    get_specified_nodes,
    global_node_types,
)
from file_handler.file_handler import FileHandler
from typing import Set, Dict
from dataclasses import dataclass, field
from tree_sitter import Parser, Node


@dataclass
class CodeScrapper:
    _input_file: FileHandler = None
    _snippet_storage: SnippetStorage = field(default_factory=lambda: SnippetStorage())
    _parser: Parser = field(default_factory=lambda: Parser())
    _relevant_nodes_names: Set[str] = None
    _assignment_nodes_names: Set[str] = None
    _ast_root: Node = None

    def extract_snippets(self) -> bool:
        if not self._check_input_file():
            raise Exception("CodeScrapper_File_Error: No file has been charged ")
        self._scrape_relevant()
        self._scrape_assignment()
        return True

    def change_file(self, file: FileHandler) -> bool:
        self._input_file = file
        self._update_scrapper()
        return True

    @property
    def storage_dict(self) -> Dict[int, CodeSnippet]:
        return self._snippet_storage.storage

    def _update_scrapper(self):
        self._update_parser()
        self._update_nodes_names()
        self._update_ast_root()

    def _update_parser(self):
        self._parser.set_language(FileExtension[self._input_file.file_extension].value)

    def _update_nodes_names(self):
        self._relevant_nodes_names = LanguageNodes[
            self._input_file.file_extension
        ].value[0]
        self._assignment_nodes_names = LanguageNodes[
            self._input_file.file_extension
        ].value[1]

    def _update_ast_root(self):
        tree = self._parser.parse(bytes(self._input_file.file_str, "utf8"))
        self._ast_root = tree.root_node

    def _scrape_relevant(self):
        relevant_nodes = get_specified_nodes(self._ast_root, self._relevant_nodes_names)
        for node in relevant_nodes:
            snippet_extract = SnippetExtract(node, self._input_file.file_str)
            code_snippet = CodeSnippet(self._input_file, snippet_extract)
            self._save_code_snippet(code_snippet)

    def _scrape_assignment(self):
        assignment_nodes = global_node_types(
            self._ast_root, self._assignment_nodes_names
        )
        for node in assignment_nodes:
            snippet_extract = SnippetExtract(node, self._input_file.file_str)
            code_snippet = CodeSnippet(self._input_file, snippet_extract)
            self._save_code_snippet(code_snippet)

    def _save_code_snippet(self, code_snippet: CodeSnippet):
        self._snippet_storage.add_code_snippet(code_snippet)

    def _check_input_file(self):
        return self._input_file != None and isinstance(self._input_file, FileHandler)

    def show_storage(self):
        self._snippet_storage.show_storage()
