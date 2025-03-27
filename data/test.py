import io
import sys
from pathlib import Path
import jmcomic
from jmcomic import JmAlbumDetail, create_option_by_file
import json

def get_album_info(album_id):
    op = create_option_by_file(r'D:\PycharmProjects\AstrBot\data\plugins\fatetrial_jmdownloader\option.yml')
    html_cl = op.new_jm_client()
    album: JmAlbumDetail = html_cl.get_album_detail(album_id=album_id)
    # 获取并格式化详细信息
    return   {
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


if __name__ == "__main__":
    info=get_album_info("123456")
    print(info)
    output_file = Path(__file__).parent / f"album_{123456}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=4)
        print(f"JSON 文件已生成: {output_file}")