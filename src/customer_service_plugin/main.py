import json
import time
from threading import Timer
from typing import Optional

import openai
from omni_bot_sdk.plugins.interface import (
    Bot,
    Plugin,
    PluginExcuteContext,
    PluginExcuteResponse,
    MessageType,
    SendTextMessageAction,
)
from pydantic import BaseModel

from dingtalk import *


class CustomerServicePluginConfig(BaseModel):
    """
        上下文插件配置
        enabled: 是否启用该插件
        priority: 插件优先级，数值越大优先级越高
        """

    enabled: bool = False
    priority: int = 1001
    openai_api_key: str = "unknown"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    prompt: str = (
        "你是一个客服机器人，请根据当前群聊中的历史消息综合判断是否发生了投诉行为。你的返回消息要严格遵守'{bool_res}|{reason}'其中bool_res取“True”或“False”，reason是你的判断理由。历史消息：{{chat_history}} 当前时间：{{time_now}} "
        "你的昵称：{{self_nickname}} 群昵称：{{room_nickname}} 消息来自于：{{contact_nickname}}"
    )
    min_session_length: int = 10  # 最小会话长度，少于这个长度不进行AI回复
    cooling_time: int = 7200  # 群聊冷却时间，单位为秒，默认2小时

    ding_app_key: str = "unknown"
    ding_app_secret: str = "unknown"
    union_id: str = "unknown"
    workbook_id: str = "unknown"
    sheet_id: str = "unknown"


