import asyncio
import random

import jmcomic
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.core.message.components import File
from jmcomic import *
from astrbot.api.message_components import Node, Nodes, Plain
import time



@register("jm", "xm", "本子", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.downloading = set()  # 存储正在下载的ID
        self.getting_message = set()  # 存储正在浏览的ID

    async def get_message(self, album_id):
        if album_id in self.getting_message:
            return False, "该本子正在查看中，请稍后再试"

        self.getting_message.add(album_id)
        try:
            current_dir = os.path.abspath(os.path.dirname(__file__))
            op_path = os.path.join(current_dir, "op.yml")
            op = create_option_by_file(op_path)
            html_cl = op.new_jm_client()
            album: JmAlbumDetail = html_cl.get_album_detail(album_id=album_id)
            return True, album
        except Exception as e:
            return False, f"未知错误: {str(e)}"
        finally:
            # 确保无论成功与否都移除 album_id
            self.getting_message.discard(album_id)

    # 将同步下载任务包装成异步函数
    async def download_comic_async(self, album_id):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        op_path = os.path.join(current_dir, "op.yml")
        option = create_option_by_file(op_path)
        if album_id in self.downloading:
            return False, "该本子正在下载中，请稍后再试"

        self.downloading.add(album_id)
        try:
            # 将同步下载操作放到线程池中执行，避免阻塞事件循环
            await asyncio.to_thread(jmcomic.download_album, album_id, option)
            return True, None
        except Exception as e:
            return False, f"下载出错: {str(e)}"
        finally:
            self.downloading.discard(album_id)

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
        # op = create_option_by_file(r"D:\PycharmProjects\AstrBot\data\plugins\astrbot_plugin_jm\op.yml")
        # html_cl = op.new_jm_client()
        # album: JmAlbumDetail = html_cl.get_album_detail(album_id=tokens)
        success, result = await self.get_message(tokens)
        if success:
            album = result  # type: JmAlbumDetail
        else:
            yield event.plain_result(result)
            return

        # # 获取并格式化详细信息
        # info_text = (
        #         f"ID: {str(album.id)}\n"
        #         f"标题: {album.name}\n"
        #         f"作者: {album.author if hasattr(album, 'author') else 'default_author'}\n"
        #         f"章节数: {len(album) if hasattr(album, '__len__') else 0}\n"
        #         f"总页数: {album.page_count if hasattr(album, 'page_count') else 0}\n"
        #         f"关键词: {', '.join(album.tags) if hasattr(album, 'tags') and album.tags else '无'}\n"
        #         f"发布日期: {str(album.pub_date) if hasattr(album, 'pub_date') else '0'}\n"
        #         f"最后更新: {str(album.update_date) if hasattr(album, 'update_date') else '0'}\n"
        #         f"点赞数: {str(album.likes) if hasattr(album, 'likes') else '0'}\n"
        #         f"浏览数: {str(album.views) if hasattr(album, 'views') else '0'}\n"
        #         f"评论数: {album.comment_count if hasattr(album, 'comment_count') else 0}\n"
        #         f"作品系列: {', '.join(album.works) if hasattr(album, 'works') and album.works else '无'}\n"
        #         f"角色列表: {', '.join(album.actors) if hasattr(album, 'actors') and album.actors else '无'}\n"
        #         f"相关推荐: \n" +
        #         '\n'.join([
        #             f"  - ID: {related.get('id', '')}, 标题: {related.get('name', '')}, 作者: {related.get('author', '未知')}"
        #             for related in
        #             (album.related_list if hasattr(album, 'related_list') and album.related_list is not None else [])
        #         ])
        # )
        # yield event.plain_result(info_text)

        # 主信息节点
        main_info = (
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
                f"相关推荐:"
        )

        # 创建主信息节点
        main_node = Node(
            uin=1499624522,  # 使用机器人ID作为发送者
            time=int(time.time()),
            content=[Plain(main_info)]
        )

        # 创建相关推荐节点列表
        related_nodes = []
        for i, related in enumerate(
                album.related_list if hasattr(album, 'related_list') and album.related_list else []):
            related_info = (
                f"推荐 #{i + 1}\n"
                f"ID: {related.get('id', '')}\n"
                f"标题: {related.get('name', '')}\n"
                f"作者: {related.get('author', '未知')}"
            )

            related_node = Node(
                uin=1499624522,
                time=int(time.time()) - (i + 1) * 60,  # 按顺序递减时间
                content=[Plain(related_info)]
            )
            related_nodes.append(related_node)

        # 合并所有节点
        all_nodes = [main_node] + related_nodes

        # 创建合并消息
        merged_message = Nodes(nodes=all_nodes)

        # 发送合并消息
        yield event.chain_result([merged_message])

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
        success, result = await self.get_message(album_id)
        if success:
            album = result  # type: JmAlbumDetail
        else:
            yield event.plain_result(f'id={album_id}的本子不存在')
            return

            # 主信息节点
        main_info = (
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
            f"相关推荐:"
        )

        # 创建主信息节点
        main_node = Node(
            uin=1499624522,  # 使用机器人ID作为发送者
            time=int(time.time()),
            content=[Plain(main_info)]
        )

        # 创建相关推荐节点列表
        related_nodes = []
        for i, related in enumerate(
                album.related_list if hasattr(album, 'related_list') and album.related_list else []):
            related_info = (
                f"推荐 #{i + 1}\n"
                f"ID: {related.get('id', '')}\n"
                f"标题: {related.get('name', '')}\n"
                f"作者: {related.get('author', '未知')}"
            )

            related_node = Node(
                uin=1499624522,
                time=int(time.time()) - (i + 1) * 60,  # 按顺序递减时间
                content=[Plain(related_info)]
            )
            related_nodes.append(related_node)

        # 合并所有节点
        all_nodes = [main_node] + related_nodes

        # 创建合并消息
        merged_message = Nodes(nodes=all_nodes)

        # 发送合并消息
        yield event.chain_result([merged_message])

        pdf_path = f"{path}/pdf/{album.id}.pdf"

        # 检查文件是否已存在
        if os.path.exists(pdf_path):
            yield event.plain_result(f"本子 {album.id} 已存在，直接发送")
            yield event.chain_result(
                [File(name=f"{album.id}.pdf", file=pdf_path)]
            )
            return

        # op.download_album(album_id=album_id)
        # 创建配置并开始异步下载
        yield event.plain_result(f"开始下载本子 {album.id}，请稍候...")
        success, error_msg = await self.download_comic_async(album.id)

        if not success:
            yield event.plain_result(error_msg)
            return

        # 检查文件是否下载成功
        if os.path.exists(pdf_path):
            yield event.plain_result(f"本子 {album.id} 下载完成")
            yield event.chain_result(
                [File(name=f"{album.id}.pdf", file=pdf_path)]
            )
            return
        else:
            yield event.plain_result(f"下载完成，但未找到生成的PDF文件，请检查下载路径")
            return

    @filter.command("jm随机")
    async def t(self, event: AstrMessageEvent):
        path = os.path.abspath(os.path.dirname(__file__))
        album_id = random.randint(1, 1100000)
        success, result = await self.get_message(album_id)
        if success:
            album = result  # type: JmAlbumDetail
        else:
            yield event.plain_result(result)
            return

        pdf_path = f"{path}/pdf/{album.id}.pdf"

        # 检查文件是否已存在
        if os.path.exists(pdf_path):
            yield event.plain_result(f"本子 {album.id} 已存在，直接发送")
            yield event.chain_result(
                [File(name=f"{album.id}.pdf", file=pdf_path)]
            )
            return

        # op.download_album(album_id=album_id)
        # 创建配置并开始异步下载
        yield event.plain_result(f"开始下载本子 {album.id}，请稍候...")
        success, error_msg = await self.download_comic_async(album.id)

        if not success:
            yield event.plain_result(error_msg)
            return

        # 检查文件是否下载成功
        if os.path.exists(pdf_path):
            yield event.plain_result(f"本子 {album.id} 下载完成")
            yield event.chain_result(
                [File(name=f"{album.id}.pdf", file=pdf_path)]
            )
            return
        else:
            yield event.plain_result(f"下载完成，但未找到生成的PDF文件，请检查下载路径")
            return
