import asyncio
import json
import subprocess
from pathlib import Path

from jmcomic import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from data.plugins.astrbot_plugin_jm.data import test




@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)


    @filter.command("jm")
    async def jm(self, event: AstrMessageEvent):
        messages = event.get_messages()
        if not messages:
            yield event.plain_result("未收到消息")
            return

        message_text = messages[0].text.strip()
        parts = message_text.split()

        if len(parts) < 2:
            yield event.plain_result("格式错误，请提供正确的参数")
            return

        tokens = parts[1]
        op = create_option_by_file(r"D:\PycharmProjects\AstrBot\data\plugins\astrbot_plugin_jm\op.yml")
        html_cl = op.new_jm_client()
        album: JmAlbumDetail = html_cl.get_album_detail(album_id=tokens)
        # 获取并格式化详细信息
        info= {
            "ID": str(album.id),
            "标题": album.name,
            "作者": album.author if hasattr(album, 'author') else 'default_author',
            "章节数": len(album) if hasattr(album, '__len__') else 0,
            "总页数": album.page_count if hasattr(album, 'page_count') else 0,
            "关键词": ', '.join(album.tags) if hasattr(album, 'tags') and album.tags else '无',
            "发布日期": str(album.pub_date) if hasattr(album, 'pub_date') else '0',
            "最后更新": str(album.update_date) if hasattr(album, 'update_date') else '0',
            "点赞数": str(album.likes) if hasattr(album, 'likes') else '0',
            "浏览数": str(album.views) if hasattr(album, 'views') else '0',
            "评论数": album.comment_count if hasattr(album, 'comment_count') else 0,
            "作品系列": ', '.join(album.works) if hasattr(album, 'works') and album.works else '无',
            "角色列表": ', '.join(album.actors) if hasattr(album, 'actors') and album.actors else '无',
            "相关推荐": [
                {"ID": related.get('id', ''), "标题": related.get('name', ''), "作者": related.get('author', '未知')}
                for related in
                (album.related_list if hasattr(album, 'related_list') and album.related_list is not None else [])
            ]
        }
        yield event.plain_result(info)
        return




