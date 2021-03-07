import requests
from bs4 import BeautifulSoup


def which_journal(url):
    # given the url, what is the journal that it is from, e.g. 'pnas'
    if 'www' in url:
        publisher = url.split('.')[1]
    else:
        publisher = url.split('.')[0].split('//')[1]

    return publisher

class PaperInfo(object):
    # Abstract class for all of the
    def __init__(self, url):
        self.url = url
        self.html = self.get_html()
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.pdf_link = None

    def get_html(self):
        # use request module to get HTML from the Webpage at self.url
        r = requests.get(self.url)
        html = r.text
        return html

    def get_title(self):
        # given self.html, get the title
        pass

    def get_doi(self):
        # given self.html, get the doi
        pass

    def get_abstract(self):
        # given self.html, get the abstract
        pass

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pass

    def is_open_access(self):
        # given full_doc_link, can you get the full PDF from it?
        if self.pdf_link is None:
            self.pdf_link = self.get_full_doc_link()
        r = requests.get(self.pdf_link)
        return r.ok


class PaperInfoNature(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('h1', class_='c-article-title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        spans = self.soup.find_all('span', class_='c-bibliographic-information__value')
        for span in spans:
            if 'doi' in span.text:
                doi = span.text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find(id='Abs1-content', class_='c-article-section__content').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pdf_link = self.url + '.pdf'
        return pdf_link


class PaperInfoJEB(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('div', class_='highwire-cite-title', id='page-title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('span', class_='highwire-cite-metadata-doi highwire-cite-metadata').text
        doi = doi[5:].strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('p', id='p-1').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        for a in self.soup.find_all('a', href=True):
            link = a['href']
            if 'pdf' in link:
                if 'jeb.biologists.org' in link:
                    pdf_link = link

        return pdf_link

class PaperInfoSpringer(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('h1', class_='c-article-title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('span', class_='bibliographic-information__value u-overflow-wrap').text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('p', class_='Para').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pdf_link = self.url.replace('chapter','content/pdf')+'.pdf'
        return pdf_link


class PaperInfoRSP(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('h1', class_='citation__title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('a', class_='epub-section__doi__text').text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('div', class_='abstractSection abstractInFull').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        pdf_link = self.url.replace('full', 'pdf')
        return pdf_link


class PaperInfoPNAS(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find('h1', class_='highwire-cite-title').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('span', class_='highwire-cite-metadata-doi highwire-cite-metadata').text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('div', class_='section abstract').find('p').text.strip()
        return abstract

    def get_full_doc_link(self):
        # given self.html, get the full_doc_link
        if self.url[-4:] == 'full':
            pdf_link = self.url + '.pdf'
        else:
            pdf_link = self.url + '.full.pdf'
        return pdf_link


class PaperInfoPubMed(PaperInfo):
    def get_title(self):
        title = self.soup.find(id="full-view-heading").find("h1").text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi = self.soup.find('span', class_='identifier doi').find('a').text.strip()
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = self.soup.find('div', class_='abstract-content selected').find('p').text.strip()
        return abstract

    def get_similar_articles(self):
        articles = self.soup.find('ul', class_='articles-list', id="similar-articles-list").findAll('span', class_="docsum-journal-citation full-journal-citation")

        dois = []
        for article in articles:
            doi = article.text
            doi = doi.split('doi: ')[1].split(' Epub')[0]
            dois.append(doi)
        return dois
    # def get_full_doc_link(self):
    #     # given self.html, get the full_doc_link
    #     pass

class PaperInfoScienceDirect(PaperInfo):
    def get_title(self):
        # given self.html, get the title
        title = self.soup.find(class_='title-text').text.strip()
        return title

    def get_doi(self):
        # given self.html, get the doi
        doi_tag = self.soup.find(id='doi-link')
        doi = doi_tag.find('a').get('href')
        return doi

    def get_abstract(self):
        # given self.html, get the abstract
        abstract = ''
        abstract_tag = self.soup.find(class_='abstract author')
        if abstract_tag:
            abstract_div = abstract_tag.find('div')
            abstract_paras = abstract_div.find_all('p')
            for i in abstract_paras:
                abstract += i.text.strip()
        return abstract

    def get_full_doc_link(self):
        pdf_link = ''
        get_access = self.soup.find(class_='pdf-download-label-short u-hide-from-lg')
        if get_access.text.strip() != 'Get Access':
            pdf_link = self.url
            if 'abs/' in pdf_link:
                pdf_link = pdf_link.replace('abs/', '')
            if '?via%3Dihub' in pdf_link:
                pdf_link = pdf_link.split('?via%3Dihub', 1)[0]
            pdf_link = pdf_link + '/pdfft'
        return pdf_link

paper_info_classes = {
    'pnas': PaperInfoPNAS,
    'pubmed': PaperInfoPubMed,
    'nature': PaperInfoNature,
    'jeb': PaperInfoJEB,
    'springer': PaperInfoSpringer,
    'rsp': PaperInfoRSP,
    'sciencedirect': PaperInfoScienceDirect
}


def get_paper_info(url):
    #Determine the journal site name, and create corresponding object name
    journal = which_journal(url)
    paper_info_class = paper_info_classes[journal]
    paper_info_instance = paper_info_class(url)

    #Retrieiving journal properties
    title = paper_info_instance.get_title()
    doi = paper_info_instance.get_doi()
    abstract = paper_info_instance.get_abstract()
    full_doc_link = paper_info_instance.get_full_doc_link()
    # is_open_access = paper_info_instance.is_open_access()
    is_open_access = True

    return title, doi, abstract, full_doc_link, is_open_access
