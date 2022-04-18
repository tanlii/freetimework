from work.freetimework.db.db_model import FreeTimeWorkModel
import datetime


class FreeTimeWorkPipeline:
    def process_item(self, item, spider):
        default = {
            "updated_at": datetime.datetime.now(),
            "created_at": datetime.datetime.now(),
            "status": 1
        }
        for k, v in item.items():
            default.update({k: v})
        try:
            instance, created = FreeTimeWorkModel.get_or_create(
                article_id=item["article_id"],
                defaults=default)
            if not created:
                for k, v in item.items():
                    if hasattr(instance, k):
                        setattr(instance, k, v)
                instance.updated_at = datetime.datetime.now()
                instance.status = 1  # 重置推送状态 0 推送失败 1未推送 2 推送完成
                instance.save()
            print(f"入库：{item['article_id']}")
        except BaseException as e:
            print(e)
        return item
