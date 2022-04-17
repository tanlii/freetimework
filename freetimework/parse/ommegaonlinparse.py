import re
import difflib


class OmmegaOnlineParse:
    def __init__(self):
        pass

    def parse(self, res_content):
        product = dict()
        email_author = self.parse_email_author(res_content)
        product["author"] = email_author["author"]
        product["email"] = email_author["email"]
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
        pattern = '<h2>Corresponding Author</h2>(.*?)<a title="([^"]+)"'
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
    <meta name=keywords content="Sickle; Transition; Disparities">
    <meta name=description content="&nbsp;
Background: Young adults with sickle cell anemia are at high risk for increased hospitalization and death at the time of transition to adult care. This may be related to failure of the transition system to prepare young adults for the adult healthcare system. This qualitative study was designed to identify factors related to transition that may affect the health of adults with sickle cell anemia.Procedure: Ten patients currently treated in an adult hematology clinic participated in semi-structured qualitative interviews to describe their experience transitioning from pediatric to adult care and differences in adult and pediatric healthcare systems.Results: Participants were generally unprepared for the adult healthcare system. Negative issues experienced by participants included physician mistrust, difficulty with employers, keeping insurance, and stress in personal relationships. Positive issues experienced by participants included improved self efficiency with improved self care and autonomy.Conclusions: In the absence of a formalized transition program, adults with sickle cell anemia experience significant barriers to adult care. In addition to medical history review and identification of an adult provider, transition programs should incorporate strategies to navigate the adult medical system, insurance and relationships as well as encouraging self efficiency." >
       <meta name="citation_title" content="Exploring Adult Care Experiences and Barriers to Transition in Adult Patients with Sickle Cell Disease" />
     <meta name="citation_author" content="Jeffrey Lebensburger" />
     <meta name='citation_author' content='Halanych'/><meta name='citation_author' content=' J. H2'/><meta name='citation_author' content=' Howard'/><meta name='citation_author' content='T. H1'/><meta name='citation_author' content=' Hilliard'/><meta name='citation_author' content=' L. M1'/><meta name='citation_author' content=' Lebensburger'/><meta name='citation_author' content=' J. D1'/>     
     <meta name="citation_author" content="Ommega Internationals">

     <meta name="citation_publication_date" content="2015-09-06">
     <meta name="citation_journal_title" content="International Journal of Hematology and Therapy" />

     <meta name="citation_year" content="2015" />

     <meta name="citation_volume"  content="1" />

     <meta name="citation_issue" content="1" />

     

    <meta name="citation_firstpage" content="0" />
    <meta name="citation_lastpage" content="0" />
    <meta name="citation_DOI" content="10.15436/2381-1404.15.003" />
    
    <meta name="citation_publisher" content="Ommega Internationals" />

     <meta name="citation_pdf_url" content="https://www.ommegaonline.org/articles/publishimages/14946_Exploring-Adult-Care.pdf" />
     <meta name="citation_fulltext_html_url" content="https://www.ommegaonline.org/article-details/article/451  "/>
     <meta name="citation_xml_url" content="https://www.ommegaonline.org/home/articlexml/451"/>
     
     <meta name="citation_issn" content="2381-1404"/>
    <title>Exploring Adult Care Experiences and Barriers to Transition in Adult Patients with Sickle Cell Disease</title>

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
                                                    <div class="">Research                                                    </div>
                                                    <div class="">Publish Date : 2015-09-06                                                    </div>
                                                </div>
                                                <div class="qodef-post-info">
                                                    <div class="">International Journal of Hematology and Therapy                                                    </div>
                                                                                                        
                                                    <div class=""><a href='https://doi.org/10.15436/2381-1404.15.003' target='_blank'>
                                                         <input style='border:none; width:275px;' type='text' value='https://doi.org/10.15436/2381-1404.15.003' id='myInput'/></a>
                                                    </div>
                                                    <div class="">
                                                      
                                                        <button onclick="myFunction()">Copy doi</button>
                                                
                                                    </div>                                                 </div>
                                                   
                                                <div>
                                                    <h2>Exploring Adult Care Experiences and Barriers to Transition in Adult Patients with Sickle Cell Disease</h2>
                                                </div>
                                                <span class="qodef-quote-author" style="font-size: 16px;">Jeffrey Lebensburger  </span>
                                                <br>
                                               Halanych, J. H<sup>2</sup>, Howard,T. H<sup>1</sup>, Hilliard, L. M<sup>1</sup>, Lebensburger, J. D<sup>1</sup>                                    
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
                                                               <p><sup>1</sup> Pediatric Hematology Oncology, University of Alabama, Birmingham, Alabama,USA<br /><sup>2</sup>Department of Medicine, Division of Preventive Medicine, University of Alabama, Birmingham, Alabama, USA</p>                                                            </p>
                                                        </div>
                                                                                                                                                                        <div class="article_info_block1">
                                                            <h2>Corresponding Author</h2>
                                                            <p>
                                                              <p>Bemrich-Stolz, C. J., Department of Pediatrics, University of Alabama, Birmingham, USA. E-mail: <a title="cbstolz@peds.uab.edu" href="mailto:cbstolz@peds.uab.edu">cbstolz@peds.uab.edu</a></p>                                                            </p>
                                                        </div>
                                                                                                                                                                        <div class="article_info_block1">
                                                            <h2>Citation</h2>
                                                            <p>
                                                            
                                                                <p>Bemrich-Stolz, C. J., et al. Exploring Adult Care Experiences and Barriers to Transition in Adult Patients with Sickle Cell Disease. (2015). Int J Hematol and Therap 1(1): 1-5.</p>                                                            
                                                            </p>
                                                        </div>
                                                                                                                <div class="article_info_block1">
                                                            <h2>Copy rights</h2>
                                                            <p>
                                                                 <p>
                                                                <p>&copy; 2015 Bemrich-Stolz, C. J. This is an Open access article distributed under the terms of Creative Commons Attribution 4.0 International License.</p>                                                                </p>
                                                            </p>
                                                        </div>
                                                                                                                <div class="article_info_block1">
                                                            <h2>Keywords</h2>
                                                            <p>Sickle; Transition; Disparities                                                            </p>
                                                        </div>
                                                                                                            </div>
                                                    <div class="article_info_content">
                                                                                                                 <div class="article_info_block1" id="ABSTRACT">
                                                            <h5>Abstract</h5>
                                                            <p style="text-align: justify;">
                                                            <p>&nbsp;</p>
