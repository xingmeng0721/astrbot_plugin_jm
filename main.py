from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core.message.components import File
from jmcomic import *


@register("jm", "xm", "本子", "1.0.0")
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
        info_text = (
                f"ID: {str(album.id)}\n"
                f"标题: {album.name}\n"
                f"作者: {album.author if hasattr(album, 'author') else 'default_author'}\n"
                f"章节数: {len(album) if hasattr(album, '__len__') else 0}\n"
                f"总页数: {album.page_count if hasattr(album, 'page_count') else 0}\n"
                f"关键词: {', '.join(album.tags) if hasattr(album, 'tags') and album.tags else '无'}\n"
                f"发布日期: {str(album.pub_date) if hasattr(album, 'pub_date') else '0'}\n"
                f"最后更新: {str(album.update_date) if hasattr(album, 'update_date') else '0'}\n"
                f"点赞数: {str(album.likes) if hasattr(album, 'likes') else '0'}\n"
                f"浏览数: {str(album.views) if hasattr(album, 'views') else '0'}\n"
                f"评论数: {album.comment_count if hasattr(album, 'comment_count') else 0}\n"
                f"作品系列: {', '.join(album.works) if hasattr(album, 'works') and album.works else '无'}\n"
                f"角色列表: {', '.join(album.actors) if hasattr(album, 'actors') and album.actors else '无'}\n"
                f"相关推荐: \n" +
                '\n'.join([
                    f"  - ID: {related.get('id', '')}, 标题: {related.get('name', '')}, 作者: {related.get('author', '未知')}"
                    for related in
                    (album.related_list if hasattr(album, 'related_list') and album.related_list is not None else [])
                ])
        )
        yield event.plain_result(info_text)
        return

    @filter.command("jmd")
    async def jmd(self, event: AstrMessageEvent):
        path = os.path.abspath(os.path.dirname(__file__))
        messages = event.get_messages()
        if not messages:
            yield event.plain_result("未收到消息")
            return

        message_text = messages[0].text.strip()
        parts = message_text.split()

        if len(parts) < 2:
            yield event.plain_result("格式错误，请提供正确的参数")
            return

        album_id = parts[1]
        op = create_option_by_file(r"D:\PycharmProjects\AstrBot\data\plugins\astrbot_plugin_jm\op.yml")
        html_cl = op.new_jm_client()
        try:
            album: JmAlbumDetail = html_cl.get_album_detail(album_id=album_id)
        except MissingAlbumPhotoException as e:
            yield event.plain_result(f'id={e.error_jmid}的本子不存在')
            return
        if album.id != album_id:
            yield event.plain_result(f'id={album_id}的本子号错误')
            yield event.plain_result(f'搜索id={album.id}的本子')

        pdf_path = f"{path}/pdf/{album.id}.pdf"

        # 检查文件是否已存在
        if os.path.exists(pdf_path):
            yield event.plain_result(f"本子 {album.id} 已存在，直接发送")
            yield event.chain_result(
                [File(name=f"{album.id}.pdf", file=pdf_path)]
            )
            return

        op.download_album(album_id=album_id)
        # 检查文件是否下载成功
        if os.path.exists(pdf_path):
            yield event.plain_result(f"本子 {album.id} 下载完成")
            yield event.chain_result(
                [File(name=f"{album.id}.pdf", file=pdf_path)]
            )
        else:
            yield event.plain_result(f"下载完成，但未找到生成的PDF文件，请检查下载路径")