class CustomerServicePlugin(Plugin):
    """
    客服插件
    """

    priority = 1001
    name = "customer-service-plugin"
    chat_rooms = []

    def __init__(self, bot: "Bot"):
        super().__init__(bot)
        self.api_key = self.plugin_config.openai_api_key
        self.base_url = self.plugin_config.openai_base_url
        self.model = self.plugin_config.openai_model
        self.enabled = self.plugin_config.enabled
        self.priority = getattr(self.plugin_config, "priority", self.__class__.priority)
        self.user = bot.user_info
        self.prompt = self.plugin_config.prompt
        openai.api_key = self.api_key
        openai.base_url = self.base_url
        self.min_session_length = self.plugin_config.min_session_length
        self.cooling_time = self.plugin_config.cooling_time

        self.ding_app_key = self.plugin_config.ding_app_key
        self.ding_app_secret = self.plugin_config.ding_app_secret
        self.union_id = self.plugin_config.union_id
        self.workbook_id = self.plugin_config.workbook_id
        self.sheet_id = self.plugin_config.sheet_id
        self.oauth = Oauth(
            app_key=self.ding_app_key,
            app_secret=self.ding_app_secret
        )

        self.room_update_time = {}
        self.room_timers = {}  # 用于存储群聊的定时器

    def get_ai_response(self, msg, chat_history) -> Optional[str]:
        if not self.enabled:
            return None
        try:
            # 构造 OpenAI 聊天消息，历史消息作为知识背景，拼接到 prompt 占位符
            messages = []
            # 支持多变量替换
            time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            system_prompt = self.prompt
            system_prompt = system_prompt.replace(
                "{{chat_history}}", chat_history or ""
            )
            system_prompt = system_prompt.replace("{{time_now}}", time_now)
            # 下面变量由用户手动创建和传递，这里默认字符串
            system_prompt = system_prompt.replace(
                "{{self_nickname}}", self.user.nickname
            )
            system_prompt = system_prompt.replace(
                "{{room_nickname}}", msg.room.display_name if msg.room else ""
            )
            system_prompt = system_prompt.replace(
                "{{contact_nickname}}", msg.contact.display_name if msg.contact else ""
            )
            messages.append({"role": "system", "content": system_prompt})
            self.logger.debug(f"构造的系统提示: {system_prompt}")
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                user=msg.room.username if msg.is_chatroom else msg.contact.username,
            )
            # OpenAI 返回格式
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            self.logger.error(f"获取AI响应时出错: {e}")
            return None

    def get_priority(self) -> int:
        return self.priority

    def get_plugin_name(self) -> str:
        return self.name

    def get_plugin_description(self) -> str:
        return "客服插件"

    @classmethod
    def get_plugin_config_schema(cls):
        return CustomerServicePluginConfig

    async def handle_message(self, plusginExcuteContext: PluginExcuteContext) -> None:
        """
        处理接收到的消息
        文本消息，引用消息处理，其他都先不处理
        文本消息要判断是不是 at 我，或者是不是引用了我
        前面的上下文插件会在上下文中添加 not_for_bot 字段，如果为True，则不进行AI回复
        """
        if not self.enabled:
            return
        message = plusginExcuteContext.get_message()
        if (
                message.local_type != MessageType.Text
                and message.local_type != MessageType.Quote
        ):
            return
        context = plusginExcuteContext.get_context()
        chat_history = context.get("chat_history", "")
        self.logger.debug(f"当前消息数量: {len(json.loads(chat_history))}")
        if len(json.loads(chat_history)) < self.min_session_length:
            return
        self.chat_rooms = self.read_all_chat_rooms()
        self.logger.info(f"读取到的群聊列表: {self.chat_rooms}")
        # 增加判断条件，如果是私聊，直接可以响应
        if message.is_chatroom:
            # 从room_timers中判断该群聊计时器是否存在，存在则重置时间，否则创建一个新的计时器，计时到23:00时执行process_room方法
            # 计算当前时间距离23：00的秒数，创建一个新的计时器
            count_down = (23 - time.localtime().tm_hour) * 3600 - time.localtime().tm_min * 60 - time.localtime().tm_sec
            if message.room.display_name not in self.room_timers:
                timer = Timer(count_down, self.process_room, args=(message, chat_history))
                timer.start()
                self.room_timers[message.room.display_name] = timer
            else:
                # 重置现有的计时器
                self.room_timers[message.room.display_name].cancel()
                self.room_timers[message.room.display_name] = Timer(count_down, self.process_room,
                                                                    args=(message, chat_history))
                self.room_timers[message.room.display_name].start()
        else:
            # 私聊的消息，直接使用Dify的工作流回复
            response = self.get_ai_response(msg=message, chat_history=chat_history)
            plusginExcuteContext.add_response(
                PluginExcuteResponse(
                    message=message,
                    plugin_name=self.name,
                    should_stop=True,
                    actions=[
                        SendTextMessageAction(
                            content=response,
                            target=(
                                message.room.display_name
                                if message.room
                                else message.contact.display_name
                            ),
                            is_chatroom=message.is_chatroom,
                        )
                    ],
                )
            )
        plusginExcuteContext.should_stop = True

    def process_room(self, message, chat_history):
        # if self.room_update_time.get(message.room.display_name, 0) + self.cooling_time > time.time():
        #     self.logger.info(f"群聊 {message.room.display_name} 最近已更新，跳过处理")
        #     return
        response = self.get_ai_response(msg=message, chat_history=chat_history)
        self.logger.info(f"AI响应: {response}")
        is_complaint, complaint = response.split('|')
        self.update_chat_room(message.room.display_name, is_complaint, complaint)
        self.room_update_time[message.room.display_name] = time.time()

    def read_all_chat_rooms(self):
        # 获取 access_token
        resp = self.oauth.main()
        access_token = resp['accessToken']

        read_sheet = ReadSheet()
        chat_rooms = read_whole_column('B', access_token, read_sheet, self.union_id, self.workbook_id, self.sheet_id)
        return chat_rooms

    def update_chat_room(self, room_name, is_complaint, complaint):
        resp = self.oauth.main()
        access_token = resp['accessToken']

        # try:
        #     index = self.chat_rooms.index(room_name) + 2
        # except ValueError:
        index = len(self.chat_rooms) + 2
        write_sheet = WriteSheet()
        write_row(f'B{index}:E{index}',
                  [[room_name, is_complaint, complaint, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())]],
                  access_token, write_sheet, self.union_id, self.workbook_id, self.sheet_id, )