<p style="text-align: justify;"><span style="font-weight: bold;">Background: </span>Young adults with sickle cell anemia are at high risk for increased hospitalization and death at the time of transition to adult care. This may be related to failure of the transition system to prepare young adults for the adult healthcare system. This qualitative study was designed to identify factors related to transition that may affect the health of adults with sickle cell anemia.<br /><span style="font-weight: bold;">Procedure: </span>Ten patients currently treated in an adult hematology clinic participated in semi-structured qualitative interviews to describe their experience transitioning from pediatric to adult care and differences in adult and pediatric healthcare systems.<br /><span style="font-weight: bold;">Results: </span>Participants were generally unprepared for the adult healthcare system. Negative issues experienced by participants included physician mistrust, difficulty with employers, keeping insurance, and stress in personal relationships. Positive issues experienced by participants included improved self efficiency with improved self care and autonomy.<br /><span style="font-weight: bold;">Conclusions: </span>In the absence of a formalized transition program, adults with sickle cell anemia experience significant barriers to adult care. In addition to medical history review and identification of an adult provider, transition programs should incorporate strategies to navigate the adult medical system, insurance and relationships as well as encouraging self efficiency.</p>                                                            </p>
                                                        </div>
                                                                                                                
                                                       <div class="article_info_block1">
                                                                                                                   <h5 id="intro">Introduction</h5>
                                                                                                                        <div id="fulltext" name="fulltext">
                                                                <div id="intro">
                                                                <p style="text-align: justify;">&emsp;&emsp;Treatment of complications and preventive care have significantly improved life span for patients living with sickle cell disease<sup>[1]</sup>. Almost 95% of patients with sickle cell disease live past 18 years of age and require transition to an adult healthcare setting<sup>[1,2]</sup>. The age at which these patients move to the adult care system varies among centers but often occurs between 18 and 22 years old. A major concern is that this age range has been associated with significant increases in health care utilization and risk of death<sup>[2-6]</sup>. This data suggests that the time of transition is a very high risk time for patients with sickle cell disease and may be due in part to failures of appropriate transition to the adult care setting.</p>
