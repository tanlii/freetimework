import re
import difflib


class OmmegaOnlineParse:
    def __init__(self):
        pass

    def parse(self, res_content):
        product = dict()
        email_author = self.parse_email_author(res_content)
        product["author"] = email_author.get("author")
        product["email"] = email_author.get("email")
        product["article_abstract"] = self.parse_abstract(res_content)
        product["article_title"] = self.parse_title(res_content)
        product["journal_name"] = self.parse_journal_name(res_content)
        return product

    def parse_journal_name(self, res_content):
        journal_name = ''
        pattern = r'<meta name="citation_journal_title" content="([^"]+)"'
        res = re.findall(pattern, res_content, re.S)
        if res:
            journal_name = res[0]
        return journal_name

    def parse_title(self, res_content):
        title = ''
        pattern = r' <title>(.*?)</title>'
        res = re.findall(pattern, res_content, re.S)
        if res:
            title = res[0]
        return title

    def parse_author(self, res_content):
        author_names = []
        pattern_author = r'name="citation_author" content="(.{1,50})"'
        res_author = re.findall(pattern_author, res_content, re.S)
        if res_author:
            author_name = res_author[0].replace('<br>', ',').split(',')
            author_names = [
                name.replace('</sub>', '').replace('<sub>', '_').replace('\n', '').strip() for
                name in author_name]
        return author_names

    def parse_email_author(self, res_content):
        email_author = dict()
        pattern = '<h2>Corresponding Author</h2>.{1,100}<p[^>]*>(.{1,500})<a[^>]*>(.{1,50})</a>'
        res = re.findall(pattern, res_content, re.S)
        print(res)
        if res:
            author = res[0][0].split(',')[0].split('>')[1].strip()
            email = res[0][1]
            email_author.update({
                "author": author,
                "email": email
            })
        return email_author

    def parse_email(self, res_content, authors):
        pattern = r'[[A-Za-z0-9]*[.-_]]*[A-Za-z0-9]+@[A-Za-z0-9-]+[\.[A-Z|a-z]{2,}]*'
        res = re.findall(pattern, res_content, re.S)
        print(res)
        if res:
            scores = []
            for email in res:
                for author in authors:
                    ratio = difflib.SequenceMatcher(None, author.replace(' ', ''), email.split('@')[0]).quick_ratio()
                    scores.append(
                        {
                            "author": author,
                            "email": email,
                            "ratio": ratio
                        }
                    )
            print(scores)
            if not scores:
                return
            sorted_scores = sorted(scores, key=lambda x: x["ratio"], reverse=True)
            a = [x for x in sorted_scores if x["ratio"] >= 0.4]
            if a:
                return a
            else:
                return [sorted_scores[0]]

    def parse_abstract(self, res_content):
        pattern = r'<div class="article_info_block1" id="ABSTRACT">(.*?)</div>'
        res = re.findall(pattern, res_content, re.S)
        if res:
            return res[0]

    def parse_next_page(self, res_content, category_id):
        next_page = {}
        pattern = rf'<a href="(/archive-view/' + category_id + '[^"]{1,10})" title="">([^<]{1,50})</a>'
        res = re.findall(pattern, res_content, re.S)
        if res:
            next_page = dict(res)

        return next_page

    def parse_article_list(self, res_content):
        def parse_url_title(article_info):
            res_urls = pattern_url_title.findall(article_info)
            print(res_urls)
            if res_urls:
                return res_urls[0]

        def parse_pdf_url(article_info):
            res_pdf = pattern_pdf.findall(article_info)
            if res_pdf:
                return res_pdf[0]

        article_list = []
        pattern_article = r'<article.*?</article>'
        res = re.findall(pattern_article, res_content, re.S)
        if not res:
            return
        pattern_url_title = re.compile(r'href="(.{1,50}/article-details/[^"]{1,200})" title="([^"]{1,300})">', re.S)
        pattern_pdf = re.compile(r'href="(.{1,50}/articles/publishimages/.{1,100}\.pdf)"', re.S)
        # pattern_author = re.compile(r'<span class="qodef-quote-author">(.{1,300})</span>', re.S)
        for row in res:
            url_title = parse_url_title(row)
            if not url_title:
                continue
            # author = parse_author(row)
            pdf_url = parse_pdf_url(row)
            article_list.append({
                "article_url": url_title[0],
                "article_title": url_title[1],
                # "article_author": author,
                "article_pdf_url": pdf_url
            })

        return article_list


if __name__ == '__main__':
    p = OmmegaOnlineParse()
    html = ''
    res = p.parse(html)
    print(res)
