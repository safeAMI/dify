from typing import Any, Union

import requests
import logging
import os

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool

SERP_API_URL = "https://serpapi.com/search"


class SerpAPI:
    """
    SerpAPI tool provider.
    """
    def __init__(self, api_key: str) -> None:
        """Initialize SerpAPI tool provider."""
        self.serpapi_api_key = api_key

        current_dir = os.getcwd()
        log_file_path = os.path.join(current_dir, 'app.log')

        # 配置日志记录器
        logging.basicConfig(
            level=logging.DEBUG,  # 设置最低日志级别为 DEBUG
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 配置日志格式
            handlers=[
                logging.FileHandler(log_file_path),  # 将日志写入文件
            ]
        )

        # 记录日志消息
        logging.debug('这是一个调试信息')
        logging.info('这是一个信息')
        logging.warning('这是一个警告')
        logging.error('这是一个错误')
        logging.critical('这是一个严重错误')

    def run(self, query: str, **kwargs: Any) -> str:
        """Run query through SerpAPI and parse result."""
        typ = kwargs.get("result_type", "text")
        return self._process_response(self.results(query), typ=typ)

    def results(self, query: str) -> dict:
        """Run query through SerpAPI and return the raw result."""
        params = self.get_params(query)
        response = requests.get(url=SERP_API_URL, params=params)
        response.raise_for_status()
        return response.json()

    def get_params(self, query: str) -> dict[str, str]:
        """Get parameters for SerpAPI."""
        params = {
            "api_key": self.serpapi_api_key,
            "q": query,
            "engine": "google",
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en"
        }
        return params

    @staticmethod
    def _process_response(res: dict, typ: str) -> str:
        """
        Process response from SerpAPI.
        SerpAPI doc: https://serpapi.com/search-api
        Google search main results are called organic results
        """
        if "error" in res:
            raise ValueError(f"Got error from SerpAPI: {res['error']}")
        toret = ""
        if typ == "text":
            if "knowledge_graph" in res and "description" in res["knowledge_graph"]:
                toret += res["knowledge_graph"]["description"] + "\n"
            if "organic_results" in res:
                snippets = [
                    f"content: {item.get('snippet')}\nlink: {item.get('link')}"
                    for item in res["organic_results"]
                    if "snippet" in item
                ]
                toret += "\n".join(snippets)
        elif typ == "link":
            if "knowledge_graph" in res and "source" in res["knowledge_graph"]:
                toret += res["knowledge_graph"]["source"]["link"]
            elif "organic_results" in res:
                links = [
                    f"[{item['title']}]({item['link']})\n"
                    for item in res["organic_results"]
                    if "title" in item and "link" in item
                ]
                toret += "\n".join(links)
            elif "related_questions" in res:
                questions = [
                    f"[{item['question']}]({item['link']})\n"
                    for item in res["related_questions"]
                    if "question" in item and "link" in item
                ]
                toret += "\n".join(questions)
            elif "related_searches" in res:
                searches = [
                    f"[{item['query']}]({item['link']})\n"
                    for item in res["related_searches"]
                    if "query" in item and "link" in item
                ]
                toret += "\n".join(searches)
        if not toret:
            toret = "No good search result found"
        return toret


class GoogleSearchTool(BuiltinTool):
    def _invoke(self,
                user_id: str,
                tool_parameters: dict[str, Any],
                ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
        """
        query = tool_parameters['query']
        result_type = tool_parameters['result_type']
        api_key = self.runtime.credentials['serpapi_api_key']
        result = SerpAPI(api_key).run(query, result_type=result_type)
        if result_type == 'text':
            return self.create_text_message(text=result)
        return self.create_link_message(link=result)