<p style="text-align: justify;">&emsp;&emsp;Transition of care is described as the &ldquo;purposeful, planned movement of adolescents with chronic medical conditions from child-centered to adult-oriented health care&rdquo; with a goal of maximizing &ldquo;lifelong functioning and potential through the provision of high-quality, developmentally appropriate health care services that continue uninterrupted as the individual moves from adolescence to adulthood&rdquo;<sup>[7,8]</sup>. Transition is considered to be synonymous with transfer of care to an adult provider but it should instead be viewed as a process by which adolescents and young adults (AYA) are empowered with skills and knowledge to navigate adult health care systems and advocate for their health, families learn how to best support the patients in their transition and providers assist patients and families to set and meet transition goals in addition to facilitating transfer of care. Transition of care has become an increasingly recognized priority for all adolescents and young adults but particularly those with special health care needs.</p>
<p style="text-align: justify;">&emsp;&emsp;It is imperative to determine which fears are justified and what new concerns are identified after transition in order to design specific interventions to address them. Given the complex nature of these personal issues, a qualitative research design was selected to allow for theory generating, inductive research on this topic from the adult patient perspective. We conducted semi-structured interviews with adult patients with sickle cell disease that had experienced transition with the goal of identifyingadult perspective on transition of care.</p>
<div>&emsp;</div>
<h5 id="METHODS">Methods</h5>
<div>&emsp;</div>
<p style="text-align: justify;">&emsp;&emsp;The purpose of this qualitative research study was to identify barriers to transition to adult care by exploring the transition experiences from the perspective of adult patients with sickle cell disease. After Institutional Review Board approval, ten participants were recruited during a six month period through the University of Alabama at Birmingham Hematology Clinic during regularly scheduled clinic visits (Table 1). Patients greater than 18 years old with any sickle cell genotype were eligible to participate. Patients who presented to clinic for current illness were excluded. As the local Children&rsquo;s Hospital only recently initiated a formalized transition program for patients with sickle cell disease, none of the participants had participated in such a program during their transition to adult care. To ensure reliability, all interviews were performed by one investigator (C.B.) in clinic or by telephone and audio recorded. (supplemental document 1) Interviews lasted 30-40 minutes and transcribed by the same investigator (C.B). The interview transcript was designed to facilitate description of the participants&rsquo; experiences of pediatric, transitional and adult care utilizing both open and closed-ended questions. Demographic and disease complication information was also collected from each participant.</p>
<div>&emsp;</div>
<p style="font-size: 12px; text-align: center;"><strong>Table 1: </strong>Characteristics of Study Sample</p>
<table border="1" width="50%" cellspacing="0.1" align="center">
<tbody>
<tr>
<th style="font-weight: bolder; text-align: center;">Characteristics</th>
<th style="font-weight: bolder; text-align: center;">N = 10</th>
</tr>
<tr>
<th style="font-weight: bolder; text-align: center;" colspan="2">Gender</th>
</tr>
<tr>
<td>Male</td>
<td style="text-align: center;">3</td>
</tr>
<tr>
<td>Female</td>
<td style="text-align: center;">7</td>
</tr>
<tr>
<td>Age</td>
<td style="text-align: center;">24-55</td>
</tr>
<tr>
<th style="text-align: center;" colspan="2">Education completed</th>
</tr>
<tr>
<td>Some high school</td>
<td style="text-align: center;">1</td>
</tr>
<tr>
<td>High School Graduate</td>
<td style="text-align: center;">2</td>
</tr>
<tr>
<td>Some college</td>
<td style="text-align: center;">6</td>
</tr>
<tr>
<td>College Graduate</td>
<td style="text-align: center;">1</td>
</tr>
<tr>
<th style="font-weight: bolder; text-align: center;" colspan="2">Insurance</th>
</tr>
<tr>
<td>Medicaid</td>
<td style="text-align: center;">8</td>
</tr>
<tr>
<td>Private Insurance</td>
<td style="text-align: center;">2</td>
</tr>
<tr>
<th style="font-weight: bolder; text-align: center;" colspan="2">Disability</th>
</tr>
<tr>
<td>Yes</td>
<td style="text-align: center;">9</td>
</tr>
<tr>
<td>No</td>
<td style="text-align: center;">1 (has applied)</td>
</tr>
<tr>
<th style="font-weight: bolder; text-align: center;" colspan="2">Current therapy</th>
</tr>
<tr>
<td>Hydroxyurea</td>
<td style="text-align: center;">9</td>
</tr>
<tr>
<td>Chronic transfusion</td>
<td style="text-align: center;">1</td>
</tr>
</tbody>
</table>
<div>&emsp;</div>
<p style="text-align: justify;"><strong>Data Analysis</strong><br />&emsp;&emsp;The researcher&rsquo;s position on this topic prior to initiating research was that transition was a difficult process for patients and which was exacerbated by a lack of transition program. First cycle coding methods used In-Vivo coding to capture exact quotes (codes) from patients. Two researchers independently coded the transcript and only codes with 100% inter-coder agreement were included in the final code book. Coding and identification of preliminary categories continued until data saturation was achieved, the key stopping component in qualitative research. Specifically, during analysis of the transcripts from the final interviews, no new codes or categories were generated, providing the required validation for the final sample size. Recoding and recategorizing was performed two additional times using a qualitative research analysis program (NVivo 10, QSR International) until final categories and themes were agreed upon by the researchers. Internal validity was established using triangulation and peer review. The integrity of the qualitative researcher was established by reflexivity, establishing any biases/assumptions prior to analysis. Reliability of the data was attained through consistency of one interviewer conducting the same semi-structured interview. External validity was established through rich thick descriptions obtained through In-Vivo coding.</p>
<div>&emsp;</div>
<h5 id="RESULTS">Results</h5>
<div>&emsp;</div>
<p style="text-align: justify;">&emsp;&emsp;Coding of data identified 13 categories related to transition that revealed three distinct themes, 1) Living with SCD as an Adult, 2) Emotions Experienced during Transition, and 3) Self Efficiency. &ldquo;Living with SCD as an Adult&rdquo; focused on experiences that affect adults living with sickle cell disease, including five categories related to physician mistrust, access to care, insurance, employment, and relationships. (Figure 1) &ldquo;Emotions Experienced during Transition&rdquo; identified the emotions experienced during the transition which included categories of concerns for either new care setting or new doctor and patient readiness. &ldquo;Self-Efficiency&rdquo; included categories of improved self-maintenance and relationship with parents. (Figure 2).</p>
<div>&emsp;</div>
<p><a href="../../admin/journalassistance/picturegallery/481.jpg" target="_blank" rel="noopener" name="figure1"> <img src="../../admin/journalassistance/picturegallery/481.jpg" alt="https://www.ommegaonline.org/admin/journalassistance/picturegallery/481.jpg" width="200px;" height="120px" /></a></p>
<p><strong>Figure 1: </strong></p>
<p><a id="h8" class="position-top-50" name="h8"></a></p>
<div>&emsp;</div>
<p><a href="../../admin/journalassistance/picturegallery/482.jpg" target="_blank" rel="noopener" name="figure2"> <img src="../../admin/journalassistance/picturegallery/482.jpg" alt="https://www.ommegaonline.org/admin/journalassistance/picturegallery/482.jpg" width="200px;" height="120px" /></a></p>
<p><strong>Figure 2: </strong></p>
<p><a id="h8" class="position-top-50" name="h8"></a></p>
<div>&emsp;</div>
<p style="text-align: justify;">&emsp;&emsp;The largest category in this theme was &ldquo;physician mistrust&rdquo;, including subcategories of difficulties with pain management and general knowledge about sickle cell disease. While participants expressed positive relationships with their adult hematologist, codes related to relationships with emergency room doctors or primary care physicians were negative. Several participants expressed their belief that ER physicians treated them as &ldquo;drug seekers&rdquo; rather than as a patient. &ldquo;The worst thing (about adult care) is people don&rsquo;t treat you with respect and kindness. They treat you like a crack head.&rdquo; Another participant stated &ldquo;Treat me like you would want someone to treat you. Don&rsquo;t group me in a category of other SCD patients.&rdquo; Additionally, participants felt that ER doctors were hesitant to prescribe a sufficient quantity of pain medications to treat their pain crises at home which created a cycle in which they would have to return to the ER for more pain medications. The experience with their primary care provider identified concerns that these physicians did not have enough medical knowledge about sickle cell disease. &ldquo;Dr. X is my primary doctor but he doesn&rsquo;t really know anything about sickle cell disease so I have to tell him what to do..&rdquo; Another participant stated, &ldquo;he (Primary Medical Doctor) was really mean to me. He was a little bit arrogant. It was like he was blaming me for the sore on my leg (leg ulcers).&rdquo; The mistrust with emergency room and adult primary care doctors may lead to a serious health risk as patients, in an attempt to avoid the emergency room, describe different techniques they would use to manage their sickle cell complications at home.</p>
<p style="text-align: justify;">&emsp;&emsp;The second category was &ldquo;access to care&rdquo; including subcategories of identifying adult providers, and transportation issues. While finding their first hematologist was easy, which may be biased as the patients were interviewed in a hematology clinic on the same medical campus as their pediatric hematologists, difficulties arose when their physician left or the patient moved to a new city. For the subcategory of transportation, one participant needed to have &ldquo;money wired&rdquo; to her so that she could pay for transportation to the hospital.</p>
<p style="text-align: justify;">&emsp;&emsp;The third category of this theme was &ldquo;insurance&rdquo; including Subcategories of loss of insurance, physicians acceptance of insurance, and limitations with refills. Despite the fact that all participants in the study were insured, a number had difficulty navigating their insurance. Several participants expressed difficulty obtaining clinic appointments with doctors based on their insurance. Participants had exaggerated negative experiences with physician access when they lost insurance based on job termination as private insurance provided improved access to care. Finally, limitations in medication refill based on their insurance coverage lead to several participants not having enough pain medication.</p>
<p style="text-align: justify;">&emsp;&emsp;The fourth category identified was employment, including subcategories of working with SCD and loss of employment. Interestingly, while jobs were not intended as a focus of the interview, participants frequently discussed difficulties that they encountered while working. They reported challenges with employers understanding sickle cell disease and complications of pain. Specifically, pain episodes were often managed at home, so participants would have to explain their frequent absences that were not accompanied by a doctor&rsquo;s excuse. Many participants had difficulty explaining frequent absences for pain crisis to their employers. &ldquo;You can&rsquo;t go in there telling them that you have these crises and I have to be out&rdquo;. Participants felt that they had difficulty remaining employed based on frequent pain crises. &ldquo;It&rsquo;s very difficult to hold employment because of the stress level.&rdquo;</p>
<p style="text-align: justify;">&emsp;&emsp;The fifth category identified was relationships including subcategories of relationships at work and at home. Frequent absences for pain crises placed a strain on relationships with co-workers. One participant described a situation in which fellow employees would &ldquo;tease&rdquo; her about frequently missing work, asking her &ldquo;where have you been on vacation&rdquo;. At home, one participant acknowledged that SCD complications placed a strain on her marriage, &ldquo;(he did not) understand the cycle of pain and what it does.&rdquo; Aside from their mother, many participants felt less support from other family members. They explained how family members would minimize their disease, such as &ldquo;If I say &lsquo;oh my god my leg hurts so bad&rsquo; than he&rsquo;d say &lsquo;well mine hurts too&rsquo;&hellip; I just say OK dad, but it&rsquo;s a different type of hurt.&rdquo; Emotions Experienced During Transition</p>
<p style="text-align: justify;">&emsp;&emsp;The second theme &ldquo;Emotions Experienced during Transition&rdquo; encompasses codes related to the patients beliefs about the transition process. Participants described their pediatric medical experiences with language including, &ldquo;it was wonderful, doctors were supportive,&rdquo; &ldquo;they try to help you more,&rdquo; and &ldquo;they showed you respect.&rdquo; When transition was first discussed, a number of participants were surprised and felt abandoned. &ldquo;Why are you trying to send me over there? I&rsquo;ve known you since I was a little girl to now and how could you&rdquo;. I was worried about &ldquo;who was going to be my doctor and was she going to be nice from the time (I transition). How to get used to being over here instead of Children&rsquo;s the different scenery&rdquo;. The age of transition varied among participants from 18-22 years and without a history of a structured transition at this institution, patients were often transferred to adult doctors within weeks to months of being told about transition.</p>
<p style="text-align: justify;">&emsp;&emsp;The final theme identified was &ldquo;Self efficiency&rdquo; as several patients experienced an improved ability to care for themselves and understand their disease after transition.(figure 2) Categories in this theme include &ldquo;improved self care&rdquo;, &ldquo;relationship with parents&rdquo;, &ldquo;reflections on transition&rdquo; The first category &ldquo;improved self care&rdquo; included knowing how to handle sickle cell complications and understanding their body. &ldquo;I pretty much know how to handle it now. When I felt these excruciating pains coming as a kid, I didn&rsquo;t know what to do.&rdquo; The second category involved the change in their relationship with parents who now would act as an advisor or assist with practical issues. Several participants believed that their ability to manage their disease was related to their independence from their parents. One participant stated that it was easier to care for her since &ldquo;I make my own decisions now.&rdquo; While the overall feeling of participants was one of apprehension about leaving pediatrics, this independence in medical decision making allowed them to reflect on the benefit of leaving the pediatric setting. A participant who stayed until she was 21 stated, &ldquo;He should have let me go at the age of 19. Children&rsquo;s hospital is only for children.&rdquo; Another participant wondered, &ldquo;I was an adult going to a children&rsquo;s doctor. I felt out of place.&rdquo;</p>
<div>&emsp;</div>
<h5 id="DISCUSSION">Discussion</h5>
<div>&emsp;</div>
<p style="text-align: justify;">&emsp;&emsp;A significant emphasis is being placed on enhancing transition of care for all diseases. The US Department of Health and Human Services has included a need to &ldquo;increase the proportion of youth with special health care needs whose health care provider has discussed transition planning from pediatric to adult health care&rdquo; as one of their Healthy People 2020 goals and the American Academy of Pediatrics, American Academy of Family Physicians and American College of Physicians-American Society of Internal Medicine have published a consensus statement and an algorithm to assist physicians in understanding the need for transition and implementing transition programs in their practice<sup>[8-11]</sup>. Recently published quality of care guidelines for sickle cell anemia recommend that a transition plan should be developed for all patients and that adolescents should be notified of the need to transition, but specifics regarding structure of such programs remain lacking<sup>[10]</sup>. Despite this enthusiasm for transition programs, there is a dearth of literature examining the outcomes associated with various programs making development of evidence-based programs for patient transition difficult<sup>[12]</sup>. Though the specific details of programs may vary, transition programs have the potential to require significant amounts of time for both providers and families. It is important to focus programs on topics that are most likely to impact health in adulthood. A number of studies have examined concerns of older pediatric patients, their caregivers and providers as they neared the time for transition<sup>[13-19]</sup>. Unfortunately, scant data limited to small samples exists to ascertain if the concerns noted prior to transition were actual barriers to completing transition or receiving care in adulthood<sup>[20]</sup>. This manuscript provide a patient centered perspective that is vital to improving the process of transition of care.</p>
<p style="text-align: justify;">&emsp;&emsp;Adult patients with sickle cell provide insights about transition to adult care that should be incorporated into pediatric sickle cell transition programs. Prior concerns reported by pediatric patients remain relevant in the adult setting. (Table 2) Additionally, several new issues related to transition were identified and should be incorporated into transition programs, such as developing relationships with loved ones and employees/employers who do not understand the complications of sickle cell anemia, teaching patients strategies to handle difficult situations in the emergency room or with primary care providers, identifying new sickle cell providers if they move or their provider leaves, and how to navigate obtaining insurance with job termination.</p>
<div>&emsp;</div>
<p style="font-size: 12px; text-align: center;"><strong>Table 2: </strong>Concerns expressed by patients prior to transition to adult care</p>
<table border="1" width="50%" cellspacing="0.1" align="center">
<tbody>
<tr>
<td>Leaving comfortable pediatric setting<sup>[10, 11, 14, 15]</sup></td>
</tr>
<tr>
<td>Going to a doctor unfamiliar with treating sickle cell disease<sup>[11]</sup></td>
</tr>
<tr>
<td>Will my parents allow patients to become independent<sup>[11,15]</sup></td>
</tr>
<tr>
<td>How will I pay for medical treatment<sup>[10]</sup></td>
</tr>
<tr>
<td>Will I be treated as an adult<sup>[10]</sup></td>
</tr>
<tr>
<td>Will adult providers understand how sickle cell disease affects me as an individual<sup>[10,14]</sup></td>
</tr>
<tr>
<td>Will adult staff believe me when I am in pain[10]</td>
</tr>
</tbody>
</table>
<p style="text-align: justify;">&emsp;&emsp;A major emphasis of transition programs is to educate patients about their disease and medical history. This education is necessary as several of the adult experiences confirm that adult primary care providers or emergency room physicians may not be comfortable or knowledgeable about treating patients with sickle cell anemia. It is important for patients to be educated on how to best navigate situations in which they perceive that an adult provider does not believe their reports of pain or recognize the unique way that sickle cell disease affects them as individuals. Recommendations for how to educate patients about this concern are difficult as the researchers could not identify whether this issue represents true physician disbelief, patient misunderstanding of physician&rsquo;s feelings or poor communication on the part of the provider. Some component of this discrepancy in disease management may be related to the lack of understanding of the differences in culture between pediatric and adult medicine. It has been suggested that addressing the differences in culture between the subspecialties my help adolescents navigate the transition<sup>[21]</sup>. If provider attitudes also play a role in patient beliefs regarding their care, it would be important to continue to study those attitudes, outcomes associated with different attitudes towards patients with sickle cell disease in pain and, if significant, methods for modifying attitudes<sup>[21,22]</sup>.</p>
<p style="text-align: justify;">&emsp;&emsp;The positive experiences of the adult participants highlight some benefits of transition that should be conveyed to pediatric patients during the time of transition. Despite the fact that a few participants reported worse overall health during adulthood, most participants believed that they were better able to understand and control their disease complications as an adult. Parents allowed the young adult patients to experience medical independence. Finally, after transition, patients realize the need to leave pediatric facilities as natural and appropriate for their stage of maturation. Incorporating this knowledge may be comforting to patients that approach transition with apprehension.</p>
<p style="text-align: justify;">&emsp;&emsp;Unfortunately, several barriers to transition and negative experiences in adult care are not easily addressed through transition programs. Though identification of an adult provider is important and incorporated in all transition programs, it is not clear what the most appropriate adult care provider for these patients would be. In a national survey of sickle cell transition programs, despite 97% of programs reporting that they had identified a provider to accept their patients, only 60% of centers routinely transfer care to a hematologist specializing in sickle cell anemia<sup>[23]</sup>. A 2008 survey of general internal medicine and pediatric providers found that only one third of IM physicians would be comfortable serving as the primary care provider for patients with sickle cell disease<sup>[24]</sup>. Further research is needed to determine if internal medicine physicians are able to provide care equivalent to that provided by hematologists and how to best engage them to take on these patients. With decreasing reimbursements for coordination of care and preventive care in general in addition to a small hematology workforce willing to accept patients with sickle cell, without changes, pediatric providers are likely to find a smaller population of potential providers in the future<sup>[24]</sup>.</p>
<p style="text-align: justify;">&emsp;&emsp;Limitations to this study include recall bias as all participants had completed transition from pediatric care more than 2 years prior to participation in interviews, however most of the concerns that participants recalled around the time of transition were consistent with published literature. A second limitation is that the study population only included patients who had, regardless of transition plan, found an adult hematologist to provide regular care. This would suggest that patients in this population differ from those who have been unable to find adult care for their sickle cell disease at a tertiary care setting in yet unknown ways. All participants in this study were insured and the majority is disabled. Though this is an important population to study, it may not be representative of all patients with sickle cell disease. While the sample size was small, this should not be viewed as a limitation as data saturation was achieved. Finally, inherent to qualitative research, the goal of this method of research is to develop a deeper understanding of how individuals make sense of their own reality so that theories can be inductively generated. Qualitative research is not intended to generalize findings to a larger population other institutions, but this limitation should not detract from the importance of this research design.</p>
<p style="text-align: justify;">&emsp;&emsp;Transition planning should occur years prior to transferring a patient to an adult center. Education should focus both on disease education and strategies to navigate employment, insurance, personal relationships, and adult physicians. Future research should be performed to understand the experiences and barriers of adult patients with sickle cell disease who may not have a regular source of medical care outside of the inpatient and emergency room setting. In addition, qualitative research can identify the perspectives of adult primary care providers and emergency room physicians in relation to the barriers they perceive about transition and further explore issues associated with mistrust.</p>
<div>&emsp;</div>
<p style="text-align: justify;"><strong>Conflict of interest</strong><br />&emsp;&emsp;The authors have no relevant conflicts of interest, personal or financial, to disclose.</p>
<div>&emsp;</div>
<p style="text-align: justify;"><strong>Acknowledgment</strong><br />&emsp;&emsp;We would like to thank the patients living with sickle cell disease who participated in this research. Portions of this manuscript were presented at the American Society of Hematology Annual Meeting. J.L. receives salary support from the NIH 1K23HL127100-01.</p>
<div>&emsp;</div>
<h5 id="REFERENCES">References</h5>
<div>&emsp;</div>
<div class="ol">
<ol style="text-align: justify;">
<li>1. <a href="https://www.ncbi.nlm.nih.gov/pubmed/23450875" target="_blank" rel="noopener">Lanzkron, S., Carroll, C. P., Haywood, C. Jr., et al. Mortality rates and age at death from sickle cell disease. (2013) Public Health Rep 128(2): 110- 116.</a></li>
<li>2. <a href="https://www.ncbi.nlm.nih.gov/pubmed/20194891" target="_blank" rel="noopener">Quinn, C. T., Rogers, Z. R., McCavit, T. L., et al. Improved survival of children and adolescents with sickle cell disease. (2010) Blood 115(17): 3447- 3452.</a></li>
<li>3. <a href="https://www.ncbi.nlm.nih.gov/pubmed/20371788" target="_blank" rel="noopener">Brousseau, D. C., Owens, P. L., Mosso, A.L., et al. Acute care utilization and rehospitalizations for sickle cell disease. (2010) JAMA 303(13): 1288- 1294.</a></li>
<li>4. <a href="https://www.ncbi.nlm.nih.gov/pubmed/16315251" target="_blank" rel="noopener">Shankar, S. M., Arbogast, P. G., Mitchel, E., et al. Medical care utilization and mortality in sickle cell disease: a population-based study. (2005) Am J Hematol 80(4): 262- 270.</a></li>
<li>5. <a href="https://www.ncbi.nlm.nih.gov/pubmed/21796763" target="_blank" rel="noopener">Dickerson, A. K., Klima, J., Rhodes, M. M., et al. Young adults with SCD in US children's hospitals: are they different from adolescents? (2012) Pediatr Blood Cancer 58(5): 741- 745.</a></li>
<li>6. <a href="https://www.ncbi.nlm.nih.gov/pubmed/23335275" target="_blank" rel="noopener">Blinder, M.A., Vekeman, F., Sasane, M., et al. Age-related treatment patterns in sickle cell disease patients and the associated sickle cell complications and healthcare costs. (2013) Pediatr Blood Cancer 60(5): 828- 835.</a></li>
<li>7. <a href="https://www.ncbi.nlm.nih.gov/pubmed/12456948" target="_blank" rel="noopener">Blum, R.W. Introduction. Improving transition for adolescents with special health care needs from pediatric to adult-centered health care. (2002) Pediatrics 110(6 Pt 2): 1301- 1303.</a></li>
<li>8. <a href="https://www.ncbi.nlm.nih.gov/pubmed/12456949" target="_blank" rel="noopener">A consensus statement on health care transitions for young adults with special health care needs. (2002). Pediatrics 110(6 Pt 2): 1304- 1306. </a></li>
<li>9. <a href="https://www.ncbi.nlm.nih.gov/pubmed/21708806" target="_blank" rel="noopener">Supporting the health care transition from adolescence to adulthood in the medical home. (2011) Pediatrics. 128(1): 182- 200.</a></li>
<li>10. <a href="https://www.ncbi.nlm.nih.gov/pubmed/21844055" target="_blank" rel="noopener">Wang, C. J., Kavanagh, P. L., Little, A. A., et al. Quality-of-care indicators for children with sickle cell disease. (2011) Pediatrics 128(3): 484- 493.</a></li>
<li>11. <a href="https://www.ncsl.org/research/health/healthy-people-2020-a-road-map-for-health.aspx" target="_blank" rel="noopener">Van Kalsbeek, M., Saunders, J. B. Healthy People 2020: a road map for health. (2011) NCSL 19(27): 1- 2. </a></li>
<li>12. <a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3460672/" target="_blank" rel="noopener">Lebensburger, J. D., Bemrich-Stolz, C. J., Howard, T. H. Barriers in transition from pediatrics to adult medicine in sickle cell anemia. (2012) J Blood Med 3: 105- 112.</a></li>
<li>13. <a href="https://www.ncbi.nlm.nih.gov/pubmed/7857954" target="_blank" rel="noopener">Telfair, J., Myers, J., Drezner, S. Transfer as a component of the transition of adolescents with sickle cell disease to adult care: adolescent, adult, and parent perspectives. (1994) J Adolesc Health 15(7): 558- 565.</a></li>
<li>14. <a href="https://www.ncbi.nlm.nih.gov/pubmed/12024394" target="_blank" rel="noopener">Hauser, E. S., Dorn, L. Transitioning adolescents with sickle cell disease to adult-centered care. (1999) Pediatr Nurs 25(5): 479- 488.</a></li>
<li>15. <a href="https://www.ncbi.nlm.nih.gov/pubmed/19103405" target="_blank" rel="noopener">Bryant, R., Walsh, T. Transition of the chronically ill youth with hemoglobinopathy to adult health care: an integrative review of the literature. (2009) J Pediatr Health Care 23(1): 37- 48.</a></li>
<li>16. <a href="https://www.ncbi.nlm.nih.gov/pubmed/21602723" target="_blank" rel="noopener">Smith, G. M., Lewis, V. R., Whitworth, E., et al. Growing up with sickle cell disease: a pilot study of a transition program for adolescents with sickle cell disease. (2011) J Pediatr Hematol Oncol 33(5): 379- 382.</a></li>
<li>17. <a href="https://www.ncbi.nlm.nih.gov/pubmed/15148858" target="_blank" rel="noopener">Telfair, J., Ehiri, J. E., Loosier, P. S., et al. Transition to adult care for adolescents with sickle cell disease: results of a national survey. (2004) Int J Adolesc Med Health 16(1): 47- 64.</a></li>
<li>18. <a href="https://www.ncbi.nlm.nih.gov/pubmed/18796047" target="_blank" rel="noopener">Tuchman, L. K., Slap, G. B., Britto, M. T. Transition to adult care: experiences and expectations of adolescents with a chronic illness. (2008) Child Care Health Dev 34(5): 557 563.</a></li>
<li>19. <a href="https://www.ncbi.nlm.nih.gov/pubmed/24807007" target="_blank" rel="noopener">Williams, C. P., Smith, C. H., Osborn, K., et al. Patient-centered approach to designing sickle cell transition education. (2015) J Pediatr Hematol Oncol 37(1): 43- 47.</a></li>
<li>20. <a href="https://www.ncbi.nlm.nih.gov/pubmed/25188623" target="_blank" rel="noopener">Mennito, S., Hletko, P., Ebeling, M., et al. Adolescents with sickle cell disease in a rural community: are they ready to transition to adulthood? (2014) South Med J 107(9): 578- 582.</a></li>
<li>21. <a href="https://www.ncbi.nlm.nih.gov/pubmed/19233587" target="_blank" rel="noopener">Ratanawongsa, N., Haywood, C. Jr., Bediako, S. M., et al. Health care provider attitudes toward patients with acute vaso-occlusive crisis due to sickle cell disease: development of a scale. (2009) Patient Educ Couns 76(2): 272- 278.</a></li>
<li>22. <a href="https://www.ncbi.nlm.nih.gov/pubmed/21181560" target="_blank" rel="noopener">Haywood, C. Jr., Lanzkron, S., Hughes, M. T., et al. A video-intervention to improve clinician attitudes toward patients with sickle cell disease: the results of a randomized experiment. (2011) J Gen Intern Med 26(5): 518- 523.</a></li>
<li>23. <a href="https://www.ncbi.nlm.nih.gov/pubmed/21594889" target="_blank" rel="noopener">Sobota, A., Neufeld, E. J., Sprinz, P., et al. Transition from pediatric to adult care for sickle cell disease: results of a survey of pediatric providers. (2011) Am J Hematol 86(6): 512- 515.</a></li>
<li>24. <a href="https://www.ncbi.nlm.nih.gov/pubmed/19171604" target="_blank" rel="noopener">Peter, N. G., Forke, C. M., Ginsburg, K. R., et al. Transition from pediatric to adult care: internists' perspectives. (2009) Pediatrics 123(2): 417- 423.</a></li>
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
                                        67                                      </span>
                                                                        <input type="hidden" name="" id="pagelike" value="1"> </td>
                                                                    
                                                                    <td>
                                                                       <a target="_blank" href="https://www.ommegaonline.org/download.php?download_file=articles/publishimages/14946_Exploring-Adult-Care.pdf" onclick="save_download(67,451)"> <img class="pdfimg" align="center" src="https://www.ommegaonline.org/images/pdf.png" height="50" width="50"></a>
                                                                    </td>
                                                                    <td>
                                                                       <a target="_blank" href="https://www.ommegaonline.org/download.php?download_file=admin/journalassistance/publishimages/1839_IJHT-15-RA-003.bib" onclick="save_download(67,451)"> <img class="pdfimg" src="https://www.ommegaonline.org/images/text.png" height="50" width="45"></a>
                                                                    </td>
                                                                <td>
                                                                        <a target="_blank" href="https://www.ommegaonline.org/home/articlexml/451" onclick="save_download(67,451)"><img class="pdfimg" src="https://www.ommegaonline.org/images/xml.png" height="50" width="49"></a>
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
                                                                        <a target="_blank" href="https://www.ommegaonline.org/download.php?download_file=articles/publishimages/14946_Exploring-Adult-Care.pdf" onclick="save_download(67,451)">PDF</a>
                                                                    </td>
                                                                    <td  style="text-align: center;padding:5px;font-size: 12px">
                                                                        <a target="_blank" href="https://www.ommegaonline.org/download.php?download_file=admin/journalassistance/publishimages/1839_IJHT-15-RA-003.bib" onclick="save_download(67,451)">CITATION</a>
                                                                    </td>
                                                                    <td  style="text-align: center;padding:5px;font-size: 12px">
                                                                        <a target="_blank" href="https://www.ommegaonline.org/home/articlexml/451" onclick="save_download(67,451)">XML</a>
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
                                                            <a style="color:#b1b1b1;" onclick="save_like('43','451')">
                                                                
                                                            <span>   <span id="likeval">                    
                                    43                                  </span></span>  </a>Likes
                                  </p>
                                                     
                                                        <p>
                                                            <span>5193                                </span>Views
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
