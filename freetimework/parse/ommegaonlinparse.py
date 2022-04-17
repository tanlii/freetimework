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
        pattern = '<h2>Corresponding Author</h2>.*?<p [^>]+>(.*?)<a[^>]+>(.{1,50})</a>'
        res = re.findall(pattern, res_content, re.S)
        if res:
            author = res[0][0].split(',')[0].replace('<p>', '').strip()
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
    html = '''
<!DOCTYPE html>
<html class="js flexbox flexboxlegacy canvas canvastext no-touch hashchange history draganddrop rgba hsla multiplebgs backgroundsize borderimage borderradius boxshadow textshadow opacity cssanimations csscolumns cssgradients no-cssreflections csstransforms csstransforms3d csstransitions fontface generatedcontent video audio svg inlinesvg svgclippaths js_active  vc_desktop  vc_transform  js flexbox flexboxlegacy canvas canvastext no-touch hashchange history draganddrop rgba hsla multiplebgs backgroundsize borderimage borderradius boxshadow textshadow opacity cssanimations csscolumns cssgradients no-cssreflections csstransforms csstransforms3d csstransitions fontface generatedcontent video audio svg inlinesvg svgclippaths js_active  vc_desktop  vc_transform " lang="en" xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-64293058-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'UA-64293058-1');
</script>

    <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    <link rel="shortcut icon" type="image/x-icon" href="https://www.ommegaonline.org/images/favicon.ico">
    <style>
        @font-face {
            font-family: 'georgia';
            src: url('fonts/georgia/GeorgiaRegularfont.ttf') format('truetype');
        }
        .article_info_block1 p {
            font-size: 18px;
        }
        .pdfimg {
            margin-left: 7px;
        }
        p{
            color: black !important;
font-size: 15px !important;
        }
    </style>
    <script language="javascript" type="text/javascript">
        function resizeIframe(obj) {
            obj.style.height = obj.contentWindow.document.body.scrollHeight + 'px';
        }
    </script>



            




  


    <link rel="stylesheet" href="https://www.ommegaonline.org/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/ommegacss.css">
    <link rel="profile" href="http://gmpg.org/xfn/11">
    <link rel="css" href="http://www.ghouse-sa.com/wp-content/themes/bridge/framework/admin/assets/css/scss/qodef-ui/qodef-ui.scss">
    <meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
    <meta name=keywords content="Materials-Science; Rescue Technology">
    <meta name=description content="" >
       <meta name="citation_title" content="View point of Nanotechnology and Material Science " />
     <meta name="citation_author" content="Kenji  Uchino" />
     <meta name='citation_author' content=''/>     
     <meta name="citation_author" content="Ommega Internationals">

     <meta name="citation_publication_date" content="2014-12-28">
     <meta name="citation_journal_title" content="Journal of Nanotechnology and Materials Science" />

     <meta name="citation_year" content="2014" />

     <meta name="citation_volume"  content="1" />

     <meta name="citation_issue" content="1" />

     

    <meta name="citation_firstpage" content="1" />
    <meta name="citation_lastpage" content="2" />
    <meta name="citation_DOI" content="10.15436/2377-1372.14.e001" />
    
    <meta name="citation_publisher" content="Ommega Internationals" />

     <meta name="citation_pdf_url" content="https://www.ommegaonline.org/articles/publishimages/14999-Viewpoint-of-Nanotechnology-and-Material-Science.pdf" />
     <meta name="citation_fulltext_html_url" content="https://www.ommegaonline.org/article-details/article/63  "/>
     <meta name="citation_xml_url" content="https://www.ommegaonline.org/home/articlexml/63"/>
     
     <meta name="citation_issn" content="2377-1372"/>
    <title>View point of Nanotechnology and Material Science </title>

    <script type="text/javascript" src="https://www.ommegaonline.org/js/wp-emoji-release.min.js"></script>
    <style type="text/css">
        img.wp-smiley,
        img.emoji {
            display: inline !important;
            border: none !important;
            box-shadow: none !important;
            height: 1em !important;
            width: 1em !important;
            margin: 0 .07em !important;
            vertical-align: -0.1em !important;
            background: none !important;
            padding: 0 !important;
        }
    </style>
    <link rel="stylesheet" id="layerslider-css" href="https://www.ommegaonline.org/css/layerslider.css" type="text/css" media="all">
    <!-- <link rel="stylesheet" id="ls-google-fonts-css" href=
        ald:300,regular,700&amp;subset=latin%2Clatin-ext" type="text/css" media="all"> -->
    <link rel="stylesheet" id="contact-form-7-css" href="https://www.ommegaonline.org/css/styles.css" type="text/css" media="all">
    <link rel="stylesheet" id="contact-form-7-css" href="https://www.ommegaonline.org/css/blog.min.css" type="text/css" media="all">
    <link rel="stylesheet" id="rs-plugin-settings-css" href="https://www.ommegaonline.org/css/settings.css" type="text/css" media="all">
    <style id="rs-plugin-settings-inline-css" type="text/css">
        #rs-demo-id {}
    </style>
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/style.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/plugins.min.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/modules.min.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/modules-responsive.min.css" type="text/css" media="all">
    <link rel="stylesheet" id="qodef_font_elegant-css" href="https://www.ommegaonline.org/css/style.min.css" type="text/css" media="all">
    <link rel="stylesheet" id="qodef_ion_icons-css" href="https://www.ommegaonline.org/css/ionicons.min.css" type="text/css" media="all">
    <link rel="stylesheet" id="qodef_simple_line_icons-css" href="https://www.ommegaonline.org/css/simple-line-icons.css" type="text/css" media="all">
    <link rel="stylesheet" id="qodef_dripicons-css" href="https://www.ommegaonline.org/css/dripicons.css" type="text/css" media="all">
    <link rel="stylesheet" id="contact-form-7-css" href="https://www.ommegaonline.org/css/blog.min.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/woocommerce.min.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/woocommerce-responsive.min.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/style_dynamic.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/blog-responsive.min.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/style_dynamic_responsive.css" type="text/css" media="all">
    <link rel="stylesheet" href="https://www.ommegaonline.org/css/toolbar.css" type="text/css" media="all">
    <link rel="stylesheet" id="js_composer_front-css" href="https://www.ommegaonline.org/css/js_composer.min.css" type="text/css" media="all">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <!-- <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Raleway%3A100%2C100italic%2C200%2C200italic%2C300%2C300italic%2C400%2C400italic%2C500%2C500italic%2C600%2C600italic%2C700%2C700italic%2C800%2C800italic%2C900%2C900italic%7CRaleway%3A100%2C100italic%2C200%2C200italic%2C300%2C300italic%2C400%2C400italic%2C500%2C500italic%2C600%2C600italic%2C700%2C700italic%2C800%2C800italic%2C900%2C900italic&amp;subset=latin%2Clatin-ext" type="text/css" media="all"> -->
    <!-- This site uses the Google Analytics by MonsterInsights plugin v5.5.2 - Universal enabled - https://www.monsterinsights.com/ -->
  <!--  <script>
        (function(i, s, o, g, r, a, m) {
            i['GoogleAnalyticsObject'] = r;
            i[r] = i[r] || function() {
                (i[r].q = i[r].q || []).push(arguments)
            }, i[r].l = 1 * new Date();
            a = s.createElement(o),
                m = s.getElementsByTagName(o)[0];
            a.async = 1;
            a.src = g;
            m.parentNode.insertBefore(a, m)
        })(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');
        ga('create', 'UA-64293058-1', 'auto');
        ga('send', 'pageview');
    </script>-->
    <!-- / Google Analytics by MonsterInsights -->
    <script type="text/javascript" src="https://www.ommegaonline.org/js/jquery.js"></script>
    <script type="text/javascript" src="https://www.ommegaonline.org/js/jquery-migrate.min.js"></script>
    <script type="text/javascript" src="https://www.ommegaonline.org/js/scrolltoplugin.min.js"></script>
    <script type="text/javascript" src="https://www.ommegaonline.org/js/greensock.js"></script>
    <script type="text/javascript">
        /* <![CDATA[ */
        var LS_Meta = {
            "v": "5.6.8"
        };
        /* ]]> */
    </script>
    <!-- added by clarigo  -->
    <style type="text/css">
        #sticky {
            /*padding: 0.5ex;*/
            /*border-radius: 0.5ex;*/
            
            float: left;
        }
        #sticky.stick {
            position: fixed;
            top: 0;
            z-index: 10;
            border-radius: 0 0 0.5em 0.5em;
        }
        .content-holder {
            /*margin-left:100px;*/
        }
        #footer {
            /*width:100%;*/
            /*height:600px;*/
            /*background:#ccc;*/
            
            z-index: 999999
        }
    </style>
    <link rel="shortcut icon" type="image/x-icon" href="">
    <style type="text/css">
        .qodef-landing-custom .qodef-ptf-category-holder {
            display: none !important;
        }
        .qodef-landing-custom .qodef-portfolio-list-holder-outer.qodef-ptf-standard article .qodef-item-image-holder {
            border-radius: 3px 3px 0 0;
            backface-visibility: hidden;
        }
        .qodef-landing-custom .qodef-item-title {
            text-align: center !important;
            padding: 28px 0 37px 0 !important;
        }
        .qodef-landing-custom .qodef-item-icons-holder .qodef-like,
        .qodef-landing-custom .qodef-item-icons-holder .qodef-portfolio-lightbox {
            display: none !important;
        }
        .qodef-landing-custom .qodef-portfolio-item .qodef-portfolio-shader {
            display: none !important;
        }
        .qodef-landing-custom .qodef-portfolio-list-holder-outer.qodef-ptf-standard article .qodef-item-icons-holder {
            width: 100%;
            top: -25%;
            left: 0;
            bottom: 0;
            height: 100%;
            padding: 0;
            -webkit-transform: translateY(0) scale(0);
            -ms-transform: translateY(0) scale(0);
            transform: translateY(0) scale(0);
            background-color: rgba(0, 0, 0, 0.15);
            border-radius: 100%;
            padding: 50% 0;
            display: block;
            -webkit-transition: -webkit-transform .5s cubic-bezier(.4, 0, .2, 1), opacity .2s;
            transition: transform .5s cubic-bezier(.4, 0, .2, 1), opacity .2s;
        }
        .qodef-landing-custom .qodef-portfolio-list-holder-outer.qodef-ptf-standard article:hover .qodef-item-icons-holder {
            opacity: 1;
            -webkit-transform: translateY(0) scale(1.2);
            -ms-transform: translateY(0) scale(1.2);
            transform: translateY(0) scale(1.2);
            -webkit-transition: -webkit-transform .35s cubic-bezier(.4, 0, .2, 1), opacity .35s;
            transition: transform .35s cubic-bezier(.4, 0, .2, 1), opacity .35s;
        }
        .qodef-landing-custom .qodef-item-icons-holder .qodef-preview {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: transparent !important;
            border: none !important;
            -ms-transform: translateY(0) rotate(0);
            -webkit-transform: translateY(0) rotate(0);
            transform: translateY(0) rotate(0);
        }
        .qodef-landing-custom .qodef-portfolio-list-holder article .qodef-item-icons-holder a:hover {
            -ms-transform: translateY(0) rotate(0);
            -webkit-transform: translateY(0) rotate(0);
            transform: translateY(0) rotate(0);
        }
        .qodef-landing-custom .qodef-item-icons-holder .qodef-preview:before {
            content: "\f002" !important;
            font-size: 22px;
            position: relative;
            top: 50%;
            -webkit-transform: translateY(-65%) translateX(-50%);
            -ms-transform: translateY(-75%) translateX(-50%);
            transform: translateY(-75%) translateX(-50%);
            width: 60px;
            height: 60px;
            display: block;
            background: #b2dd4c;
            border-radius: 100%;
            text-align: center;
            line-height: 60px;
            left: 50%;
        }
        .page-id-2689 .qodef-page-header .qodef-position-right,
        .page-id-2689 .qodef-sticky-holder,
        .page-id-2689 footer,
        .page-id-2689 #qodef-back-to-top {
            display: none !important;
        }
        .page-id-2689 #qodef-particles .qodef-p-content {
            width: auto;
        }
        .qodef-va-fix {
            vertical-align: middle;
        }
        .qodef-sticky-holder{
            display: none;
        }
         
        @media only screen and (max-width: 1284px) {
            .page-id-3520.qodef-header-vertical footer .qodef-four-columns .qodef-column {
                width: 49.5%;
                min-height: initial !important;
            }
        }
        @media only screen and (max-width: 1024px) {
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(1) .qodef-slider-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(3) .qodef-slider-content {
                padding-right: 80px;
            }
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(1) .qodef-graphic-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(3) .qodef-graphic-content {
                padding-right: 0;
            }
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(2) .qodef-graphic-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(4) .qodef-graphic-content {
                display: none;
            }
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(2) .qodef-slider-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(4) .qodef-slider-content {
                padding-left: 80px;
            }
            .qodef-top-bar-mobile-hide .qodef-top-bar{
                display: block;
                height:100px;
            }
            .qodef-sticky-up-mobile-header .mobile-header-appear .qodef-mobile-header-inner{
                position:relative;
            }
            .menu-item #text-9 p{
                padding: 0 0 0 10px !important;
            }
            .hide-mobile img{
                height: 100px !important;
            }
        }
        @media only screen and (max-width: 768px) {
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(1) .qodef-slider-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(3) .qodef-slider-content {
                padding-left: 80px;
            }
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(1) .qodef-graphic-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(3) .qodef-graphic-content {
                display: none;
            }
            .page-id-3520.qodef-header-vertical footer .qodef-four-columns .qodef-column {
                width: 100%;
                min-height: initial !important;
            }
            .qodef-two-columns-75-25 .qodef-column1 .qodef-column-inner,
            #sidebar-1 .qodef-column-inner
            {
                padding:0;
            }
            .qodef-two-columns-75-25 .side_bar_inner2{
                margin: 0 !important;
                float: none;
                width: 100% !important;
            }
            .qodef-carousel-holder{display: none;}
            h2{
                font-size:32px;
                margin-bottom: 10px;
            }
            footer .widget input[type="text"], footer .widget select{
                margin: 0 !important;
                margin-bottom: 20px !important;
            }
            .flatnon{
                float:none !important;
            }
            .flatnon a{
                display: block;
                width: 100%;
            }
            .qodef-mobile-menu-opener{
                margin-left: -5px;
            }
            .qodef-wrapper-inner{
                opacity: 1 !important;
            }
            .qodef-mobile-nav{
                width: 100%;
            }
            .qodef-vertical-align-containers .qodef-position-center{
                width: 90%;
                left: 5%;
            }
            .qodef-mobile-header .qodef-mobile-menu-opener{
                z-index: 3; 
            }
            .qodef-content-has-sidebar .container{
                width:100% !important;
            }
            #sidebar-1{
                position: relative !important;
                top:0 !important;
                margin-top:0 !important;
            }
            #sidebar-1 .article_details_sidebar{
                margin-top:0 !important;
            }
            #sidebar-1 .qodef-item-text-holder table td:first-child{
                display: none;
            }
            #sidebar-1 .article_share_info{
                padding: 12px;
            }
            .subscription .qodef-custom-font-holder{
                font-size: 25px !important;
            }
        }
        @media only screen and (max-width: 480px) {
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(1) .qodef-slider-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(2) .qodef-slider-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(3) .qodef-slider-content,
            .page-id-2476 #qodef-meetup-slider.carousel .carousel-inner .item:nth-child(4) .qodef-slider-content {
                padding-left: 20px;
            }
        }
        .landing-new-custom .qodef-portfolio-item .qodef-portfolio-shader {
            background-color: rgba(34, 34, 34, 0.8);
            -webkit-transform: scale(1);
            -ms-transform: scale(1);
            transform: scale(1);
            border-radius: 0;
            top: 0;
            left: 0;
            padding: 0;
            border-radius: 15px;
        }
        .landing-new-custom .qodef-portfolio-list-holder-outer .qodef-item-title {
            font-size: 22px;
            color: #fff;
            font-weight: 700;
        }
        .landing-new-custom .qodef-portfolio-list-holder-outer .qodef-item-text-holder .qodef-ptf-category-holder {
            display: none;
        }
        .landing-new-custom .qodef-portfolio-list-holder-outer article {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 4px 4px 15px #c3c3c3;
            transform: translateZ(0px);
        }
        .landing-new-custom .qodef-portfolio-filter-holder .qodef-portfolio-filter-holder-inner ul li span {
            font-size: 16px;
            color: #686868;
        }
        .landing-new-custom .qodef-portfolio-filter-holder .qodef-portfolio-filter-holder-inner ul li span:hover {
            color: #b2dd4c;
        }
        .landing-new-custom .qodef-portfolio-filter-holder {
            margin-bottom: 86px;
        }
    </style>
    <style type="text/css" data-type="vc_custom-css">
        @media only screen and (max-width: 480px) {
            .iwt-custom-fix .qodef-icon-shortcode {
                margin-left: 0 !important;
            }
        }
    </style>
    <style type="text/css" data-type="vc_shortcodes-custom-css">
        .vc_custom_1469616180967 {
            padding-top: 77px !important;
        }
        .vc_custom_1469176263584 {
            background-color: #f6f6f6 !important;
        }
        .vc_custom_1469613162058 {
            padding-top: 140px !important;
            padding-bottom: 155px !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-size: cover !important;
        }
        .vc_custom_1469719742753 {
            padding-top: 105px !important;
            padding-bottom: 105px !important;
        }
        .vc_custom_1469626010018 {
            padding-top: 120px !important;
            padding-bottom: 90px !important;
            background-color: #f9f9f9 !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-size: cover !important;
        }
        .vc_custom_1469783534218 {
            padding-top: 80px !important;
            padding-bottom: 115px !important;
        }
        .vc_custom_1469719700585 {
            padding-top: 90px !important;
            padding-bottom: 125px !important;
            background-image: url(images/tech-background-image-2.jpg?id=5075) !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-size: cover !important;
        }
        .vc_custom_1469183244345 {
            padding-top: 85px !important;
            padding-bottom: 50px !important;
            background-color: #ffffff !important;
        }
        .vc_custom_1469719560458 {
            padding-top: 130px !important;
            padding-bottom: 101px !important;
            background-image: url(images/tech-background-image-3.jpg?id=5073) !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-size: cover !important;
        }
        .vc_custom_1469615697840 {
            padding-top: 72px !important;
            padding-bottom: 72px !important;
        }
    </style>
    <noscript>
        <style type="text/css">
            .wpb_animate_when_almost_visible {
                opacity: 1;
            }
        </style>
    </noscript>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <style>
        .fluidvids {
            width: 100%;
            max-width: 100%;
            position: relative;
        }
        .fluidvids-item {
            position: absolute;
            top: 0px;
            left: 0px;
            width: 100%;
            height: 100%;
        }
    </style>
    <!-- Go to www.addthis.com/dashboard to customize your tools -->
    <script type="text/javascript" src="//s7.addthis.com/js/300/addthis_widget.js#pubid=ra-59f8703b23631f3c"></script>
    
</head>
</head>
<body class="page page-id-3487 page-template page-template-full-width page-template-full-width-php qode-core-1.2  qodef-smooth-scroll qodef-smooth-page-transitions qodef-top-bar-mobile-hide qodef-header-standard qodef-sticky-header-on-scroll-up qodef-default-mobile-header qodef-sticky-up-mobile-header qodef-dropdown-animate-height qodef-search-covers-header qodef-side-menu-slide-with-content qodef-width-470 wpb-js-composer js-comp-ver-4.12 vc_responsive">

<section tabindex="0" style="" class="qodef-side-menu right">

        <div class="qodef-close-side-menu-holder">

        <div class="qodef-close-side-menu-holder-inner">

            <a href="#" target="_self" class="qodef-close-side-menu">

                <span aria-hidden="true" class="icon_close"></span>

            </a>

        </div>

    </div>

</section>

<div class="qodef-wrapper">

    <div class="qodef-wrapper-inner">

<div class="qodef-top-bar">

<div class="qodef-grid" style="">

                    <div class="qodef-position-left">

                <div class="qodef-position-left-inner">

                                            <div id="nav_menu-2" class="widget widget_nav_menu qodef-top-bar-widget" style="width: 100%;"><div class="menu-top-bar-menu-container"><ul id="menu-top-bar-menu" class="menu" style="width: 100%;">
  
<li id="menu-item-4724" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-4724"><a href="https://www.ommegaonline.org/faq">FAQ's</a></li>

<li id="menu-item-4724" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-4724"><a href="https://www.ommegaonline.org/user-authenticate/register">Register</a></li>

<li id="menu-item-4723" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-4723"><a href="https://www.ommegaonline.org/contact-us">Contact Us</a></li>

<li id="menu-item-4723" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-4723" style="float: right;">
<div class="menu">

                <div class="qodef-position-right-inner">

                                            <div id="text-7" class="widget widget_text qodef-top-bar-widget">           <div class="textwidget"><p style="font-size:13px; color:#b6b6b6; font-weight:600;">Follow Us:</p></div>

        </div><div id="text-8" class="widget widget_text qodef-top-bar-widget">         <div class="textwidget">

    <span class="qodef-icon-shortcode circle" style="margin: 0 5px 0 0;width: 19px;height: 19px;line-height: 19px;background-color: #3b5998;border-style: solid;border-width: 0px" data-color="#363636">

                     <a class="" href="https://www.facebook.com/ommegaonlinepublishers/" target="_blank">

        

        <span aria-hidden="true" class=" fa fa-facebook" style="color: #363636;font-size:15px;margin-top: 3px;"></span>

                    </a>

            </span>









    <span class="qodef-icon-shortcode circle" style="margin: 0 5px 0 0;width: 19px;height: 19px;line-height: 19px;background-color: #55acee;border-style: solid;border-width: 0px" data-color="#363636">

                     <a class="" href="https://twitter.com/OmmegaonlineC" target="_blank">

        

        <span aria-hidden="true" class="fa fa-twitter" style="color: #363636;font-size:15px;margin-top: 3px;"></span>

                    </a>

            </span>













    <span class="qodef-icon-shortcode circle" style="margin: 0 5px 0 0;width: 19px;height: 19px;line-height: 19px;background-color: #b2dd4c;border-style: solid;border-width: 0px" data-color="#363636">

                     <a class="" href="https://www.linkedin.com/company/ommega-publishers?trk=company_name" target="_blank">

        

        <span aria-hidden="true" class="fa fa-linkedin" style="color: #363636;font-size:15px;margin-top: 3px;"></span>

                    </a>

            </span>

<span class="qodef-icon-shortcode circle" style="margin: 0 5px 0 0;width: 19px;height: 19px;line-height: 19px;background-color: #dd954c;border-style: solid;border-width: 0px" data-color="#363636">

                     <a class="" href="https://ommegaonline.org/home/rss" target="_blank">

        

        <span aria-hidden="true" class="fa fa-rss" style="color: #363636;font-size:15px;margin-top: 3px;"></span>

                    </a>

            </span>


</div>

        </div><div id="text-9" class="widget widget_text qodef-top-bar-widget">         <div class="textwidget"><p class="custom-row-color-changer" style="font-size:13px;font-weight:600;line-height: 40px;background: #b2dd4c;padding: 0 17px;color:#fff;"><a href="mailto:helpdesk&#64;ommegaonline.org" style="color: white;">Email us: helpdesk@ommegaonline.org</a></p></div>

        </div>                                    </div>

            <div></div></div>
</li></ul></div></div>                                    </div>

            </div><div class="qodef-vertical-align-containers qodef-50-50">

            

                        

        </div>

        </div>

    </div>







<header class="qodef-page-header">

        <div class="qodef-menu-area">

                    <div class="qodef-grid">

                    <form autocomplete="off" role="search" action="" class="qodef-search-cover" method="get">

        <div class="qodef-container">

        <div class="qodef-container-inner clearfix">

                        <div class="qodef-form-holder-outer">

                <div class="qodef-form-holder">

                    <div class="qodef-form-holder-inner">

                        <input placeholder="Search" name="s" class="qode_search_field" autocomplete="off" type="text">

                        <div class="qodef-search-close">

                            <a href="#">

                                <i class="qodef-icon-ion-icon ion-close "></i>                          </a>

                        </div>

                    </div>

                </div>

            </div>

                    </div>

    </div>

    </form>            <div class="qodef-vertical-align-containers">

                <div class="qodef-position-left">

                    <div class="qodef-position-left-inner">

                        

<div class="qodef-logo-wrapper">

    <a href="https://www.ommegaonline.org/" style="height: 90px;">

        <img class="qodef-normal-logo" style="height: 50px;

padding-top: 20px;" src="https://www.ommegaonline.org/images/logo_ommega.png" alt="logo"></a>

</div>



                    </div>

                </div>

                

                


                <div class="qodef-position-right">

                    <div class="qodef-position-right-inner">

                        

<nav class="qodef-main-menu qodef-drop-down qodef-default-nav">

    <ul id="menu-main-menu" class="clearfix"><li id="nav-menu-item-634" class="menu-item menu-item-type-post_type menu-item-object-page current-menu-ancestor current_page_ancestor menu-item-has-children has_sub wide wide_background"><a href="https://www.ommegaonline.org/" class="  "><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Home</span></span><span class="plus"></span></span></a>



</li>

<li id="nav-menu-item-314" class="menu-item menu-item-type-post_type menu-item-object-page current-menu-ancestor current_page_ancestor menu-item-has-children has_sub wide wide_background"><a href="https://www.ommegaonline.org/about-us" class="current"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">About</span></span><span class="plus"></span></span></a>



</li>

<li id="nav-menu-item-629" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub narrow"><a href="#" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Guidelines</span></span><span class="plus"></span></span></a>

<div style="height: 0px; visibility: hidden; opacity: 0; margin-top: 0px; overflow: hidden;" class="second"><div class="inner"><ul>

    

    <li id="nav-menu-item-812" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children sub"><a href="https://www.ommegaonline.org/guidelines/author-guidelines" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Author Guidelines</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    

</li>

    <li id="nav-menu-item-789" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children sub"><a href="https://www.ommegaonline.org/guidelines/editor-guidelines" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Editor Guidelines</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    

</li>

    <li id="nav-menu-item-758" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="https://www.ommegaonline.org/guidelines/reviewer-guidelines" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Reviewer Guidelines</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    

</li>

</ul></div></div>

</li>

<li id="nav-menu-item-630" class="menu-item menu-item-type-post_type menu-item-object-page current-menu-ancestor current_page_ancestor menu-item-has-children has_sub wide wide_background">



<a href="https://www.ommegaonline.org/submit-manuscript" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="" style="padding: 5px;">Submit Manuscript</span></span><span class="plus"></span></span></a>



</li>



</li>





<li id="nav-menu-item-630" class="menu-item menu-item-type-post_type menu-item-object-page current-menu-ancestor current_page_ancestor menu-item-has-children has_sub wide wide_background">
<a href="https://www.ommegaonline.org/user-authenticate/login" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Login</span></span><span class="plus"></span></span></a>
</li>







<li id="nav-menu-item-632" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub wide icons wide_background"><a href="https://www.ommegaonline.org/journals" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Journals</span></span><span class="plus"></span></span></a>
</li>
<div style="height: 0px; visibility: hidden; opacity: 1; margin-top: 0px; overflow: hidden; left: -1000.62px; width: 100%;" class="second"><div class="inner">



<ul>



    <li style="height: 791px;" id="nav-menu-item-1286" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Medical</span></span><span class="plus"></span><i class=" fa fa-angle-right"></i></span></a>

    <ul>

    
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Gastrointestinal-Disorders-and-Liver-function/31" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Gastrointestinal Disorders and Liver function </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2471-0601</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Investigative-Dermatology-and-Venereology-Research/32" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Investigative Dermatology and Venereology Research </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2381-0858</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Dentistry-and-Oral-Care/30" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Dentistry and Oral Care </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2379-1705</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Gynecology-and-Neonatal-Biology/28" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Gynecology and Neonatal Biology </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2380-5595</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Diabetes-and-Obesity/25" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Diabetes and Obesity </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2376-0494</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Neurology-and-Brain-Disorders/26" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">International Journal of Neurology and Brain Disorders </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2377-1348</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Cancer-and-Oncology-/24" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">International Journal of Cancer and Oncology  </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2377-0902</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Heart-and-Cardiology-/21" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Heart and Cardiology  </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2378-6914</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Pediatrics-and-Palliative-Care/53" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Pediatrics and Palliative Care </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2690-4810</span></a></li>

        
    </ul>

</li>

    <li style="height: 791px;" id="nav-menu-item-1287" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Life Science</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    <ul>

    
        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Stem-Cell-and-Regenerative-Biology/45" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Stem Cell and Regenerative Biology</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2471-0598</span></a></li>

        
        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Hematology-and-Therapy/44" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">International Journal of Hematology and Therapy</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2381-1404</span></a></li>

        
        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Addiction-and-Dependence/41" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Addiction and Dependence</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2471-061X</span></a></li>

        
        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Cellular-Immunology-and-Serum-Biology/34" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Cellular Immunology and Serum Biology</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2471-5891</span></a></li>

        
        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Letters-in-Health-and-Biological-Sciences/46" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Letters in Health and Biological Sciences</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2475-6245</span></a></li>

        
        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Anesthesia-and-Surgery/23" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Anesthesia and Surgery</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2377-1364</span></a></li>

        
        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Food-and-Nutritional-Science-/20" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">International Journal of Food and Nutritional Science </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2377-0619</span></a></li>

        
        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Veterinary-Science-and-Animal-Welfare/56" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Veterinary Science and Animal Welfare</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2690-0939</span></a></li>

        
    </ul>

    

</li>

    <li style="height: 791px;" id="nav-menu-item-1288" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Engineering</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    <ul>

    
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Bioinformatics--Proteomics-and-Imaging-Analysis/33" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-space-shuttle"></i></span><span class="item_text">Journal of Bioinformatics, Proteomics and Imaging Analysis
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2381-0793</span></a></li>

        
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Nanotechnology-and-Materials-Science/22" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-space-shuttle"></i></span><span class="item_text">Journal of Nanotechnology and Materials Science
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2377-1372</span></a></li>

        
       

    </ul>

<a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Biochemistry</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>    <ul>

    
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Analytical--Bioanalytical-and-Separation-Techniques/58" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-flask"></i></span><span class="item_text">Journal of Analytical, Bioanalytical and Separation Techniques
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2476-1869</span></a></li>

        




       

    </ul>



</li>





    <li style="height: 791px;" id="nav-menu-item-1288" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Pharma</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    <ul>

    


        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Pharmacy-and-Pharmaceutics/27" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-medkit"></i></span><span class="item_text">Journal of Pharmacy and Pharmaceutics
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2576-3091</span></a></li>

        


        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Medicinal-Chemistry-and-Toxicology-/51" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-medkit"></i></span><span class="item_text">Journal of Medicinal Chemistry and Toxicology 
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2575-808X</span></a></li>

        
       

    </ul>

<a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Environment</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>    <ul>

    
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Marine-Biology-and-Aquaculture/29" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-envira"></i></span><span class="item_text">Journal of Marine Biology and Aquaculture
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2381-0750</span></a></li>

        
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Environment-and-Health-Science-/19" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-envira"></i></span><span class="item_text">Journal of Environment and Health Science 
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2378-6841</span></a></li>

        
       

    </ul>



</li>







    

    

    



</ul>



</div></div>





</ul></nav>



                                                            

        

        

                    



                                                </div>

                </div>

            </div>

                </div>

            </div>

        

<div class="qodef-sticky-header">

    <form autocomplete="off" role="search" action="#" class="qodef-search-cover" method="get">

        <div class="qodef-container">

        <div class="qodef-container-inner clearfix">

                        <div class="qodef-form-holder-outer">

                <div class="qodef-form-holder">

                    <div class="qodef-form-holder-inner">

                        <input placeholder="Search" name="s" class="qode_search_field" autocomplete="off" type="text">

                        <div class="qodef-search-close">

                            <a href="#">

                                <i class="qodef-icon-ion-icon ion-close "></i>                          </a>

                        </div>

                    </div>

                </div>

            </div>

                    </div>

    </div>

    </form>    <div class="qodef-sticky-holder">

            <div class="qodef-grid">

                        <div class="qodef-vertical-align-containers">

                <div class="qodef-position-left">

                    <div class="qodef-position-left-inner">

                        

<div class="qodef-logo-wrapper">

    <a href="https://www.ommegaonline.org/" style="height: 50px;">

        <img class="qodef-normal-logo" style="" src="https://www.ommegaonline.org/images/logo_ommega.png" alt="logo"></a>

</div>



                    </div>

                </div>

                <div class="qodef-position-right">

                    <div class="qodef-position-right-inner">

                        

<nav class="qodef-main-menu qodef-drop-down qodef-default-nav">

    <ul id="menu-main-menu" class="clearfix"><li id="nav-menu-item-634" class="menu-item menu-item-type-post_type menu-item-object-page current-menu-ancestor current_page_ancestor menu-item-has-children qodef-active-item has_sub wide wide_background"><a href="https://www.ommegaonline.org/" class=" current "><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Home</span></span><span class="plus"></span></span></a>



</li>

<li id="nav-menu-item-314" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub narrow"><a href="https://www.ommegaonline.org/about-us" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">About</span></span><span class="plus"></span></span></a>



</li>

<li id="nav-menu-item-629" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub narrow"><a href="#" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Guidelines</span></span><span class="plus"></span></span></a>

<div style="height: 0px; visibility: hidden; opacity: 0; margin-top: 0px; overflow: hidden;" class="second"><div class="inner"><ul>

    

    <li id="nav-menu-item-812" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children sub"><a href="https://www.ommegaonline.org/guidelines/author-guidelines" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Author Guidelines</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    

</li>

    <li id="nav-menu-item-789" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children sub"><a href="https://www.ommegaonline.org/guidelines/editor-guidelines" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Editor Guidelines</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    

</li>

    <li id="nav-menu-item-758" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="https://www.ommegaonline.org/guidelines/reviewer-guidelines" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Reviewer Guidelines</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    

</li>

</ul></div></div>

</li>

<li id="nav-menu-item-630" class="menu-item menu-item-type-post_type menu-item-object-page current-menu-ancestor current_page_ancestor menu-item-has-children has_sub wide wide_background"><a href="https://www.ommegaonline.org/user-authenticate/login" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="" style="padding: 5px;">Submit Manuscript</span></span><span class="plus"></span></span></a>



</li>

<li id="nav-menu-item-630" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub narrow"><a href="https://www.ommegaonline.org/user-authenticate/login" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">LOGIN</span></span><span class="plus"></span></span></a>



</li>


<li id="nav-menu-item-632" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub wide icons wide_background"><a href="https://www.ommegaonline.org/journals" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Journals</span></span><span class="plus"></span></span></a>
</li>
<div style="height: 0px; visibility: hidden; opacity: 1; margin-top: 0px; overflow: hidden; left: -1000.62px; width: 100%;" class="second"><div class="inner"><ul>

    <li style="height: 791px;" id="nav-menu-item-1286" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Medical</span></span><span class="plus"></span><i class=" fa fa-angle-right"></i></span></a>

    <ul>

    
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Gastrointestinal-Disorders-and-Liver-function/31" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Gastrointestinal Disorders and Liver function </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2471-0601</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Investigative-Dermatology-and-Venereology-Research/32" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Investigative Dermatology and Venereology Research </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2381-0858</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Dentistry-and-Oral-Care/30" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Dentistry and Oral Care </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2379-1705</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Gynecology-and-Neonatal-Biology/28" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Gynecology and Neonatal Biology </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2380-5595</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Diabetes-and-Obesity/25" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Diabetes and Obesity </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2376-0494</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Neurology-and-Brain-Disorders/26" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">International Journal of Neurology and Brain Disorders </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2377-1348</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Cancer-and-Oncology-/24" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">International Journal of Cancer and Oncology  </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2377-0902</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Heart-and-Cardiology-/21" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Heart and Cardiology  </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2378-6914</span></a></li>

        
        <li id="nav-menu-item-1822" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Pediatrics-and-Palliative-Care/53" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-stethoscope"></i></span><span class="item_text">Journal of Pediatrics and Palliative Care </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">ISSN:2690-4810</span></a></li>

        
    </ul>

</li>

    <li style="height: 791px;" id="nav-menu-item-1287" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Life Science</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    <ul>

    


        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Stem-Cell-and-Regenerative-Biology/45" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Stem Cell and Regenerative Biology</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2471-0598</span></a></li>

        


        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Hematology-and-Therapy/44" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">International Journal of Hematology and Therapy</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2381-1404</span></a></li>

        


        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Addiction-and-Dependence/41" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Addiction and Dependence</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2471-061X</span></a></li>

        


        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Cellular-Immunology-and-Serum-Biology/34" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Cellular Immunology and Serum Biology</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2471-5891</span></a></li>

        


        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Letters-in-Health-and-Biological-Sciences/46" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Letters in Health and Biological Sciences</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2475-6245</span></a></li>

        


        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Anesthesia-and-Surgery/23" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Anesthesia and Surgery</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2377-1364</span></a></li>

        


        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Food-and-Nutritional-Science-/20" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">International Journal of Food and Nutritional Science </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2377-0619</span></a></li>

        


        <li id="nav-menu-item-1292" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Veterinary-Science-and-Animal-Welfare/56" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-heartbeat"></i></span><span class="item_text">Journal of Veterinary Science and Animal Welfare</span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

        ISSN:2690-0939</span></a></li>

        
    </ul>

    

</li>

    <li style="height: 791px;" id="nav-menu-item-1288" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Engineering</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    <ul>

    
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Bioinformatics--Proteomics-and-Imaging-Analysis/33" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-space-shuttle"></i></span><span class="item_text">Journal of Bioinformatics, Proteomics and Imaging Analysis
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2381-0793</span></a></li>

        
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Nanotechnology-and-Materials-Science/22" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-space-shuttle"></i></span><span class="item_text">Journal of Nanotechnology and Materials Science
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2377-1372</span></a></li>

        
       

    </ul>

<a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Biochemistry</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>    <ul>

    
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Analytical--Bioanalytical-and-Separation-Techniques/58" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-flask"></i></span><span class="item_text">Journal of Analytical, Bioanalytical and Separation Techniques
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2476-1869</span></a></li>

        
       

    </ul>



</li>





    <li style="height: 791px;" id="nav-menu-item-1288" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children sub"><a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Pharma</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>

    <ul>

    
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Pharmacy-and-Pharmaceutics/27" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-medkit"></i></span><span class="item_text">Journal of Pharmacy and Pharmaceutics
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

            ISSN:2576-3091
            </span></a></li>

        
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Medicinal-Chemistry-and-Toxicology-/51" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-medkit"></i></span><span class="item_text">Journal of Medicinal Chemistry and Toxicology 
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

            ISSN:2575-808X
            </span></a></li>

        
       

    </ul>

<a href="#" class=" no_link" style="cursor: default;" onclick="JavaScript: return false;"><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="menu_icon null fa"></i></span><span class="item_text">Environment</span></span><span class="plus"></span><i class="q_menu_arrow fa fa-angle-right"></i></span></a>    <ul>

    
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Marine-Biology-and-Aquaculture/29" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-envira"></i></span><span class="item_text">Journal of Marine Biology and Aquaculture
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2381-0750</span></a></li>

        
        <li id="nav-menu-item-1586" class="menu-item menu-item-type-post_type menu-item-object-page "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Environment-and-Health-Science-/19" class=""><span class="item_outer"><span class="item_inner"><span class="menu_icon_wrapper"><i class="fa fa-envira"></i></span><span class="item_text">Journal of Environment and Health Science 
        </span></span><span class="plus"></span></span><span class=" qodef-featured-icon text " aria-hidden="true">

         ISSN:2378-6841</span></a></li>

        
       

    </ul>



</li>

    

    

    



    

</ul></div></div>

</li>

</ul></nav>



                                                            

        

        

                    



                                                </div>

                </div>

            </div>

                    </div>

            </div>

</div>


</header>





<header style="margin-bottom: 0px;" class="qodef-mobile-header qodef-animate-mobile-header mobile-header-appear">

    <div class="qodef-mobile-header-inner">

                <div class="qodef-mobile-header-holder">

            <div class="qodef-grid">

                <div class="qodef-vertical-align-containers">

                                            <div class="qodef-mobile-menu-opener">

                            <a href="javascript:void(0)">

                    <span class="qodef-mobile-opener-icon-holder">

                        <i class="qodef-icon-font-awesome fa fa-bars "></i>                    </span>

                            </a>

                        </div>

                                                                <div class="qodef-position-center">

                            <div class="qodef-position-center-inner">

                                

<div class="qodef-mobile-logo-wrapper">

    <a href="https://www.ommegaonline.org/" >

        <img src="https://www.ommegaonline.org/images/logo_ommega.png" alt="mobile-logo">

    </a>

</div>



                            </div>

                        </div>

                                        <div class="qodef-position-right">

                        <div class="qodef-position-right-inner">

                                                    </div>

                    </div>

                </div> <!-- close .qodef-vertical-align-containers -->

            </div>

        </div>

        

<nav class="qodef-mobile-nav">

    <div class="qodef-grid">

        <ul id="menu-main-menu-1" class="">



        <li id="mobile-menu-item-634" class="menu-item menu-item-type-post_type menu-item-object-page current-menu-ancestor current_page_ancestor menu-item-has-children qodef-active-item has_sub"><a href="https://www.ommegaonline.org/" class=" current "><span>Home</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

        </li>



<li id="mobile-menu-item-314" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="https://www.ommegaonline.org/about-us" class=""><span>About Us</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

</li>

<li id="mobile-menu-item-629" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="#" class=""><span>Guidelines</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>



<ul class="sub_menu">

<li id="mobile-menu-item-839" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children  has_sub"><a href="https://www.ommegaonline.org/guidelines/author-guidelines" class=""><span>Author Guidelines</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

    </li>

<li id="mobile-menu-item-812" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children  has_sub"><a href="https://www.ommegaonline.org/guidelines/editor-guidelines" class=""><span>Editor Guidelines</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

</li>

 <li id="mobile-menu-item-812" class="menu-item menu-item-type-post_type menu-item-object-page menu-item-has-children  has_sub"><a href="https://www.ommegaonline.org/guidelines/reviewer-guidelines" class=""><span>Reviewer Guidelines</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

</li>

</ul>



</li>



<li id="mobile-menu-item-314" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="https://www.ommegaonline.org/user-authenticate/login" class=""><span>Submit Manuscript</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

</li>

<li id="mobile-menu-item-314" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub">

<a href="https://www.ommegaonline.org/user-authenticate/login" class=""><span>Login</span></a>


<span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

</li>





<li id="mobile-menu-item-630" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="#" class=""><span>Journals</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

<ul class="sub_menu">

    

    

    <li id="mobile-menu-item-936" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="#" class=""><span>Medical</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

    <ul class="sub_menu">

    
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Gastrointestinal-Disorders-and-Liver-function/31" class=""><span>Journal of Gastrointestinal Disorders and Liver function</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Investigative-Dermatology-and-Venereology-Research/32" class=""><span>Investigative Dermatology and Venereology Research</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Dentistry-and-Oral-Care/30" class=""><span>Journal of Dentistry and Oral Care</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Gynecology-and-Neonatal-Biology/28" class=""><span>Journal of Gynecology and Neonatal Biology</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Diabetes-and-Obesity/25" class=""><span>Journal of Diabetes and Obesity</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Neurology-and-Brain-Disorders/26" class=""><span>International Journal of Neurology and Brain Disorders</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Cancer-and-Oncology-/24" class=""><span>International Journal of Cancer and Oncology </span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Heart-and-Cardiology-/21" class=""><span>Journal of Heart and Cardiology </span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Pediatrics-and-Palliative-Care/53" class=""><span>Journal of Pediatrics and Palliative Care</span></a></li>

       
    </ul>



</li>



 <li id="mobile-menu-item-936" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="#" class=""><span>Life Science</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

    <ul class="sub_menu">

    
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Stem-Cell-and-Regenerative-Biology/45" class=""><span>Journal of Stem Cell and Regenerative Biology</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Hematology-and-Therapy/44" class=""><span>International Journal of Hematology and Therapy</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Addiction-and-Dependence/41" class=""><span>Journal of Addiction and Dependence</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Cellular-Immunology-and-Serum-Biology/34" class=""><span>Journal of Cellular Immunology and Serum Biology</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Letters-in-Health-and-Biological-Sciences/46" class=""><span>Letters in Health and Biological Sciences</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Anesthesia-and-Surgery/23" class=""><span>Journal of Anesthesia and Surgery</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/International-Journal-of-Food-and-Nutritional-Science-/20" class=""><span>International Journal of Food and Nutritional Science </span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Veterinary-Science-and-Animal-Welfare/56" class=""><span>Journal of Veterinary Science and Animal Welfare</span></a></li>

       
    </ul>



</li>



<li id="mobile-menu-item-936" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="#" class=""><span>Engineering</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

    <ul class="sub_menu">

    
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Bioinformatics--Proteomics-and-Imaging-Analysis/33" class=""><span>Journal of Bioinformatics, Proteomics and Imaging Analysis</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Nanotechnology-and-Materials-Science/22" class=""><span>Journal of Nanotechnology and Materials Science</span></a></li>

       
    </ul>



</li>



<li id="mobile-menu-item-936" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="#" class=""><span>Biochemistry</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

    <ul class="sub_menu">

    
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Analytical--Bioanalytical-and-Separation-Techniques/58" class=""><span>Journal of Analytical, Bioanalytical and Separation Techniques</span></a></li>

       
    </ul>



</li>



<li id="mobile-menu-item-936" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="#" class=""><span>Pharma</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

    <ul class="sub_menu">

    
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Pharmacy-and-Pharmaceutics/27" class=""><span>Journal of Pharmacy and Pharmaceutics</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Medicinal-Chemistry-and-Toxicology-/51" class=""><span>Journal of Medicinal Chemistry and Toxicology </span></a></li>

       
    </ul>



</li>



<li id="mobile-menu-item-936" class="menu-item menu-item-type-custom menu-item-object-custom menu-item-has-children  has_sub"><a href="#" class=""><span>Environment</span></a><span class="mobile_arrow"><i class="qodef-sub-arrow fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>

    <ul class="sub_menu">

    
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Marine-Biology-and-Aquaculture/29" class=""><span>Journal of Marine Biology and Aquaculture</span></a></li>

       
        <li id="mobile-menu-item-942" class="menu-item menu-item-type-post_type menu-item-object-post "><a href="https://www.ommegaonline.org/journal-details/Journal-of-Environment-and-Health-Science-/19" class=""><span>Journal of Environment and Health Science </span></a></li>

       
    </ul>



</li>





</ul>

</li>





</ul>   

 </div>

</nav>



    </div>

</header>
            
            <div class="hide-mobile">
                <img src="https://www.ommegaonline.org/images/spaja_header.jpg" style=" width: auto;     height: 170px;">
            </div>
            <div class="qodef-container-inner">
                <div class="qodef-two-columns-75-25 qodef-content-has-sidebar  clearfix">
                    <div class="qodef-column1 qodef-content-left-from-sidebar">
                        <div class="qodef-column-inner">
                            <!--  <table class="badge-bar">
                    <tr>
                      <td class="articleInfoLink">
                            <a href="#" role="button" tabindex="0" onclick="return articleInfoToggle();">Article information&nbsp;<span id="authorInfoArrow" class="arrow-down indicator"><img src="https://maxcdn.icons8.com/Share/icon/Arrows//expand21600.png" style="width: 10px;height: 10px"></span>
                            </a>
                        </td>
                    <tr>
                </table> -->
                            <div style="position: relative;" class="qodef-blog-holder qodef-blog-type-masonry qodef-masonry-pagination-infinite-scroll">
                                <div class="qodef-blog-masonry-grid-sizer">
                                </div>
                                <div class="qodef-blog-masonry-grid-gutter">
                                </div>
                                <div>
                                </div>
                                <article style="width: 100%;float: left;" id="post-1545" class="post-1545 post type-post status-publish format-link has-post-thumbnail hentry category-ideas category-trends tag-creative tag-design tag-digital post_format-post-format-link">
                                    <div class="qodef-post-content content-holder">
                                        <div class="qodef-post-text ">
                                            <!-- it is remove by ashok only for border <div class="qodef-post-text-inner"> -->
                                            <div>
                                                <div class="article_info_block1">
                                                    <p>
                                                    </p>
                                                </div>
                                                <div class="qodef-post-info">
                                                    <div class="">Editorial                                                    </div>
                                                    <div class="">Publish Date : 2014-12-28                                                    </div>
                                                </div>
                                                <div class="qodef-post-info">
                                                    <div class="">Journal of Nanotechnology and Materials Science                                                    </div>
                                                                                                    </div>
                                                   
                                                <div>
                                                    <h2>View point of Nanotechnology and Material Science </h2>
                                                </div>
                                                <span class="qodef-quote-author" style="font-size: 16px;">Kenji  Uchino  </span>
                                                <br>
                                                                                   
                                                <div class="qodef-post-mark">
                                                    <span class="fa fa-quote-right quote_mark">
                            </span>
                                                </div>
                                                <div class="qodef-blog-standard-post-date">
                                                </div>
                                                <div class="qodef-blog-standard-info-holder">
                                                    <div class="qodef-post-title">
                                     
                                                        <!--   <h4 style="font-size: 25px;">
                                                                                      Intra-Abdominal (Mesenteric) Desmoid Tumors (Dts) after Kidney Transplantation: A Case Report
                                                                                      </h4> -->
                                                    </div>
                                                    <a href="#" role="button" tabindex="0" onclick="return articleInfoToggle();">Article information&nbsp;
                              <span id="authorInfoArrow" class="arrow-down indicator">
                                <img src="https://maxcdn.icons8.com/Share/icon/Arrows//expand21600.png" style="width: 10px;height: 10px">
                              </span>            </a>
                                                    <!-- 
                                                                                <div class="editor_info_head_rt_media" style="width:100%; clear:both;">
                                                                                    <a style="border: solid 1px #e7e7e7;">
                                          2017-05-22
                                          <span>Recieved Date</span></a>
                                                                                    <a style="border: solid 1px #e7e7e7;">
                                          2017-06-12
                                          <span>Accepted Date</span></a>
                                                                                    <a style="border: solid 1px #e7e7e7;">
                                          2017-06-19
                                          <span>Publication Date</span></a>
                            <a style="border: solid 1px #e7e7e7;" target="_blank" href="https://doi.org/10.15436/2471-0601.17.1545">10.15436/2471-0601.17.1545
                            <span>DOI</span></a>
                            <span class="clear">&nbsp;</span> </div>
                            -->
                                                     <div class="article_info_content" id="articleInfo">
                                                                                                            <div class="article_info_block1" id="affiliationn" style="display: block;">
                                                            <h2>Affiliation</h2>
                                                            <p>
                                                               <p>Electrical Engineering, International Center for Actuators and Transducers, The Pennsylvania State University, USA</p>                                                            </p>
                                                        </div>
                                                                                                                                                                        <div class="article_info_block1">
                                                            <h2>Corresponding Author</h2>
                                                            <p>
                                                              <p class="p1" style="margin: 0in 0in 0.0001pt; text-align: justify;">Uchino, k. International Ctr. for Actuators &amp; Transducers, The Pennsylvania State &Acirc;&nbsp;&Acirc;&nbsp;University, University Park, PA 16802, USA. E-mail: <a href="mailto:kenjiuchino@psu.edu">kenjiuchino@psu.edu</a></p>                                                            </p>
                                                        </div>
                                                                                                                                                                        <div class="article_info_block1">
                                                            <h2>Citation</h2>
                                                            <p>
                                                            
                                                                <p>Uchino, k. Viewpoint of Nanotechnology and Material Science. (2014) J Nanotech Mater Sci 1(1): 1-2.</p>                                                            
                                                            </p>
                                                        </div>
                                                                                                                <div class="article_info_block1">
                                                            <h2>Copy rights</h2>
                                                            <p>
                                                                 <p>
                                                                <p>&copy; 2014 Uchino, K. This is an Open access article distributed under the terms of Creative Commons Attribution 4.0 International License.</p>                                                                </p>
                                                            </p>
                                                        </div>
                                                                                                                <div class="article_info_block1">
                                                            <h2>Keywords</h2>
                                                            <p>Materials-Science; Rescue Technology                                                            </p>
                                                        </div>
                                                                                                            </div>
                                                    <div class="article_info_content">
                                                                                                                 
                                                       <div class="article_info_block1">
                                                                                                                   <h5 id="intro">Introduction</h5>
                                                                                                                        <div id="fulltext" name="fulltext">
                                                                <div id="intro">
                                                                <p class="mb15" style="text-align: justify;">&emsp;&emsp;"Journal of Nanotechnology and Material Science" is an open access, peer reviewed journal with a sole intention of promulgation of research articles throughout the globe. Open access model provides the scientists and researchers a platform to share their innovations, discoveries and findings thus removing all the barriers that were imposed in traditional publishing models.</p>
<p class="mb15" style="text-align: justify;">&emsp;&emsp;I am delighted to write an editorial message for this new edition as one of the journal's Editorial Board Members. This edition is an omnibus of various areas, 1) Indium-free amorphous oxide semiconductor, 2) Carbon nano tubes, 3) Oxide ferroelectrics, and 4) Virosome of unilamellar phospholipid membrane. Using this opportunity, Iwould like to discuss the necessary strategies, which the materials research engineers need to keep in their minds in these decades, which are already exemplified in this issue. Though you might have already read my previous articles<sup>[1-3]</sup>, I dare to repeat my opinion for wider materials-science readers from a different angle.</p>
<p class="mb15" style="text-align: justify;">&emsp;&emsp;I have been a so-called "Navy Ambassador to Japan" (officially Associate Director at Asia Office of the US Office of Naval Research) in these four years until July this year. I had chances in deep involvement in setting multipleinternational R&amp;D related agreements between the US Department of Defense and Japanese governmental institutes, including the rescue technology projects relating with the Big Earthquake and consequent Fukushima Daiichi Nuclear Power Plant melt-down in 2011.</p>
<p class="mb15" style="text-align: justify;">&emsp;&emsp;During these diplomatic work tasks, I confirmed the urgent necessity of politically initiated technology development. Historically, the Japanese government set the four-Chinese-character slogan for encouraging the researchers along a particular direction. "(heavier, thicker, longer, and larger)" was the first one in 1960s, aiming at the infrastructure recovery from the WW-II ruins. A completely opposite slogan, "(lighter, thinner, shorter, and smaller)", started in 1980s, for strengthening the country economic power. I started my compact piezoelectric actuators for micromechatronic applications in the late 1970s under this trend.</p>
<p class="mb15" style="text-align: justify;">&emsp;&emsp;I would like to propose a new four-Chinese-character keyword for the new 21<sup>st</sup> century era, "cooperation, protection, reduction, and continuation". International cooperationand global collaboration in standardization of internet systems became essential to accelerate the mutual communication. The US-Japan Agreement in the "Rescue Robot" development for crisis occasions is one of the urgent tasks which I was involved. The Kyoto Protocol in December 1997 was a trigger to more wide international agreements linked to the United Nations Framework Convention on Climate Change in order to reduce greenhouse gas emission. This is a symbolic global regime for determining the materials' research direction in the 21<sup>st</sup> century. Accordingly, I am proud to announce that my invention "multilayer piezoelectric actuator" became one of the key technologies for reducing NO<sub>x</sub> or SO<sub>x</sub> in recent diesel engine automobiles.</p>
<p class="mb15" style="text-align: justify;">&emsp;&emsp;Protection of the territory and environment from the enemy or natural disaster, and of infectious disease spreadis mandatory. In addition to terrorist attacks, HID, Bird Flu and in particular EBOLA are now the worldwide headache. How can our materials be applied for these aims. Bio materials or medicine development is highly required. Reduction of toxic materials such as lead, heavy metals, dioxin, and of the use of resources and energy consumption is also the key, and the society continuation (i.e., status quo or Sustainable Society) is important to promote. Even in my research area, the long-term material champion, PZT, may be regulated in several years by RoHS (Restriction of Hazardous Substances Directive) due to Pb (lead) inclusion. I recognize various toxic compounds such as Indium Gallium Arsenideeven in semiconductor materials. Thus, the current material researchers needto seek alternative materials(environmentally friendly materials) for replacing toxic ones. Bio/medical materials such as hormones are important to develop, but their disposal way should also be seriouslyconsidered not to harm the environment. The material related with renewable energy generation is also the "must" for reducing nuclear power plants.</p>
<p class="mb15" style="text-align: justify;">&emsp;&emsp;As a concluding remark, Uchino's recommendation is to learn global and domestic regimes/political strategies for 10 years ahead, and to reflect the materials development according to this direction.</p>
<p>&nbsp;</p>
<h5 id="REFERENCES">References</h5>
<p>&nbsp;</p>
<div class="ol">
<ol>
<li style="text-align: justify;">1. <a href="http://symbiosisonlinepublishing.com/materialsscience-engineering/materialsscience-engineering04.php" target="_blank" rel="noopener">Uchino, K. "Politico-Engineering&minus;Politically-Initiated Engineering in Piezoelectric Devices". (2013) SOJ Materials Science &amp; Engineering 1(1): 10.</a></li>
<li>2. <a href="http://www.actuator.de/UserFiles/File/ACTUATOR_14/shorties/A1_0.pdf" target="_blank" rel="noopener">Uchino, K. Piezoelectric Actuator Renaissance. Proc. 14th Int'l Conf. (2014) New Actuators, Bremen, Germany p: 37.</a></li>
<li>3. <a href="http://www.degruyter.com/view/j/ehs.2014.1.issue-1-2/ehs-2013-0021/ehs-2013-0021.xml" target="_blank" rel="noopener">Uchino, K. "Piezoelectric Actuator Renaissance". (2014) J Energy Harvesting and Systems 1(1-2): 45&ndash;56.</a></li>
</ol>
</div>    
                                                                   </div>
                                                            </div>
                                                        </div>
                                                        
                                                        
                                                        
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </article>
                            </div>
                        </div>
                    </div>
                    <div class="container" style="width: 250px;float: left;margin-right: 20px;">
                        <div id="sticky-anchor">
                        </div>
                        <div id="sidebar-1" class="sidebar" style="position: fixed;margin-top: -480px;">
                            <div class="qodef-column2" style="width: 100%;">
                                <div class="qodef-column2" style="width: 100%;">
                                    <div class="qodef-column-inner">
                                        <aside class="qodef-sidebar">
                                            <div class="index_main_rt side_bar_inner side_bar_inner2">
                                                <div class="article_details_sidebar" style="margin-top:192px">
                                                    <div class="article_page_viewblock">
                                                        <div class="qodef-item-text-holder">
                                                            <table border="0">
                                                                <tr>
                                                                    
                                                                    <td>
                                                                        <span id="downloads" style="font-size: 20px;      line-height: 20px;     color: #000;     font-weight: 700;     display: block;">                    
                                        37                                      </span>
                                                                        <input type="hidden" name="" id="pagelike" value="1"> </td>
                                                                    
                                                                    <td>
                                                                       <a target="_blank" href="https://www.ommegaonline.org/download.php?download_file=articles/publishimages/14999-Viewpoint-of-Nanotechnology-and-Material-Science.pdf" onclick="save_download(37,63)"> <img class="pdfimg" align="center" src="https://www.ommegaonline.org/images/pdf.png" height="50" width="50"></a>
                                                                    </td>
                                                                    <td>
                                                                       <a target="_blank" href="https://www.ommegaonline.org/download.php?download_file=admin/journalassistance/publishimages/864_JNMS-e001.bib" onclick="save_download(37,63)"> <img class="pdfimg" src="https://www.ommegaonline.org/images/text.png" height="50" width="45"></a>
                                                                    </td>
                                                                <td>
                                                                        <a target="_blank" href="https://www.ommegaonline.org/home/articlexml/63" onclick="save_download(37,63)"><img class="pdfimg" src="https://www.ommegaonline.org/images/xml.png" height="50" width="49"></a>
                                                                    </td>
                                                                </tr>
                                                                <tr>
                                                                    <td width="100" style="text-align: left;">
                                                                        <style type="text/css">
                                                                            #articleInfo {
                                                                                display: none;
                                                                                border-bottom: 1px solid #CCCCCC;
                                                                                font-size: 14px;
                                                                                color: #333333;
                                                                                padding-bottom: 15px;
                                                                            }
                                                                            #articleInfo b {
                                                                                font-weight: normal;
                                                                            }
                                                                            #articleInfo .copyRight {
                                                                                margin-bottom: 20px;
                                                                                margin-top: 20px;
                                                                            }
                                                                            .articleInfoBadge,
                                                                            .pdfBadge {
                                                                                text-align: center;
                                                                            }
                                                                            .articleInfoBadge img,
                                                                            .pdfBadge img {
                                                                                display: block;
                                                                                margin-left: auto;
                                                                                margin-right: auto;
                                                                            }
                                                                        </style>
                                                                        <script>
                                                                            function articleInfoToggle() {
                                                                                var articleInfoID = document.getElementById('articleInfo');
                                                                                if (articleInfoID.style.display === 'none' || articleInfoID.style.display === '') {
                                                                                    articleInfoID.style.display = 'block';
                                                                                    document.getElementById("authorInfoArrow").className = "arrow-up indicator";
                                                                                } else {
                                                                                    articleInfoID.style.display = 'none';
                                                                                    document.getElementById("authorInfoArrow").className = "arrow-down indicator";
                                                                                }
                                                                                return false;
                                                                            }

                                                                            function articleInfoToggleMobile() {
                                                                                var articleInfoID = document.getElementById('articleInfo');
                                                                                if (articleInfoID.style.display === 'none' || articleInfoID.style.display === '') {
                                                                                    articleInfoID.style.display = 'block';
                                                                                    document.getElementById("authorInfoImage").src = "/pb-assets/Icons/Cross-blue-grey.png";
                                                                                } else {
                                                                                    articleInfoID.style.display = 'none';
                                                                                    document.getElementById("authorInfoImage").src = "/pb-assets/Icons/author-info.png";
                                                                                }
                                                                            }
                                                                        </script>
                                                                        <span style="text-align: right;font-size:25px">Total
                                        <br>Download
                                      </span> </td>
                                                                    <td style="text-align: center; padding:5px;font-size: 12px">
                                                                        <a target="_blank" href="https://www.ommegaonline.org/download.php?download_file=articles/publishimages/14999-Viewpoint-of-Nanotechnology-and-Material-Science.pdf" onclick="save_download(37,63)">PDF</a>
                                                                    </td>
                                                                    <td  style="text-align: center;padding:5px;font-size: 12px">
                                                                        <a target="_blank" href="https://www.ommegaonline.org/download.php?download_file=admin/journalassistance/publishimages/864_JNMS-e001.bib" onclick="save_download(37,63)">CITATION</a>
                                                                    </td>
                                                                    <td  style="text-align: center;padding:5px;font-size: 12px">
                                                                        <a target="_blank" href="https://www.ommegaonline.org/home/articlexml/63" onclick="save_download(37,63)">XML</a>
                                                                    </td>
                                                                </tr>
                                                            </table>
                                                        </div>
                                            
                                                        <span class="clear">&nbsp;
                              </span>
                                                        </p>
                                                        <span class="clear">&nbsp;
                              </span>
                                                    </div>
                                                    <div class="article_share_info">
                                                        <p>
                                                            <a style="color:#b1b1b1;" onclick="save_like('64','63')">
                                                                
                                                            <span>   <span id="likeval">                    
                                    64                                  </span></span>  </a>Likes
                                  </p>
                                                     
                                                        <p>
                                                            <span>3993                                </span>Views
                                                        </p>
                                                       <!-- <p>
                                                            <span>0                                </span>Cited-by
                                                        </p>-->
                                                        <span class="clear">&nbsp;
                              </span>
                                                    </div>
                                                    <div class="article_sharing_block">
                                                        <p>Share this page to
                                                        </p>
                                                        <!-- Go to www.addthis.com/dashboard to customize your tools -->
                                                        <div class="addthis_inline_share_toolbox">
                                                        </div>
                                                        <span class="clear">&nbsp;
                              </span>
                                                    </div>
                                                    <div id="fbcount">
                                                    </div>
                                                </div>
                                                <div class="article_sidebar_nav affix-top" data-spy="affix" data-offset-top="197">
                                                    <ul>
                                                        <li>
                                                            <a class="active" href="#ABSTRACT">Abstract</a>
                                                        </li>
                                                        <li>
                                                            <a href="#intro">Introduction</a>
                                                        </li>
                                                        <li>
                                                            <a href="#METHODS">Methods</a>
                                                        </li>
                                                        <li>
                                                            <a href="#DISCUSSION">Discussion</a>
                                                        </li>
                                                        <li>
                                                            <a href="#CONCLUSION">Conclusion</a>
                                                        </li>
                                                        <li>
                                                            <a href="#REFERENCES">References</a>
                                                        </li>
                                                    </ul>
                                                </div>
                                                <!--<div class="article_share_info">
                                                    <div id="recent-posts-2" class="widget qodef-footer-column-2 widget_recent_entries">
                                                        <h4 class="qodef-footer-widget-title">Recent Articles</h4>
                                                        <ul>
                                                            <li>
                                                                <a href="">Breast Cancer Stem Cells  Understanding and Opportunities for Therapeutics</a>
                                                            </li>
                                                            <li>
                                                                <a href="">Subcostal Transversus Abdominis Plane  </a>
                                                            </li>
                                                        </ul>
                                                    </div>
                                                    <span class="clear">&nbsp;
                            </span>
                                                </div>-->
                                            </div>
                                        </aside>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    </div>
    </div>
    </div>
    </div>
    <div id="footer">
        <div class="vc_row wpb_row vc_row-fluid qodef-section vc_custom_1446024295969 qodef-content-aligment-left" style="margin-top: 50px;">
            <div class="clearfix qodef-full-section-inner">
                <div class="wpb_column vc_column_container vc_col-sm-12">
                    <div class="vc_column-inner ">
                        <div class="wpb_wrapper">
                            <div class="qodef-carousel-holder with_navigation clearfix">
                                <div class="qodef-carousel" data-items="6" data-navigation="yes">
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/crossref.png" alt="crossref">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/doaj.png" alt="DOAJ">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/GIF.png" alt="Global Impact Factor">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/google_scholar.png" alt="google scholar">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/icmjenew.png" alt="ICMJ">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/index_copernicus.png" alt="Index copernicus">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/isinew.png" alt="ISI">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/j-gate.png" alt="J gate">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/worldcat.png" alt="World cat">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                        
                        <img src="https://www.ommegaonline.org/images/TOCs.png" alt="TOCs">                    
                      </span>
                                    </div>
                                    <div class="qodef-carousel-item-holder">
                                        <span class="qodef-carousel-first-image-holder  qodef-image-zoom">                                                
                        <img src="https://www.scilit.net/images/scilitLogo_black.png" width="200" alt="Scilit logo" />                                            
                      </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    </div>
    </div>
    <!-- close div.content_inner -->
    </div>
    <!-- close div.content -->
    </div>
    <!-- close div.qodef-wrapper-inner  -->
    </div>
    <!-- close div.qodef-wrapper -->
    
    <script type='text/javascript' src='https://www.ommegaonline.org/js//mediaelement-and-player.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//wp-mediaelement.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//third-party.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//isotope.pkgd.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//smoothPageScroll.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//js_composer_front.min.js'></script>
    <footer id="footer">
        <div class="qodef-footer-inner clearfix">
            <div class="qodef-footer-top-holder">
                <div class="qodef-footer-top  qodef-footer-top-full">
                    <div class="qodef-four-columns clearfix">
                        <div class="qodef-four-columns-inner">
                            <div style="min-height: 492px;" class="qodef-column">
                                <div class="qodef-column-inner">
                                    <div id="text-2" class="widget qodef-footer-column-1 widget_text">
                                        <div class="textwidget">
                                            <div class="vc_empty_space" style="height: 24px">
                                                <span class="vc_empty_space_inner">
                          </span>
                                            </div>
                                            <a href="https://www.ommegaonline.org/">
                                                <img src="https://www.ommegaonline.org/images/logo_ommega.png" alt="logo">
                                            </a>
                                            <div class="vc_empty_space" style="height: 24px">
                                                <span class="vc_empty_space_inner">
                          </span>
                                            </div>
                                            <ul>
                                            <li>PLAINSBORO</li>

<li>08536 NEW JERSEY, USA</li>

<li>Email: helpdesk@ommegaonline.org</li>

<li>Phone: +19177923454 </li>
</ul>
                                            <div class="vc_empty_space" style="height: 28px">
                                                <span class="vc_empty_space_inner">
                          </span>
                                            </div>
                                            <div class="custom-color-row-changer">
                                                <!--
                              <span class="qodef-icon-shortcode square" style="margin: 0px -5px 0px 0px;width: 36px;height: 36px;line-height: 36px;background-color: rgba(255,255,255,0.01);border-style: solid;border-color: #b4b4b4;border-width: 1px" data-hover-border-color="#b2dd4c" data-hover-background-color="#b2dd4c" data-hover-color="#ffffff" data-color="#ffffff">
                                               <a class="" href="https://www.facebook.com/" target="_blank">
                                  
                                  <i class="qodef-icon-font-awesome fa fa-facebook qodef-icon-element" style="color: #ffffff;font-size:18px"></i>
                                              </a>
                                      </span>
                              <span class="qodef-icon-shortcode square" style="margin: 0px -4px 0px 0px;width: 36px;height: 36px;line-height: 36px;background-color: rgba(255,255,255,0.01);border-style: solid;border-color: #b4b4b4;border-width: 1px" data-hover-border-color="#b2dd4c" data-hover-background-color="#b2dd4c" data-hover-color="#ffffff" data-color="#ffffff">
                                               <a class="" href="https://twitter.com/" target="_blank">
                                  
                                  <i class="qodef-icon-font-awesome fa fa-twitter qodef-icon-element" style="color: #ffffff;font-size:18px"></i>
                                              </a>
                                      </span>
                              <span class="qodef-icon-shortcode square" style="margin: 0px -5px 0px 0px;width: 36px;height: 36px;line-height: 36px;background-color: rgba(255,255,255,0.01);border-style: solid;border-color: #b4b4b4;border-width: 1px" data-hover-border-color="#b2dd4c" data-hover-background-color="#b2dd4c" data-hover-color="#ffffff" data-color="#ffffff">
                                               <a class="" href="https://vine.co/" target="_blank">
                                  
                                  <i class="qodef-icon-font-awesome fa fa-vine qodef-icon-element" style="color: #ffffff;font-size:18px"></i>
                                              </a>
                                      </span>
                              <span class="qodef-icon-shortcode square" style="margin: 0px -4px 0px 0px;width: 36px;height: 36px;line-height: 36px;background-color: rgba(255,255,255,0.01);border-style: solid;border-color: #b4b4b4;border-width: 1px" data-hover-border-color="#b2dd4c" data-hover-background-color="#b2dd4c" data-hover-color="#ffffff" data-color="#ffffff">
                                               <a class="" href="https://www.linkedin.com/" target="_blank">
                                  
                                  <i class="qodef-icon-font-awesome fa fa-linkedin qodef-icon-element" style="color: #ffffff;font-size:18px"></i>
                                              </a>
                                      </span>
                              <span class="qodef-icon-shortcode square" style="margin: 0px -4px 0px 0px; width: 36px; height: 36px; line-height: 36px; background-color: rgba(255, 255, 255, 0.01); border-style: solid; border-width: 1px;" data-hover-border-color="#b2dd4c" data-hover-background-color="#b2dd4c" data-hover-color="#ffffff" data-color="#ffffff">
                                               <a class="" href="https://instagram.com/" target="_blank">
                                  
                                  <i class="qodef-icon-font-awesome fa fa-instagram qodef-icon-element" style="color: rgb(255, 255, 255); font-size: 18px;"></i>
                                              </a>
                                      </span>
                          -->
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div style="min-height: 492px;" class="qodef-column">
                                <div class="qodef-column-inner">
                                    <div id="recent-posts-2" class="widget qodef-footer-column-2 widget_recent_entries">        <h4 class="qodef-footer-widget-title">Recent Articles</h4>     <ul>

                
                    <li>

                <a href="https://www.ommegaonline.org/article-details/Can-you-Have-Your-Cake-and-Eat-it-Too?-Outpatient-Cardiology-Precepting-Models/3834">Can you Have Your Cake and Eat it Too  Outpatient Cardiology Precepting Models</a>

                        </li>

                    
                    <li>

                <a href="https://www.ommegaonline.org/article-details/Food-Insecurity-among-Cancer-Patients:-A-Systematic-Review/3821">Food Insecurity among Cancer Patients  A Systematic Review</a>

                        </li>

                    
                    <li>

                <a href="https://www.ommegaonline.org/article-details/Social-Determinants-of-Health-and-Cancer-Survivorship/3805">Social Determinants of Health and Cancer Survivorship</a>

                        </li>

                    
                    <li>

                <a href="https://www.ommegaonline.org/article-details/Effects-of-some-varieties-of-Ananas-comosus-on-obesity-and-insulin-resistance-induced-by-oxidised-palm-oil-and-sucrose-diet-in-albino-rats/3802">Effects of some varieties of Ananas comosus on obesity and insulin resistance induced by oxidised palm oil and sucrose diet in albino rats</a>

                        </li>

                    
                    <li>

                <a href="https://www.ommegaonline.org/article-details/Preoperative-endoleak-type-and-intraoperative-blood-loss-in-aneurysmorrhaphy:-a-case-series-of-18-patients/3567">Preoperative endoleak type and intraoperative blood loss in aneurysmorrhaphy  a case series of 18 patients</a>

                        </li>

                    
                    <li>

                <a href="https://www.ommegaonline.org/article-details/Correlation-of-Socio-Economic-Determinants-to-Initial-Low-Risk-Substance-Use,-subsequent-Opioid-Use-Disorder-and-negative-prognostic-treatment-indicators.-/3547">Correlation of Socio-Economic Determinants to Initial Low Risk Substance Use  subsequent Opioid Use Disorder and negative prognostic treatment indicators  </a>

                        </li>

                    
                </ul>

        </div>  
                                </div>
                            </div>
                            <div style="min-height: 492px;" class="qodef-column">

        <div id="text-4" class="widget qodef-footer-column-4 widget_text">          


          <div class="textwidget"><div class="vc_empty_space" style="height: 12px"><span class="vc_empty_space_inner"></span></div>







<div class="qodef-custom-font-holder" style="font-family: Raleway;font-size: 22px;line-height: 22px;font-weight: 700;letter-spacing: 0px;text-align: left;color: #ffffff" data-font-size="22" data-line-height="22">

    Subscriber Here</div>



<div class="vc_empty_space" style="height: 7px"><span class="vc_empty_space_inner"></span></div>





Subscribe to our newsletter.



<div class="vc_empty_space" style="height: 20px"><span class="vc_empty_space_inner"></span></div>





<div role="form" class="wpcf7" id="wpcf7-f1334-o1" dir="ltr" lang="en-US">

<div class="screen-reader-response"></div>

<form action="/tech-business/#wpcf7-f1334-o1" method="post" class="wpcf7-form" novalidate="novalidate">

<div style="display: none;">

<input name="_wpcf7" value="1334" type="hidden">

<input name="_wpcf7_version" value="4.4.2" type="hidden">

<input name="_wpcf7_locale" value="en_US" type="hidden">

<input name="_wpcf7_unit_tag" value="wpcf7-f1334-o1" type="hidden">

<input name="_wpnonce" value="b1b2b2e095" type="hidden">

</div>

<form class="my-form soundest-subscribe-form" action="/subscribe" method="post" data-list="XXXXXXXXXXXXXXXXXXXXXXXX">

 

    <input class="soundest-subscribe-input" type="text" placeholder="NAME" style="margin:20px;" />

    <input class="soundest-subscribe-input" type="text" placeholder="EMAIL" style="margin:20px;"/>

 

    <input type="submit" value="Subscribe!" style="text-align: center;margin: 20px;">

 

</form>

<div class="wpcf7-response-output wpcf7-display-none"></div></form></div></div>

        </div>

        </div>

        <div style="min-height: 492px;" class="qodef-column">

            <div class="qodef-column-inner">

                <div id="text-3" class="widget qodef-footer-column-4 widget_text"><h4 class="qodef-footer-widget-title">Links</h4>           <div class="textwidget"></div>

                <div id="recent-posts-2" class="widget qodef-footer-column-2 widget_recent_entries">  <ul>

                

                  <li>

                <a href="https://www.ommegaonline.org/open-access-journals">Open Access Journals</a>

                        </li>

              

                        <li>

  <a href="https://www.ommegaonline.org/submit-manuscript">Submit Manuscript</a>

   
              

                        </li>

                        <li>

                <a href="https://www.ommegaonline.org/peer-review-system">Peer review system</a>

                        </li>

                        <li>

                <a href="https://www.ommegaonline.org/contact-us">Contact Us</a>

                        </li>

                        <li>

                <a href="https://www.ommegaonline.org/user-authenticate/register">Join Us</a>

                        </li> 

                </ul>

        </div> 

        </div>


                


          </div>

        </div>

    </div>

</div>  </div>

</div>



<div class="qodef-footer-bottom-holder">    
<div class="qodef-footer-bottom-holder-inner">    
   <div class="qodef-column-inner">  
    <div id="text-5" class="widget qodef-footer-text widget_text">      
        <div class="textwidget" style="float: left">
        <a rel="license" href="https://creativecommons.org/licenses/by/4.0/">
        <img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" />
        </a>
        <span>All Articles are Open access and distributed under the terms of <a rel="license" href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a></span>
        </div>
        <span style="float: right;">Website Copyright © Ommega Publishers   </span>
        </div>
        </div>    
        </div>
          </div>



    </div>

</footer>
    <!-- close div.qodef-wrapper-inner  -->
    <!-- close div.qodef-wrapper -->
    <script type="text/javascript" src="https://www.ommegaonline.org/js/underscore.min.js"></script>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <script type='text/javascript'>
        $(document).ready(function(){
            $(".qodef-mobile-menu-opener a").click(function(){
                $(".qodef-mobile-nav").toggle(200);
                return false;
            });
            $(".qodef-mobile-nav li .mobile_arrow").click(function(){
                //$(this).parent("li").parent("ul").children("li").children("ul").hide();
                if(!$(this).next("ul").is(':visible'))
                {
                       $(this).next("ul").show();
                }else{
                   $(this).next("ul").hide();
                }
                
                
                /*if(($(this).next("ul").css('display') === 'none')){
                  //$(this).next("ul").show();
                  console.log("show");
                }else{
                 //$(this).next("ul").hide();
                 console.log("hide");
                } */
               
            });
            //console.log("sdfsdf");
            var width = jQuery(window).width();
            if(width <= 1024){
                $(window).scroll(function(){
                    var scrollPos = $(document).scrollTop();
                    //console.log(scrollPos);
                    if(scrollPos >= 60){
                      //  $(".qodef-mobile-header-inner").hide();
                        //$(".hide-mobile img").height(100);
                    }else{
                       // $(".qodef-mobile-header-inner").show();
                       // $(".hide-mobile img").height(170);
                    }
                });
            }
        });
    </script>
    <script type='text/javascript'>
        var width = jQuery(window).width();
            if(width >= 1024){
        /* <![CDATA[ */
                var DavesWordPressLiveSearchConfig = {
                    "resultsDirection": "",
                    "showThumbs": "false",
                    "showExcerpt": "false",
                    "showMoreResultsLink": "true",
                    "minCharsToSearch": "0",
                    "xOffset": "0",
                    "yOffset": "0",
                    "blogURL": "http:\/\/",
                    "ajaxURL": "http:\/\/\/wp-admin\/admin-ajax.php",
                    "viewMoreText": "View more results",
                    "outdatedJQuery": "Dave's WordPress Live Search requires jQuery 1.2.6 or higher. WordPress ships with current jQuery versions. But if you are seeing this message, it's likely that another plugin is including an earlier version.",
                    "resultTemplate": "<ul id=\"dwls_search_results\" class=\"search_results dwls_search_results\">\n<input type=\"hidden\" name=\"query\" value=\"<%- resultsSearchTerm %>\" \/>\n<% _.each(searchResults, function(searchResult, index, list) { %>\n        <%\n        \/\/ Thumbnails\n        if(DavesWordPressLiveSearchConfig.showThumbs == \"true\" && searchResult.attachment_thumbnail) {\n                liClass = \"post_with_thumb\";\n        }\n        else {\n                liClass = \"\";\n        }\n        %>\n        <li class=\"daves-wordpress-live-search_result <%- liClass %> '\">\n        <% if(DavesWordPressLiveSearchConfig.showThumbs == \"true\" && searchResult.attachment_thumbnail) { %>\n                <img src=\"<%= searchResult.attachment_thumbnail %>\" class=\"post_thumb\" \/>\n        <% } %>\n\n        <a href=\"<%= searchResult.permalink %>\" class=\"daves-wordpress-live-search_title\"><%= searchResult.post_title %><\/a>\n\n        <% if(searchResult.post_price !== undefined) { %>\n                <p class=\"price\"><%- searchResult.post_price %><\/p>\n        <% } %>\n\n        <% if(DavesWordPressLiveSearchConfig.showExcerpt == \"true\" && searchResult.post_excerpt) { %>\n                <p class=\"excerpt clearfix\"><%= searchResult.post_excerpt %><\/p>\n        <% } %>\n\n        <% if(e.displayPostMeta) { %>\n                <p class=\"meta clearfix daves-wordpress-live-search_author\" id=\"daves-wordpress-live-search_author\">Posted by <%- searchResult.post_author_nicename %><\/p><p id=\"daves-wordpress-live-search_date\" class=\"meta clearfix daves-wordpress-live-search_date\"><%- searchResult.post_date %><\/p>\n        <% } %>\n        <div class=\"clearfix\"><\/div><\/li>\n<% }); %>\n\n<% if(searchResults[0].show_more !== undefined && searchResults[0].show_more && DavesWordPressLiveSearchConfig.showMoreResultsLink == \"true\") { %>\n        <div class=\"clearfix search_footer\"><a href=\"<%= DavesWordPressLiveSearchConfig.blogURL %>\/?s=<%-  resultsSearchTerm %>\"><%- DavesWordPressLiveSearchConfig.viewMoreText %><\/a><\/div>\n<% } %>\n\n<\/ul>"
                };
                 /* ]]> */
             }
    </script>
    
    <script type='text/javascript' src='https://www.ommegaonline.org/js//jquery.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//daves-wordpress-live-search.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//ecomp.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//spinners.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//jquery.form.min.js'></script>
    <script type='text/javascript'>
        /* <![CDATA[ */
        var _wpcf7 = {
            "loaderUrl": "http:\/\/\/wp-content\/plugins\/contact-form-7\/images\/ajax-loader.gif",
            "recaptchaEmpty": "Please verify that you are not a robot.",
            "sending": "Sending ..."
        };
        /* ]]> */
    </script>
    
    <script type='text/javascript' src='https://www.ommegaonline.org/js//scripts.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//jquery.blockUI.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//woocommerce.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//jquery.cookie.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//cart-fragments.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//core.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//widget.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//tabs.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//accordion.min.js'></script>
    
    <script type='text/javascript'>
        /* <![CDATA[ */
        var mejsL10n = {
            "language": "en-GB",
            "strings": {
                "Close": "Close",
                "Fullscreen": "Fullscreen",
                "Download File": "Download File",
                "Download Video": "Download Video",
                "Play\/Pause": "Play\/Pause",
                "Mute Toggle": "Mute Toggle",
                "None": "None",
                "Turn off Fullscreen": "Turn off Fullscreen",
                "Go Fullscreen": "Go Fullscreen",
                "Unmute": "Unmute",
                "Mute": "Mute",
                "Captions\/Subtitles": "Captions\/Subtitles"
            }
        };
        var _wpmejsSettings = {
            "pluginPath": "\/wp-includes\/js\/mediaelement\/"
        };
        /* ]]> */
    </script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//mediaelement-and-player.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//wp-mediaelement.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//third-party.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//isotope.pkgd.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//smoothPageScroll.js'></script>
    <script type='text/javascript'>
        /* <![CDATA[ */
        var qodefGlobalVars = {
            "vars": {
                "qodefAddForAdminBar": 0,
                "qodefElementAppearAmount": -150,
                "qodefFinishedMessage": "No more posts",
                "qodefMessage": "Loading new posts...",
                "qodefTopBarHeight": 0,
                "qodefStickyHeaderHeight": 60,
                "qodefStickyHeaderTransparencyHeight": 60,
                "qodefLogoAreaHeight": 0,
                "qodefMenuAreaHeight": 100,
                "qodefStickyHeight": 60,
                "qodefMobileHeaderHeight": 100
            }
        };
        var qodefPerPageVars = {
            "vars": {
                "qodefStickyScrollAmount": 0,
                "qodefHeaderTransparencyHeight": 0
            }
        };
        /* ]]> */
    </script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//modules.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//comment-reply.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//js_composer_front.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//toolbar.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//like.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//wp-embed.min.js'></script>
    <script type='text/javascript' src='https://www.ommegaonline.org/js//jquery.blockUI.min.js'></script>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 398px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2000">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 252px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 398px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2001">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 255px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 398px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2002">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 255px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 398px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2003">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 255px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 398px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2004">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 255px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 383px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2005">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 238px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 383px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2006">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 238px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 383px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2007">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 238px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 383px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2008">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 238px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 383px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2009">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 238px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 383px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2010">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 238px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 383px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2011">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 238px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    <div style="width: 0px; z-index: 9999; cursor: default; position: fixed; top: 0px; left: 1819px; height: 383px; opacity: 1; display: block;" class="nicescroll-rails nicescroll-rails-vr" id="ascrail2012">
        <div class="nicescroll-cursors" style="position: relative; top: 0px; float: right; width: 0px; height: 238px; background-color: transparent; border: 0px none; background-clip: padding-box; border-radius: 0px;">
        </div>
    </div>
    


    <script type="text/javascript" src="https://www.ommegaonline.org/js/clarigo.js"></script>
    <script type="text/javascript">
                    function save_download(downloads,aid) {
                        

                        var request = jQuery.ajax({
                            url: "https://www.ommegaonline.org/home/update_download_link/"+downloads+"/"+aid,
                            method: "GET",
                            dataType: "html"
                        });
                        request.done(function(msg) {
                           jQuery("#downloads").val(msg);
                        });
                        request.fail(function(jqXHR, textStatus) {
                            //alert( "Request failed: " + textStatus );
                            alert("Something went wrong, Please try refreshing the page.");
                        });
                    }
                    function save_like(likes,aid) {
                        

                        var request = jQuery.ajax({
                            url: "https://www.ommegaonline.org/home/updatelikes/"+likes+"/"+aid,
                            method: "GET",
                            dataType: "html"
                        });
                        request.done(function(msg) {
                           jQuery("#likeval").html(msg);
                        });
                        request.fail(function(jqXHR, textStatus) {
                            //alert( "Request failed: " + textStatus );
                            alert("Something went wrong, Please try refreshing the page.");
                        });
                    }
                    function myFunction(){
                         /* Get the text field */
                         var copyText = document.getElementById("myInput");

                              /* Select the text field */
                                 copyText.select();

                              /* Copy the text inside the text field */
                                 document.execCommand("Copy");
                    }
    </script>
    
    <script async id="slcLiveChat" src="https://widget.sonetel.com/SonetelWidget.min.js" data-account-id="206586226"></script>

</body>

</html>'''
    res = p.parse(html)
    print(res)
