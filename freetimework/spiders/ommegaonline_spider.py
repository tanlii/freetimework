import scrapy
from freetimework.freetimework.parse.ommegaonlinparse import OmmegaOnlineParse
from freetimework.freetimework.middlewares.create_headers import CreateHeaders
from freetimework.freetimework.items.items import FreeTimeWorkItem
from freetimework.freetimework.utlis.help_md5 import MakeMD5


class OmmegaonlineSpider(scrapy.Spider):
    name = 'ommegaonline_spider'
    channel_name = 'ommegaonline.org'
    channel_id = MakeMD5().get_md5(channel_name)



    def __init__(self):
        self.parse_product = OmmegaOnlineParse()
        self.make_md5 = MakeMD5()
        self.base_url = "https://www.ommegaonline.org"
        self.headers = CreateHeaders()
        self.categories = [
            '/archive/Journal-of-Nanotechnology-and-Materials-Science/22',
            '/archive/International-Journal-of-Cancer-and-Oncology-/24',
            '/archive/Journal-of-Addiction-and-Dependence/41',
            '/archive/Journal-of-Dentistry-and-Oral-Care/30',
            '/archive/Journal-of-Gastrointestinal-Disorders-and-Liver-function/31',
            '/archive/Journal-of-Bioinformatics--Proteomics-and-Imaging-Analysis/33',
            '/archive/Journal-of-Diabetes-and-Obesity/25',
            '/archive/Journal-of-Heart-and-Cardiology-/21',
            '/archive/Journal-of-Analytical--Bioanalytical-and-Separation-Techniques/58',
            '/archive/Journal-of-Gynecology-and-Neonatal-Biology/28',
            '/archive/International-Journal-of-Neurology-and-Brain-Disorders/26',
            '/archive/International-Journal-of-Food-and-Nutritional-Science-/20',
            '/archive/Journal-of-Anesthesia-and-Surgery/23',
            '/archive/Journal-of-Pediatrics-and-Palliative-Care/53',
            '/archive/Journal-of-Pharmacy-and-Pharmaceutics/27',
            '/archive/Journal-of-Medicinal-Chemistry-and-Toxicology-/51',
            '/archive/Journal-of-Veterinary-Science-and-Animal-Welfare/56',
            '/archive/Journal-of-Stem-Cell-and-Regenerative-Biology/45',
            '/archive/Journal-of-Cellular-Immunology-and-Serum-Biology/34',
            '/archive/Journal-of-Environment-and-Health-Science-/19',
            '/archive/Investigative-Dermatology-and-Venereology-Research/32',
            '/archive/Journal-of-Marine-Biology-and-Aquaculture/29',
            '/archive/International-Journal-of-Hematology-and-Therapy/44',
            '/archive/Letters-in-Health-and-Biological-Sciences/46']

    def start_requests(self):
        for category in self.categories:
            url = self.base_url + category
            yield scrapy.Request(
                url=url,
                headers=self.headers.create_headers(),
                callback=self.parse_publish,
                meta={

                }
            )

    # 解析期刊期卷链接
    def parse_publish(self, response):
        html = response.text
        journal_url = response.url
        category_id = journal_url.split('/')[-1]
        next_page = self.parse_product.parse_next_page(html, category_id)
        if not next_page:
            return
        for issue_url, issue_name in next_page.items():
            url = self.base_url + issue_url
            yield scrapy.Request(
                url=url,
                headers=self.headers.create_headers(),
                callback=self.parse_article_list,
                meta={
                    "journal_url": journal_url,
                }
            )

    # 解析期卷中的文章链接
    def parse_article_list(self, response):
        html = response.text
        journal_url = response.meta["journal_url"]
        articles = self.parse_product.parse_next_page(html)
        for article in articles:
            url = article["article_url"]
            meta = {"journal_url": journal_url}
            meta.update(article)
            yield scrapy.Request(
                url=url,
                headers=self.headers.create_headers(),
                callback=self.parse,
                meta=meta
            )

    def parse(self, response):
        html = response.text
        meta = response.meta
        product = self.parse_product.parse(html)

        item = FreeTimeWorkItem()
        item["channel_id"] = self.channel_id
        item["channel_name"] = self.channel_name
        item["publisher"] = "ommega"
        journal_url = meta["journal_url"]
        journal_name = [i for i in journal_url.split('/') if 'Journal' in i][0]
        item["journal_url"] = journal_url
        item["journal_name"] = journal_name
        item["journal_id"] = self.make_md5.get_md5(journal_name)
        item["article_id"] = self.make_md5.get_md5(product["article_title"])
        item["article_title"] = product["article_title"]
        item["article_url"] = meta["article_url"]
        item["article_pdf_url"] = meta["article_pdf_url"]
        item["article_abstract"] = product["article_abstract"]
        item["author"] = product["author"]
        item["email"] = product["email"]
        item["company"] = None

        yield item
